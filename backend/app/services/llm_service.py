"""Unified LLM service interfacing live Gemini Flash and deterministic MockLLMService."""

import json
import logging
import re
import uuid
from typing import AsyncGenerator, Optional, List
import httpx

from ..models.session import SessionResponse
from ..models.evaluation import (
    EvaluationRequest,
    EvaluationResult,
    SSESessionStartPayload,
    SSETokenPayload,
    SSEDonePayload,
)
from ..models.grammar import GrammarErrorSpan, SemanticValidation, StyleAlternative
from ..config import settings
from .mock_llm_service import mock_llm_service
from .metrics_service import calculate_session_metrics
from ..utils.latency import LatencyTimer
from ..utils.sse import format_sse_event

logger = logging.getLogger(__name__)


def is_case_or_period_error(err: GrammarErrorSpan, text: str) -> bool:
    """Check if an error relates to sentence capitalization or terminal punctuation."""
    msg = err.message.lower()
    cat = (err.category.value if hasattr(err.category, "value") else str(err.category)).lower()
    orig = err.original_text.strip()
    trimmed_len = len(text.rstrip())

    # Initial capitalization
    if "capital" in msg or "uppercase" in msg:
        return True
    if err.start == 0 and cat in ("punctuation", "grammar", "spelling") and len(orig) <= 1:
        return True

    # Terminal punctuation (period/dot at the end)
    if "terminal" in msg or "period" in msg or "full stop" in msg or "point" in msg:
        return True
    if (err.end >= trimmed_len or err.start >= max(0, trimmed_len - 1)) and (cat == "punctuation" or orig in (".", "!", "?", "")):
        return True

    return False


