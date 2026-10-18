"""Deterministic, high-performance mock LLM evaluation service conforming to SLA bounds."""

import asyncio
import re
import uuid
from typing import AsyncGenerator, List, Tuple

from ..models.grammar import (
    GrammarErrorSpan,
    ErrorCategory,
    ErrorSeverity,
    SemanticValidation,
    StyleAlternative,
    PreferredStyle,
)
from ..models.session import SessionResponse, PromptType
from ..models.metrics import SessionMetrics, LatencyBreakdown
from ..models.evaluation import (
    EvaluationRequest,
    EvaluationResult,
    SSESessionStartPayload,
    SSETokenPayload,
    SSEDonePayload,
)
from ..utils.latency import LatencyTimer
from ..utils.sse import format_sse_event
from .metrics_service import calculate_session_metrics

# Common linguistic mistake patterns (regex, category, severity, message, suggestion)
COMMON_PATTERNS = [
    # Agreement errors
    (r"\b(he|she|it)\s+have\b", ErrorCategory.AGREEMENT, ErrorSeverity.ERROR, "Subject-verb agreement error: third-person singular takes 'has'.", "has"),
    (r"\b(i)\s+is\b", ErrorCategory.AGREEMENT, ErrorSeverity.ERROR, "Subject-verb agreement: first person 'I' takes 'am'.", "am"),
    (r"\b(they|we|you)\s+is\b", ErrorCategory.AGREEMENT, ErrorSeverity.ERROR, "Plural subject takes 'are'.", "are"),
    (r"\b(they|we|you)\s+was\b", ErrorCategory.AGREEMENT, ErrorSeverity.ERROR, "Plural subject in past tense takes 'were'.", "were"),
    (r"\b(he|she|it)\s+don't\b", ErrorCategory.AGREEMENT, ErrorSeverity.ERROR, "Third-person singular takes 'doesn't'.", "doesn't"),

    # Tense & modal errors
    (r"\b(did|didn't)\s+(went|saw|came|took)\b", ErrorCategory.TENSE, ErrorSeverity.ERROR, "Auxiliary 'did' must be followed by base form of verb.", "base form (go/see/come/take)"),
    (r"\b(must|can|should|will|would)\s+to\s+([a-z]+)\b", ErrorCategory.SYNTAX, ErrorSeverity.ERROR, "Modal verbs are followed directly by the bare infinitive without 'to'.", "bare verb"),

    # Common typos / spelling
    (r"\bteh\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Typographical spelling mistake.", "the"),
    (r"\brecieve\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error: 'i' before 'e' except after 'c'.", "receive"),
    (r"\bseperate\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error.", "separate"),
    (r"\bdefinately\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error.", "definitely"),
    (r"\bbecuase\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Typographical spelling error.", "because"),
    (r"\bthier\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error.", "their"),
    (r"\balot\b", ErrorCategory.SPELLING, ErrorSeverity.WARNING, "'a lot' is written as two separate words.", "a lot"),
    (r"\buntill\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error.", "until"),
    (r"\btruely\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error.", "truly"),
    (r"\bwierd\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error.", "weird"),
    (r"\bfavourit\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error.", "favorite / favourite"),
    (r"\brestaraunt\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error.", "restaurant"),
    (r"\btommorow\b", ErrorCategory.SPELLING, ErrorSeverity.ERROR, "Spelling error.", "tomorrow"),

    # Redundancy
    (r"\b([a-zA-Z]+)\s+\1\b", ErrorCategory.GRAMMAR, ErrorSeverity.WARNING, "Accidental duplicate word.", "single word"),
]

