"""Typing performance and accuracy calculation service."""

from typing import List, Optional
from ..models.metrics import SessionMetrics
from ..models.grammar import GrammarErrorSpan, ErrorSeverity


def calculate_session_metrics(
    user_text: str,
    time_spent_ms: int,
    target_word_count: int,
    margin_buffer: int,
    timer_seconds: Optional[int] = None,
    character_count: Optional[int] = None,
    keystroke_count: Optional[int] = None,
    grammar_errors: Optional[List[GrammarErrorSpan]] = None,
    semantic_score: float = 100.0,
) -> SessionMetrics:
    """Calculate speed, accuracy, and constraint compliance metrics."""
    text = user_text.strip()
    words = text.split() if text else []
    word_count = len(words)
    chars = len(user_text) if character_count is None else character_count

    # Words Per Minute: ((chars / 5) / (time_spent_ms / 60000))
    if time_spent_ms > 0 and chars > 0:
        minutes = time_spent_ms / 60000.0
        wpm = round((chars / 5.0) / minutes, 2)
    else:
        wpm = 0.0

    max_allowed = target_word_count + margin_buffer
    word_limit_exceeded = word_count > max_allowed
    target_met = (word_count >= target_word_count) and not word_limit_exceeded

    timer_expired = False
    if timer_seconds is not None and timer_seconds > 0:
        # User ran out of time if active duration exceeded timer
        timer_expired = time_spent_ms >= (timer_seconds * 1000)

    # Accuracy Score: Blend of semantic score minus grammar penalties
    if not text:
        accuracy = 0.0
    else:
        accuracy = semantic_score
        errors = grammar_errors or []
        for err in errors:
            if err.severity == ErrorSeverity.ERROR:
                accuracy -= 10.0
            elif err.severity == ErrorSeverity.WARNING:
                accuracy -= 5.0
            elif err.severity == ErrorSeverity.INFO:
                accuracy -= 2.0

        if word_limit_exceeded:
            overflow = word_count - max_allowed
            accuracy -= min(overflow * 3.0, 20.0)
        elif word_count < target_word_count:
            shortfall = target_word_count - word_count
            accuracy -= min(shortfall * 2.0, 15.0)

        accuracy = max(0.0, min(100.0, round(accuracy, 1)))

    return SessionMetrics(
        wpm=wpm,
        accuracy_score=accuracy,
        time_spent_ms=time_spent_ms,
        word_count=word_count,
        target_word_count=target_word_count,
        target_met=target_met,
        word_limit_exceeded=word_limit_exceeded,
        timer_expired=timer_expired,
    )
