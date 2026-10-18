"""Thread-safe in-memory session and user history storage."""

import uuid
import datetime
from typing import Dict, List, Optional, Tuple

from ..models.session import (
    SessionCreateRequest,
    SessionResponse,
    SessionStatus,
)
from ..models.user import (
    UserProfile,
    UserProfileUpdate,
    GameResultSummary,
)
from ..models.evaluation import EvaluationResult
from .prompt_store import prompt_store
from ..config import settings


class SessionStore:
    """In-memory repository for active sessions, user profiles, and game history."""

    def __init__(self) -> None:
        self._sessions: Dict[str, SessionResponse] = {}
        self._user_results: Dict[str, List[GameResultSummary]] = {}
        self._user_profiles: Dict[str, UserProfile] = {}
        self._init_mock_user()

    def _init_mock_user(self) -> None:
        """Seed default profile for development/testing."""
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        default_user = UserProfile(
            id="mock-user-123",
            email="user@linguatype.app",
            display_name="LinguaType Master",
            native_language="ru",
            target_language="en",
            created_at=now,
            updated_at=now,
        )
        self._user_profiles[default_user.id] = default_user
        self._user_results[default_user.id] = []

    def create_session(self, request: SessionCreateRequest) -> SessionResponse:
        """Initialize and store a new game session."""
        session_id = str(uuid.uuid4())
        prompt = prompt_store.select_prompt_for_session(request)
        now = datetime.datetime.now(datetime.timezone.utc)
        expires_at = now + datetime.timedelta(hours=settings.SESSION_EXPIRY_HOURS)

        session = SessionResponse(
            session_id=session_id,
            status=SessionStatus.ACTIVE,
            mode=request.mode,
            prompt=prompt,
            timer_seconds=request.timer_seconds,
            input_mode=request.input_mode,
            preferred_style=request.preferred_style,
            allow_loose_phrasing=request.allow_loose_phrasing,
            check_case_and_period=request.check_case_and_period,
            created_at=now.isoformat(),
            expires_at=expires_at.isoformat(),
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionResponse]:
        """Fetch session by ID if exists and not expired."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        # Check expiration
        expires = datetime.datetime.fromisoformat(session.expires_at)
        now = datetime.datetime.now(datetime.timezone.utc)
        if now > expires and session.status == SessionStatus.ACTIVE:
            session.status = SessionStatus.EXPIRED

        return session

    def mark_session_completed(self, session_id: str) -> None:
        """Update session status to completed."""
        session = self._sessions.get(session_id)
        if session:
            session.status = SessionStatus.COMPLETED

    def save_result(
        self,
        result: EvaluationResult,
        session: SessionResponse,
        user_id: Optional[str] = None,
    ) -> GameResultSummary:
        """Record game result summary in user history."""
        summary = GameResultSummary(
            id=result.result_id,
            session_id=session.session_id,
            mode=session.mode,
            source_language=session.prompt.source_language,
            target_language=session.prompt.target_language,
            prompt_content=session.prompt.content,
            user_text=result.user_text,
            time_spent_ms=result.metrics.time_spent_ms,
            wpm=result.metrics.wpm,
            accuracy_score=result.metrics.accuracy_score,
            semantic_valid=result.semantic_validation.is_valid,
            error_count=len(result.grammar_errors),
            recommended_variant=result.style_alternative.text,
            preferred_style=result.style_alternative.style.value,
            created_at=result.created_at,
        )

        owner = user_id or "mock-user-123"
        if owner not in self._user_results:
            self._user_results[owner] = []
        self._user_results[owner].insert(0, summary)

        self.mark_session_completed(session.session_id)
        return summary

    def get_results(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        mode: Optional[str] = None,
    ) -> Tuple[List[GameResultSummary], int]:
        """Retrieve paginated results for a user."""
        history = self._user_results.get(user_id, [])
        if mode:
            history = [r for r in history if r.mode.value == mode]

        total = len(history)
        page = history[offset : offset + limit]
        return page, total

    def get_user_profile(self, user_id: str, email: str = "user@linguatype.app") -> UserProfile:
        """Fetch or create user profile."""
        if user_id not in self._user_profiles:
            now = datetime.datetime.now(datetime.timezone.utc).isoformat()
            self._user_profiles[user_id] = UserProfile(
                id=user_id,
                email=email,
                display_name=None,
                created_at=now,
                updated_at=now,
            )
            self._user_results[user_id] = []
        return self._user_profiles[user_id]

    def update_user_profile(self, user_id: str, update: UserProfileUpdate) -> UserProfile:
        """Update preferences on user profile."""
        profile = self.get_user_profile(user_id)
        if update.native_language is not None:
            profile.native_language = update.native_language
        if update.target_language is not None:
            profile.target_language = update.target_language
        if update.preferred_style is not None:
            profile.preferred_style = update.preferred_style
        if update.allow_loose_phrasing is not None:
            profile.allow_loose_phrasing = update.allow_loose_phrasing
        if update.input_mode is not None:
            profile.input_mode = update.input_mode

        profile.updated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return profile


session_store = SessionStore()