# Concept mappings for prompt semantic checks (prompt snippet -> expected English concept keywords)
CONCEPT_DICTIONARY = {
    "кофе": ["coffee", "cup", "espresso", "latte", "drink"],
    "утром": ["morning", "early", "dawn", "sunrise", "am"],
    "работой": ["work", "job", "office", "working"],
    "солнце": ["sun", "sunlight", "sunny", "shines", "bright"],
    "ветер": ["wind", "breeze", "windy", "blows"],
    "листьями": ["leaves", "foliage", "branches", "trees"],
    "кафе": ["cafe", "coffeehouse", "restaurant", "bistro"],
    "улицы": ["street", "corner", "avenue", "city"],
    "технологии": ["technology", "technologies", "tech", "ai", "artificial"],
    "интеллекта": ["intelligence", "smart", "cognitive"],
    "задач": ["tasks", "problems", "challenges", "goals"],
    "ливень": ["rain", "downpour", "shower", "storm"],
    "горы": ["mountain", "mountains", "peak", "climb", "hike"],
    "туристы": ["tourists", "hikers", "travelers"],
    "питание": ["nutrition", "diet", "food", "eating"],
    "настроение": ["mood", "spirit", "feeling"],
    "экономическая": ["economic", "economy", "financial"],
    "решений": ["decisions", "solutions", "policies"],
    "исследованиях": ["research", "studies", "science"],
}


