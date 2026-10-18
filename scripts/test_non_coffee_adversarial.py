"""Adversarial validation script for MockLLMService non-coffee prompt verification."""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
from backend.app.services.mock_llm_service import mock_llm_service
from backend.app.models.grammar import PreferredStyle
from backend.app.models.session import SessionResponse, SessionStatus, PromptType
from backend.app.models.prompt import Prompt, DifficultyLevel

styles = [
    PreferredStyle.FORMAL,
    PreferredStyle.CONCISE,
    PreferredStyle.ACADEMIC,
    PreferredStyle.BUSINESS,
    PreferredStyle.CONVERSATIONAL,
]

coffee_keywords = ["coffee", "latte", "espresso", "cappuccino", "кофе"]

test_cases = [
    (
        "Mountain / Hiking",
        "Несмотря на внезапный ливень, туристы продолжили восхождение к вершине древней горы.",
        "The tourists continued climbing the ancient mountain despite the sudden rain.",
    ),
    (
        "AI / Technology",
        "Искусственный интеллект и современные технологии стремительно меняют подходы к решению сложных аналитических задач.",
        "Artificial intelligence and modern technologies are rapidly changing approaches to solving complex analytical tasks.",
    ),
    (
        "Weather / Nature",
        "Яркое солнце освещает цветущий сад, а легкий ветер нежно колышет зеленые листья деревьев.",
        "Bright sun illuminates the blooming garden while a light breeze rustles green leaves.",
    ),
    (
        "Health / Fitness",
        "Регулярная физическая активность и правильное питание укрепляют иммунитет и улучшают общее самочувствие.",
        "Regular exercise and balanced nutrition strengthen immunity and improve well-being.",
    ),
    (
        "Economy / Governance",
        "Экономическая стабильность в условиях глобальной неопределенности требует взвешенных и стратегически выверенных решений.",
        "Economic stability amidst global uncertainty requires balanced and strategic decisions.",
    ),
    (
        "Science / Systems",
        "Междисциплинарный подход в научных исследованиях позволяет глубже понять фундаментальные закономерности сложных биологических систем.",
        "An interdisciplinary approach in scientific research enables deeper understanding of complex biological systems.",
    ),
    (
        "Travel / Airport",
        "Due to the severe blizzard, all international flights were delayed at the terminal.",
        "Due to the blizzard, all international flights were delayed at the terminal.",
    ),
    (
        "Generic non-domain sentence",
        "The team made significant progress on the assigned software architecture project.",
        "The team made significant progress on the assigned software architecture project.",
    ),
    (
        "Arbitrary student sentence",
        "Students gathered in the library to prepare for their upcoming chemistry examination.",
        "Students gathered in the library to prepare for their upcoming chemistry examination.",
    ),
]

failures = []
passed_checks = 0

print("=== STARTING ADVERSARIAL NON-COFFEE PROMPT TESTS ===")
for topic, prompt_content, user_submission in test_cases:
    prompt = Prompt(
        id=f"p_{topic.lower().replace(' ', '_')}",
        type=PromptType.TRANSLATION,
        source_language="ru" if any("\u0400" <= c <= "\u04FF" for c in prompt_content) else "en",
        target_language="en",
        content=prompt_content,
        difficulty=DifficultyLevel.MEDIUM,
        target_word_count=15,
        margin_buffer=5,
        max_word_count=20,
    )
    for style in styles:
        session = SessionResponse(
            session_id=f"s_{topic}_{style.value}",
            status=SessionStatus.ACTIVE,
            mode=PromptType.TRANSLATION,
            prompt=prompt,
            timer_seconds=60,
            input_mode="free",
            preferred_style=style,
            allow_loose_phrasing=True,
            created_at="2026-10-17T00:00:00Z",
            expires_at="2026-10-17T00:01:00Z",
        )
        alt = mock_llm_service.generate_style_alternative(user_submission, style, session)
        full_output = f"{alt.text} {alt.explanation}".lower()

        # Check style
        if alt.style != style:
            failures.append(f"[{topic} | {style.value}] Style mismatch: expected {style}, got {alt.style}")

        # Check coffee leak
        found_leaks = [kw for kw in coffee_keywords if kw in full_output]
        if found_leaks:
            failures.append(f"[{topic} | {style.value}] Coffee leak found! Keyword(s): {found_leaks} in '{alt.text}'")

        # Check text non-empty
        if not alt.text or len(alt.text.strip()) < 10:
            failures.append(f"[{topic} | {style.value}] Output text too short or empty: '{alt.text}'")

        passed_checks += 1
        print(f"PASS: [{topic} | {style.value}] -> \"{alt.text}\"")

print(f"\nTotal checks executed: {passed_checks}")
print(f"Total failures: {len(failures)}")

if failures:
    print("\n--- FAILURES DETECTED ---", file=sys.stderr)
    for f in failures:
        print(f"FAIL: {f}", file=sys.stderr)
    sys.exit(1)
else:
    print("\n>>> VERIFICATION SUCCESS: 0 coffee mentions found across all test cases and styles! <<<")
    sys.exit(0)