class LLMService:

    """LLM dispatcher with automated fallback between live Gemini Flash API and Mock."""

    def __init__(self) -> None:
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.GEMINI_API_KEY
        self.model = settings.GEMINI_MODEL
        self.base_url = settings.GEMINI_BASE_URL

    async def is_connected(self) -> bool:
        """Check availability of configured LLM provider."""
        is_real_key = bool(self.api_key and not self.api_key.startswith("YOUR_"))
        if self.provider == "mock" or not is_real_key:
            return True

        # Test reachability of Gemini REST endpoint
        try:
            url = f"{self.base_url}/models/{self.model}?key={self.api_key}"
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(url)
                return res.status_code == 200
        except Exception:
            return False

    async def _stream_gemini(
        self,
        request: EvaluationRequest,
        session: SessionResponse,
    ) -> AsyncGenerator[str, None]:
        """Call Google Generative Language API streaming endpoint and yield SSE frames."""
        check_case_and_period = (
            request.check_case_and_period
            if request.check_case_and_period is not None
            else getattr(session, "check_case_and_period", False)
        )

        case_punct_instruction = (
            ""
            if check_case_and_period
            else "Do NOT check, flag, or penalize missing initial capitalization or missing terminal punctuation (period/dot) at the end of the sentence. Ignore them completely. "
        )

        system_instruction = (
            "You are an expert real-time linguistic evaluation engine for LinguaType.\n"
            "Evaluate the user's typed submission against the exercise prompt.\n"
            f"Exercise Mode: {session.mode.value}\n"
            f"Source Language: {session.prompt.source_language}\n"
            f"Target Language: {session.prompt.target_language}\n"
            f"Prompt Content: {session.prompt.content}\n"
            f"Preferred Style Register: {session.preferred_style.value}\n"
            f"Allow Loose Phrasing: {session.allow_loose_phrasing}\n"
            f"Check Capitalization and Period: {check_case_and_period}\n"
            f"{case_punct_instruction}"
            "Analyze: 1. grammar and spelling error spans with 0-based character offsets in user text. "
            "2. semantic accuracy and fidelity score (0 to 100). "
            f"3. exactly ONE stylistic alternative in the requested register ({session.preferred_style.value}) with an explanation.\n"
            "Return valid JSON adhering to the specified schema."
        )


        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"User Submission:\n{request.user_text}"}],
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "grammar_errors": {
                            "type": "ARRAY",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "start": {"type": "INTEGER"},
                                    "end": {"type": "INTEGER"},
                                    "original_text": {"type": "STRING"},
                                    "message": {"type": "STRING"},
                                    "suggestion": {"type": "STRING"},
                                    "category": {
                                        "type": "STRING",
                                        "enum": [
                                            "grammar",
                                            "spelling",
                                            "punctuation",
                                            "syntax",
                                            "word_choice",
                                            "agreement",
                                            "tense",
                                        ],
                                    },
                                    "severity": {
                                        "type": "STRING",
                                        "enum": ["error", "warning", "info"],
                                    },
                                },
                                "required": [
                                    "start",
                                    "end",
                                    "original_text",
                                    "message",
                                    "suggestion",
                                    "category",
                                    "severity",
                                ],
                            },
                        },
                        "semantic_validation": {
                            "type": "OBJECT",
                            "properties": {
                                "is_valid": {"type": "BOOLEAN"},
                                "score": {"type": "NUMBER"},
                                "explanation": {"type": "STRING"},
                                "missing_concepts": {
                                    "type": "ARRAY",
                                    "items": {"type": "STRING"},
                                },
                            },
                            "required": [
                                "is_valid",
                                "score",
                                "explanation",
                                "missing_concepts",
                            ],
                        },
                        "style_alternative": {
                            "type": "OBJECT",
                            "properties": {
                                "text": {"type": "STRING"},
                                "explanation": {"type": "STRING"},
                            },
                            "required": ["text", "explanation"],
                        },
                    },
                    "required": [
                        "grammar_errors",
                        "semantic_validation",
                        "style_alternative",
                    ],
                },
                "maxOutputTokens": 2048,
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ],
        }

        timer = LatencyTimer()

        async with httpx.AsyncClient(timeout=15.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    raise RuntimeError(
                        f"Gemini API returned {response.status_code}: {body.decode('utf-8', errors='ignore')}"
                    )

                # 1. Yield session_start immediately upon connection
                start_payload = SSESessionStartPayload(
                    session_id=session.session_id,
                    status="active",
                )
                yield format_sse_event("session_start", start_payload)

                full_text = ""
                token_idx = 0
                first_token = False

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data:"):
                        data_str = line[5:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk_json = json.loads(data_str)
                        except json.JSONDecodeError:
                            continue

                        candidates = chunk_json.get("candidates", [])
                        if not candidates:
                            continue
                        parts = candidates[0].get("content", {}).get("parts", [])
                        for part in parts:
                            # Skip internal thinking tokens from Gemini 2.0 reasoning variants
                            if part.get("thought", False):
                                continue
                            text_part = part.get("text", "")
                            if text_part:
                                if not first_token:
                                    timer.mark_ttft()
                                    first_token = True
                                full_text += text_part
                                token_payload = SSETokenPayload(
                                    text=text_part,
                                    token=text_part,
                                    index=token_idx,
                                )
                                yield format_sse_event("token", token_payload)
                                token_idx += 1

                if not timer.ttft_time:
                    timer.mark_ttft()
                timer.mark_inference_done()

                # Parse accumulated structured JSON with markdown fence stripping
                cleaned_text = full_text.strip()
                if cleaned_text.startswith("```"):
                    cleaned_text = re.sub(r"^```(?:json)?\s*", "", cleaned_text, flags=re.MULTILINE)
                    cleaned_text = re.sub(r"\s*```$", "", cleaned_text.strip())

                try:
                    parsed = json.loads(cleaned_text)
                except json.JSONDecodeError:
                    parsed = {}

                # Construct grammar error spans with exact character offset realignment
                raw_errors = parsed.get("grammar_errors", [])
                grammar_errors: List[GrammarErrorSpan] = []
                for item in raw_errors:
                    try:
                        orig = item.get("original_text", "")
                        start_pos = int(item.get("start", 0))
                        end_pos = int(item.get("end", 0))
                        # Align offsets precisely if original_text is present in user text
                        if orig and orig in request.user_text:
                            found = request.user_text.find(orig)
                            if found != -1:
                                start_pos = found
                                end_pos = found + len(orig)

                        span = GrammarErrorSpan(
                            start=start_pos,
                            end=end_pos,
                            original_text=orig,
                            message=item.get("message", ""),
                            suggestion=item.get("suggestion", ""),
                            category=item.get("category", "grammar"),
                            severity=item.get("severity", "error"),
                        )
                        grammar_errors.append(span)
                    except Exception:
                        pass

                if not check_case_and_period:
                    grammar_errors = [e for e in grammar_errors if not is_case_or_period_error(e, request.user_text)]

                # Construct semantic validation

                raw_sem = parsed.get("semantic_validation", {})
                semantic_val = SemanticValidation(
                    is_valid=raw_sem.get("is_valid", True),
                    score=float(raw_sem.get("score", 85.0)),
                    explanation=raw_sem.get("explanation", "Evaluation completed."),
                    missing_concepts=raw_sem.get("missing_concepts", []),
                )

                # Construct style alternative
                raw_style = parsed.get("style_alternative", {})
                style_alt = StyleAlternative(
                    style=session.preferred_style,
                    text=raw_style.get("text", request.user_text),
                    explanation=raw_style.get(
                        "explanation", "Stylistic alternative generated by Gemini Flash."
                    ),
                )

                # Calculate session metrics
                metrics = calculate_session_metrics(
                    user_text=request.user_text,
                    time_spent_ms=request.time_spent_ms,
                    target_word_count=session.prompt.target_word_count,
                    margin_buffer=session.prompt.margin_buffer,
                    timer_seconds=session.timer_seconds,
                    character_count=request.character_count,
                    keystroke_count=request.keystroke_count,
                    grammar_errors=grammar_errors,
                    semantic_score=semantic_val.score,
                )

                # Yield structured events
                yield format_sse_event("grammar_errors", grammar_errors)
                yield format_sse_event("semantic_check", semantic_val)
                yield format_sse_event("style_alternative", style_alt)
                yield format_sse_event("metrics", metrics)

                # Final done event with SLA telemetry
                latency = timer.mark_pipeline_done()
                done_payload = SSEDonePayload(
                    evaluation_id=str(uuid.uuid4()),
                    result_id=str(uuid.uuid4()),
                    latency=latency,
                )
                yield format_sse_event("done", done_payload)

    async def stream_evaluation(
        self,
        request: EvaluationRequest,
        session: SessionResponse,
    ) -> AsyncGenerator[str, None]:
        """Stream SSE evaluation frames from configured provider with graceful fallback."""
        is_real_key = bool(self.api_key and not self.api_key.startswith("YOUR_"))
        if self.provider == "gemini" and is_real_key:
            yielded_any = False
            try:
                async for chunk in self._stream_gemini(request, session):
                    yielded_any = True
                    yield chunk
                return
            except Exception as e:
                logger.warning(
                    f"Live Gemini Flash streaming failed ({e}); falling back to MockLLMService."
                )
                if yielded_any:
                    return

        async for chunk in mock_llm_service.stream_evaluation(request, session):
            yield chunk

    def evaluate_sync(
        self,
        request: EvaluationRequest,
        session: SessionResponse,
        user_id: Optional[str] = None,
    ) -> EvaluationResult:
        """Evaluate submission synchronously."""
        return mock_llm_service.evaluate_sync(request, session, user_id=user_id)


llm_service = LLMService()