# Stylistic transformations tailored to content domains across all 5 registers
STYLE_DOMAIN_PATTERNS = [
    {
        "domain": "mountain_hiking",
        "keywords": ["ливень", "горы", "вершин", "турист", "mountain", "hike", "climb", "summit", "rain", "downpour", "trail", "ascent"],
        "styles": {
            PreferredStyle.FORMAL: (
                "Notwithstanding the sudden downpour, the expedition persevered with their ascent toward the ancient summit.",
                "Employs elevated preposition ('notwithstanding'), formal vocabulary ('expedition', 'persevered', 'ascent'), and sophisticated syntactic cadence.",
            ),
            PreferredStyle.CONCISE: (
                "Despite heavy rain, the hikers continued their mountain ascent.",
                "Eliminates superfluous modifiers, maximizing informational density and directness.",
            ),
            PreferredStyle.ACADEMIC: (
                "Field observations indicate that the expedition maintained upward progression toward the summit despite adverse meteorological conditions.",
                "Adopts scholarly diction ('field observations', 'upward progression', 'meteorological conditions') and analytical phrasing.",
            ),
            PreferredStyle.BUSINESS: (
                "Navigating adverse conditions to reach the summit exemplifies operational resilience and commitment to milestone execution.",
                "Frames the endeavor around risk mitigation, team resilience, and strategic goal achievement.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "Even with that sudden downpour, the hikers just kept pushing all the way to the top of the mountain.",
                "Uses natural conversational phrasing ('even with', 'kept pushing', 'all the way') ideal for casual conversation.",
            ),
        },
    },
    {
        "domain": "nature_sun",
        "keywords": ["солнце", "ветер", "листь", "дерев", "sun", "sunlight", "sunny", "breeze", "wind", "leaves", "trees", "garden", "flower", "blooming"],
        "styles": {
            PreferredStyle.FORMAL: (
                "Radiant sunlight illuminates the landscape while a gentle breeze rustles the verdant foliage.",
                "Employs descriptive elevated vocabulary ('radiant', 'illuminates', 'verdant foliage') and balanced cadence.",
            ),
            PreferredStyle.CONCISE: (
                "Bright sunlight and a light breeze rustle the green leaves.",
                "Direct, compact description prioritizing economy of words.",
            ),
            PreferredStyle.ACADEMIC: (
                "Solar irradiance combined with convective air currents produces observable motion throughout the arboreal foliage.",
                "Uses precise physical and biological terminology suited to formal scientific analysis.",
            ),
            PreferredStyle.BUSINESS: (
                "Leveraging optimal environmental conditions fosters a revitalizing atmosphere that enhances workplace well-being.",
                "Focuses on environmental impact on performance and wellness.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "The sun is shining bright and there's a nice cool breeze blowing through the trees.",
                "Relaxed, sensory language typical of informal speech.",
            ),
        },
    },
    {
        "domain": "cafe_street",
        "keywords": ["кафе", "улиц", "встрет", "cafe", "coffeehouse", "bistro", "street", "corner", "meet", "central"],
        "styles": {
            PreferredStyle.FORMAL: (
                "We agreed to convene at an inviting cafe situated on the intersection of the primary thoroughfare.",
                "Uses formal vocabulary ('convene', 'situated', 'primary thoroughfare') and elevated register.",
            ),
            PreferredStyle.CONCISE: (
                "We decided to meet at a cozy downtown corner cafe.",
                "Concise and direct, condensing spatial details without loss of clarity.",
            ),
            PreferredStyle.ACADEMIC: (
                "Participants coordinated a rendezvous at a centrally located hospitality venue to facilitate discussion.",
                "Analytical phrasing emphasizing intentionality and spatial positioning.",
            ),
            PreferredStyle.BUSINESS: (
                "We scheduled our collaborative meeting at a central cafe venue to review project priorities.",
                "Executive framing highlighting collaboration and objective-oriented discussion.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "We decided to meet up at this super cozy cafe right on the corner downtown.",
                "Warm, conversational phrasing with natural colloquial enthusiasm.",
            ),
        },
    },
    {
        "domain": "ai_tech",
        "keywords": ["технологи", "интеллект", "задач", "tech", "technology", "artificial", "intelligence", "ai", "complex", "algorithm", "solution", "conference"],
        "styles": {
            PreferredStyle.FORMAL: (
                "Artificial intelligence technologies are rapidly transforming established methodologies for addressing complex challenges.",
                "Employs formal diction ('established methodologies', 'addressing complex challenges') and refined syntax.",
            ),
            PreferredStyle.CONCISE: (
                "AI technologies rapidly transform complex problem solving.",
                "Maximizes brevity by eliminating filler words and retaining key operational concepts.",
            ),
            PreferredStyle.ACADEMIC: (
                "Advances in artificial intelligence paradigms demonstrate profound systemic effects upon algorithmic problem-solving frameworks.",
                "Scholarly framing emphasizing theoretical impact and structural paradigm shifts.",
            ),
            PreferredStyle.BUSINESS: (
                "Deploying AI-driven capabilities accelerates operational velocity and scales innovative problem resolution.",
                "Outcome-oriented corporate language highlighting scalability, velocity, and business impact.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "AI tech is totally changing how we tackle tough problems every day.",
                "Approachable, conversational tech jargon suitable for informal discussions.",
            ),
        },
    },
    {
        "domain": "health_fitness",
        "keywords": ["физическ", "активност", "питан", "иммунитет", "настроен", "exercise", "health", "workout", "nutrition", "diet", "immune", "mood"],
        "styles": {
            PreferredStyle.FORMAL: (
                "Consistent physical exertion and wholesome nutrition bolster immunological defenses and elevate emotional equilibrium.",
                "Features elevated formal vocabulary ('physical exertion', 'bolster', 'emotional equilibrium').",
            ),
            PreferredStyle.CONCISE: (
                "Regular exercise and healthy eating boost immunity and improve mood.",
                "Clean, direct expression of the core cause-and-effect relationship.",
            ),
            PreferredStyle.ACADEMIC: (
                "Empirical literature confirms that systematic exercise coupled with balanced nutritional intake significantly enhances immunological and psychological outcomes.",
                "Evidence-based academic diction using domain-specific health sciences terminology.",
            ),
            PreferredStyle.BUSINESS: (
                "Investing in sustained wellness and balanced lifestyle habits drives personal vitality and high-performance output.",
                "ROI-driven wellness framing emphasizing productivity and sustainable energy.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "Working out regularly and eating right really helps your immune system and keeps your spirits up.",
                "Friendly, encouraging colloquial tone with natural everyday expressions.",
            ),
        },
    },
    {
        "domain": "economy_governance",
        "keywords": ["экономическ", "стабильност", "неопределенност", "решен", "выверенн", "economy", "economic", "stability", "uncertainty", "decision", "strategic"],
        "styles": {
            PreferredStyle.FORMAL: (
                "Preserving economic stability amid global volatility necessitates deliberate and strategically calibrated determinations.",
                "High-level diplomatic/economic register with sophisticated lexical choices.",
            ),
            PreferredStyle.CONCISE: (
                "Economic stability amid global uncertainty demands prudent strategic decisions.",
                "Highly distilled policy statement omitting rhetorical redundancies.",
            ),
            PreferredStyle.ACADEMIC: (
                "Macroeconomic equilibrium under conditions of systemic uncertainty requires rigorous econometric assessment and policy calibration.",
                "Analytical academic language grounded in economic methodology and formal theory.",
            ),
            PreferredStyle.BUSINESS: (
                "Maintaining financial resilience through market volatility requires decisive leadership and disciplined risk management.",
                "C-suite strategic framing centered on risk governance, resilience, and value preservation.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "Keeping the economy steady when things are unpredictable takes smart, well-thought-out calls.",
                "Relatable, pragmatic phrasing explaining complex economic realities simply.",
            ),
        },
    },
    {
        "domain": "science_systems",
        "keywords": ["междисциплинарн", "исследован", "биологическ", "систем", "закономерност", "science", "research", "interdisciplinary", "biological", "systems"],
        "styles": {
            PreferredStyle.FORMAL: (
                "An interdisciplinary orientation in scientific inquiry elucidates fundamental principles governing complex biological architectures.",
                "Elevated academic syntax with formal classical roots ('elucidates', 'interdisciplinary orientation').",
            ),
            PreferredStyle.CONCISE: (
                "Interdisciplinary research reveals fundamental principles of complex biological systems.",
                "Direct and active syntactic construction focused on core discovery.",
            ),
            PreferredStyle.ACADEMIC: (
                "Cross-disciplinary methodological synthesis facilitates the identification of emergent governing mechanisms in biological networks.",
                "Rigorous peer-reviewed journal style utilizing specialized theoretical terminology.",
            ),
            PreferredStyle.BUSINESS: (
                "Fostering cross-functional research synergies unlocks breakthrough insights and accelerates scientific discovery.",
                "Organizational language highlighting cross-functional leverage and intellectual property creation.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "Combining different scientific fields really helps us figure out how living systems work.",
                "Accessible explanation that translates complex scientific methodology into conversational English.",
            ),
        },
    },
    {
        "domain": "coffee_morning",
        "keywords": ["кофе", "coffee", "espresso", "latte", "cappuccino"],
        "styles": {
            PreferredStyle.FORMAL: (
                "It is my preference to partake in a warm beverage in the early morning prior to commencing professional obligations.",
                "Employs elevated vocabulary ('partake', 'professional obligations') and formal syntactic structure.",
            ),
            PreferredStyle.CONCISE: (
                "I drink hot coffee early each morning before work.",
                "Eliminates superfluous modifiers, maximizing informational density and directness.",
            ),
            PreferredStyle.ACADEMIC: (
                "Empirical routines indicate that morning beverage consumption precedes the commencement of daily occupational activities.",
                "Adopts scholarly diction and passive analytical phrasing suitable for academic prose.",
            ),
            PreferredStyle.BUSINESS: (
                "Prioritizing a morning coffee routine optimizes alertness and readiness for daily strategic deliverables.",
                "Tailored for executive communication, emphasizing productivity, deliverables, and focus.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "I love grabbing a hot cup of coffee first thing in the morning before work.",
                "Uses natural, engaging phrasing ('grabbing a hot cup', 'first thing') ideal for everyday dialogue.",
            ),
        },
    },
    {
        "domain": "dining_restaurant",
        "keywords": ["restaurant", "meal", "order", "waiter", "dish", "menu", "favorite meal"],
        "styles": {
            PreferredStyle.FORMAL: (
                "May I inquire regarding the chef's foremost recommendation for tonight's dining selection?",
                "Polite and polished formal dining phrasing.",
            ),
            PreferredStyle.CONCISE: (
                "I would like to order dinner and hear your top recommendation.",
                "Direct ordering request with concise inquiry.",
            ),
            PreferredStyle.ACADEMIC: (
                "Patrons frequently solicit culinary recommendations to optimize dining satisfaction within hospitality environments.",
                "Objective sociological description of hospitality interactions.",
            ),
            PreferredStyle.BUSINESS: (
                "Selecting premier dining venues provides an ideal setting for client engagement and stakeholder hospitality.",
                "Framed around client relationships and professional dining.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "Hey, what would you recommend getting tonight? I'm ready for something really good!",
                "Casual and enthusiastic restaurant dialogue.",
            ),
        },
    },
    {
        "domain": "airport_travel",
        "keywords": ["airport", "flight", "delayed", "airline", "boarding", "terminal"],
        "styles": {
            PreferredStyle.FORMAL: (
                "Due to the unanticipated flight delay, I must adjust my itinerary and coordinate subsequent arrangements.",
                "Formal travel communication with diplomatic tone.",
            ),
            PreferredStyle.CONCISE: (
                "My flight is delayed three hours; I am rescheduling my plans.",
                "Brevity-focused travel update.",
            ),
            PreferredStyle.ACADEMIC: (
                "Operational disruptions in commercial aviation necessitate immediate adaptive scheduling behaviors among travelers.",
                "Analytical perspective on transportation logistics.",
            ),
            PreferredStyle.BUSINESS: (
                "Mitigating transit delays requires proactive schedule realignment to safeguard downstream business commitments.",
                "Risk-management framing focused on business deliverables.",
            ),
            PreferredStyle.CONVERSATIONAL: (
                "My flight got delayed for three hours, so I guess I'll just grab a snack and hang out at the gate.",
                "Relaxed casual reaction to travel inconvenience.",
            ),
        },
    },
]


def transform_generic_text(user_text: str, preferred_style: PreferredStyle) -> Tuple[str, str]:
    """Dynamically transform any generic sentence according to target stylistic register."""
    text = user_text.strip().rstrip(".!?")
    if not text:
        text = "The team made significant progress on the assigned project"

    clean = text[0].upper() + text[1:] if len(text) > 1 else text.upper()

    if preferred_style == PreferredStyle.FORMAL:
        formal_substitutions = [
            (r"\bi want to\b", "it is my objective to"),
            (r"\bi like to\b", "it is my distinct preference to"),
            (r"\bi think that\b", "in my deliberate assessment,"),
            (r"\bstart\b", "commence"),
            (r"\bstarted\b", "commenced"),
            (r"\bshow\b", "demonstrate"),
            (r"\bshows\b", "demonstrates"),
            (r"\bhelp\b", "facilitate"),
            (r"\bhelps\b", "facilitates"),
            (r"\buse\b", "utilize"),
            (r"\bused\b", "utilized"),
            (r"\bget\b", "obtain"),
            (r"\bmake\b", "establish"),
            (r"\bmakes\b", "establishes"),
            (r"\bbig\b", "substantial"),
            (r"\bgood\b", "advantageous"),
            (r"\bbad\b", "adverse"),
            (r"\ba lot of\b", "a considerable quantity of"),
        ]
        res = clean
        for pat, repl in formal_substitutions:
            res = re.sub(pat, repl, res, flags=re.IGNORECASE)
        alt = f"It should be noted that {res[0].lower() + res[1:]}."
        explanation = "Applies elevated formal diction and sophisticated subordinating syntax."
        return alt, explanation

    elif preferred_style == PreferredStyle.CONCISE:
        concise_substitutions = [
            (r"\bvery\s+", ""),
            (r"\breally\s+", ""),
            (r"\bactually\s+", ""),
            (r"\bbasically\s+", ""),
            (r"\bin order to\b", "to"),
            (r"\bdue to the fact that\b", "because"),
            (r"\bat this point in time\b", "now"),
        ]
        res = clean
        for pat, repl in concise_substitutions:
            res = re.sub(pat, repl, res, flags=re.IGNORECASE)
        res = re.sub(r"\s+", " ", res).strip()
        alt = f"{res}."
        explanation = "Eliminates superfluous qualifiers and wordiness to maximize informational density."
        return alt, explanation

    elif preferred_style == PreferredStyle.ACADEMIC:
        alt = f"Empirical evaluation suggests that {clean[0].lower() + clean[1:]}."
        explanation = "Adopts passive analytical framing and evidence-based academic rhetoric."
        return alt, explanation

    elif preferred_style == PreferredStyle.BUSINESS:
        alt = f"Focusing on this initiative ensures that {clean[0].lower() + clean[1:]}, driving measurable operational alignment."
        explanation = "Frames the statement around strategic outcomes, organizational focus, and measurable value."
        return alt, explanation

    else:  # CONVERSATIONAL
        alt = f"Honestly, {clean[0].lower() + clean[1:]}!"
        explanation = "Uses natural conversational phrasing and relatable spoken cadence."
        return alt, explanation


class MockLLMService:
    """Fast, deterministic linguistic analysis service conforming to latency SLAs."""

    def analyze_grammar(self, text: str, check_case_and_period: bool = False) -> List[GrammarErrorSpan]:
        """Detect real grammatical, syntactic, and spelling errors with exact span offsets."""
        errors: List[GrammarErrorSpan] = []
        if not text:
            return errors

        # 1. Capitalization check at sentence start (only when check_case_and_period is enabled)
        if check_case_and_period:
            first_char_match = re.search(r"[a-zA-Z]", text)
            if first_char_match and first_char_match.group(0).islower():
                idx = first_char_match.start()
                char = first_char_match.group(0)
                errors.append(
                    GrammarErrorSpan(
                        start=idx,
                        end=idx + 1,
                        original_text=char,
                        message="Sentences should start with a capitalized letter.",
                        suggestion=char.upper(),
                        category=ErrorCategory.PUNCTUATION,
                        severity=ErrorSeverity.INFO,
                    )
                )

        # 2. Pattern-based grammar, agreement, and spelling rules
        for pattern, category, severity, msg, suggestion in COMMON_PATTERNS:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                matched_str = match.group(0)
                # Formulate contextual suggestion
                if suggestion == "single word":
                    sug = match.group(1)
                elif suggestion == "has" and matched_str.lower().startswith("he"):
                    sug = "he has"
                elif suggestion == "has" and matched_str.lower().startswith("she"):
                    sug = "she has"
                elif suggestion == "has" and matched_str.lower().startswith("it"):
                    sug = "it has"
                elif suggestion == "doesn't":
                    subj = matched_str.split()[0]
                    sug = f"{subj} doesn't"
                elif suggestion == "are":
                    subj = matched_str.split()[0]
                    sug = f"{subj} are"
                elif suggestion == "were":
                    subj = matched_str.split()[0]
                    sug = f"{subj} were"
                elif suggestion == "am":
                    sug = "I am"
                else:
                    sug = suggestion

                errors.append(
                    GrammarErrorSpan(
                        start=match.start(),
                        end=match.end(),
                        original_text=matched_str,
                        message=msg,
                        suggestion=sug,
                        category=category,
                        severity=severity,
                    )
                )

        # 3. Missing terminal punctuation (only when check_case_and_period is enabled)
        if check_case_and_period:
            stripped = text.strip()
            if stripped and stripped[-1] not in (".", "!", "?"):
                # Mark the end of the text
                end_pos = len(text)
                last_char_pos = max(0, end_pos - 1)
                errors.append(
                    GrammarErrorSpan(
                        start=last_char_pos,
                        end=end_pos,
                        original_text=text[last_char_pos:end_pos],
                        message="Sentence should end with terminal punctuation (period, exclamation point, or question mark).",
                        suggestion=text[last_char_pos:end_pos] + ".",
                        category=ErrorCategory.PUNCTUATION,
                        severity=ErrorSeverity.INFO,
                    )
                )

        # Deduplicate and sort spans by start offset
        errors.sort(key=lambda e: (e.start, e.end))
        return errors


    def validate_semantics(
        self,
        user_text: str,
        session: SessionResponse,
    ) -> SemanticValidation:
        """Validate conceptual coverage and semantic fidelity of submission against prompt."""
        if not user_text.strip():
            return SemanticValidation(
                is_valid=False,
                score=0.0,
                explanation="No text was submitted for evaluation.",
                missing_concepts=["Complete sentence submission"],
            )

        lower_user = user_text.lower()
        prompt_content = session.prompt.content.lower()

        # Find expected concepts in prompt
        expected_concepts: List[Tuple[str, List[str]]] = []
        for ru_key, en_synonyms in CONCEPT_DICTIONARY.items():
            if ru_key in prompt_content:
                expected_concepts.append((ru_key, en_synonyms))

        if not expected_concepts:
            # Fallback for English situation prompts or unlisted words
            words = [w for w in re.findall(r"\b[a-zA-Z]{4,}\b", prompt_content) if w not in ("describe", "explain", "your", "with")]
            for w in words[:4]:
                expected_concepts.append((w, [w]))

        matched_count = 0
        missing: List[str] = []

        for concept_name, synonyms in expected_concepts:
            if any(syn in lower_user for syn in synonyms):
                matched_count += 1
            else:
                missing.append(synonyms[0])

        total_concepts = len(expected_concepts)
        if total_concepts == 0:
            score = 90.0 if len(user_text.split()) >= 3 else 50.0
        else:
            base_ratio = matched_count / total_concepts
            score = round(base_ratio * 100.0, 1)

        # Boost score slightly if loose phrasing is allowed and sentence has decent structure
        if session.allow_loose_phrasing and score > 40.0:
            score = min(100.0, round(score + 10.0, 1))

        is_valid = score >= 60.0
        if is_valid:
            if missing:
                explanation = f"Good translation capturing {matched_count}/{total_concepts} core concepts with minor omissions."
            else:
                explanation = "Excellent semantic accuracy: all core concepts and contextual nuances were preserved."
        else:
            explanation = f"Incomplete semantic coverage. Key missing elements: {', '.join(missing)}."

        return SemanticValidation(
            is_valid=is_valid,
            score=score,
            explanation=explanation,
            missing_concepts=missing,
        )

    def generate_style_alternative(
        self,
        user_text: str,
        preferred_style: PreferredStyle,
        session: SessionResponse,
    ) -> StyleAlternative:
        """Generate strictly ONE style alternative matching the user's requested register."""
        combined_context = f"{session.prompt.content} {user_text}".lower()

        # Check for domain-specific thematic patterns
        for item in STYLE_DOMAIN_PATTERNS:
            if any(kw in combined_context for kw in item["keywords"]):
                style_dict = item["styles"]
                alt_text, explanation = style_dict.get(
                    preferred_style,
                    style_dict.get(PreferredStyle.CONVERSATIONAL, ("...", "..."))
                )
                return StyleAlternative(
                    style=preferred_style,
                    text=alt_text,
                    explanation=explanation,
                )

        # Fallback to general dynamic syntactic transformation
        alt_text, explanation = transform_generic_text(user_text, preferred_style)
        return StyleAlternative(
            style=preferred_style,
            text=alt_text,
            explanation=explanation,
        )

    async def stream_evaluation(
        self,
        request: EvaluationRequest,
        session: SessionResponse,
    ) -> AsyncGenerator[str, None]:
        """Stream progressive evaluation events via SSE conforming strictly to latency SLA."""
        timer = LatencyTimer()

        # 1. Yield session_start immediately (<10ms)
        start_payload = SSESessionStartPayload(
            session_id=session.session_id,
            status="active",
        )
        yield format_sse_event("session_start", start_payload)

        # Execute genuine linguistic analysis
        check_case_and_period = (
            request.check_case_and_period
            if request.check_case_and_period is not None
            else getattr(session, "check_case_and_period", False)
        )
        errors = self.analyze_grammar(request.user_text, check_case_and_period=check_case_and_period)
        semantics = self.validate_semantics(request.user_text, session)

        style = self.generate_style_alternative(
            request.user_text,
            session.preferred_style,
            session,
        )

        # Realistic TTFT delay (e.g. 80ms) - well within TTFT < 800ms SLA
        await asyncio.sleep(0.08)
        timer.mark_ttft()

        # 2. Stream feedback preview token chunks derived from the dynamic style alternative
        style_words = style.text.split()
        token_samples = [(" " if i > 0 else "") + w for i, w in enumerate(style_words[:8])]
        if not token_samples:
            token_samples = ["Analyzing", " submission", " complete."]

        for idx, token_chunk in enumerate(token_samples):
            token_payload = SSETokenPayload(
                text=token_chunk,
                token=token_chunk,
                index=idx,
            )
            yield format_sse_event("token", token_payload)
            await asyncio.sleep(0.015)  # 15ms pacing between tokens

        timer.mark_inference_done()

        # 3. Yield grammar errors
        yield format_sse_event("grammar_errors", errors)

        # 4. Yield semantic check
        yield format_sse_event("semantic_check", semantics)

        # 5. Yield style alternative (strictly ONE alternative)
        yield format_sse_event("style_alternative", style)

        # 6. Session metrics
        metrics = calculate_session_metrics(
            user_text=request.user_text,
            time_spent_ms=request.time_spent_ms,
            target_word_count=session.prompt.target_word_count,
            margin_buffer=session.prompt.margin_buffer,
            timer_seconds=session.timer_seconds,
            character_count=request.character_count,
            keystroke_count=request.keystroke_count,
            grammar_errors=errors,
            semantic_score=semantics.score,
        )
        yield format_sse_event("metrics", metrics)

        # 7. Done event with latency SLA report
        latency = timer.mark_pipeline_done()
        done_payload = SSEDonePayload(
            evaluation_id=str(uuid.uuid4()),
            result_id=str(uuid.uuid4()),
            latency=latency,
        )
        yield format_sse_event("done", done_payload)

    def evaluate_sync(
        self,
        request: EvaluationRequest,
        session: SessionResponse,
        user_id: str = None,
    ) -> EvaluationResult:
        """Compute evaluation synchronously in a single consolidated payload."""
        import datetime
        timer = LatencyTimer()
        timer.mark_ttft()

        check_case_and_period = (
            request.check_case_and_period
            if request.check_case_and_period is not None
            else getattr(session, "check_case_and_period", False)
        )
        errors = self.analyze_grammar(request.user_text, check_case_and_period=check_case_and_period)
        semantics = self.validate_semantics(request.user_text, session)

        style = self.generate_style_alternative(
            request.user_text,
            session.preferred_style,
            session,
        )
        metrics = calculate_session_metrics(
            user_text=request.user_text,
            time_spent_ms=request.time_spent_ms,
            target_word_count=session.prompt.target_word_count,
            margin_buffer=session.prompt.margin_buffer,
            timer_seconds=session.timer_seconds,
            character_count=request.character_count,
            keystroke_count=request.keystroke_count,
            grammar_errors=errors,
            semantic_score=semantics.score,
        )
        timer.mark_inference_done()
        latency = timer.mark_pipeline_done()

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return EvaluationResult(
            result_id=str(uuid.uuid4()),
            session_id=session.session_id,
            user_id=user_id,
            user_text=request.user_text,
            semantic_validation=semantics,
            grammar_errors=errors,
            style_alternative=style,
            metrics=metrics,
            latency=latency,
            created_at=now,
        )


mock_llm_service = MockLLMService()
