"""Curated catalog of prompts for Mode A (Translation) and Mode B (Situation/Image)."""

import uuid
from typing import List, Optional
from ..models.prompt import Prompt, PromptType, DifficultyLevel
from ..models.session import SessionCreateRequest


CURATED_PROMPTS: List[Prompt] = [
    # Mode A: Translation (Russian -> English) - Easy
    Prompt(
        id="11111111-1111-1111-1111-111111111101",
        type=PromptType.TRANSLATION,
        source_language="ru",
        target_language="en",
        content="Я люблю пить горячий кофе ранним утром перед работой.",
        difficulty=DifficultyLevel.EASY,
        target_word_count=10,
        margin_buffer=4,
        max_word_count=14,
    ),
    Prompt(
        id="11111111-1111-1111-1111-111111111102",
        type=PromptType.TRANSLATION,
        source_language="ru",
        target_language="en",
        content="Солнце ярко светит, и легкий ветерок шелестит зелеными листьями деревьев.",
        difficulty=DifficultyLevel.EASY,
        target_word_count=10,
        margin_buffer=4,
        max_word_count=14,
    ),
    Prompt(
        id="11111111-1111-1111-1111-111111111103",
        type=PromptType.TRANSLATION,
        source_language="ru",
        target_language="en",
        content="Мы решили встретиться в уютном кафе на углу центральной улицы.",
        difficulty=DifficultyLevel.EASY,
        target_word_count=9,
        margin_buffer=4,
        max_word_count=13,
    ),

    # Mode A: Translation (Russian -> English) - Medium
    Prompt(
        id="11111111-1111-1111-1111-111111111104",
        type=PromptType.TRANSLATION,
        source_language="ru",
        target_language="en",
        content="Технологии искусственного интеллекта стремительно меняют подход к решению сложных задач.",
        difficulty=DifficultyLevel.MEDIUM,
        target_word_count=11,
        margin_buffer=5,
        max_word_count=16,
    ),
    Prompt(
        id="11111111-1111-1111-1111-111111111105",
        type=PromptType.TRANSLATION,
        source_language="ru",
        target_language="en",
        content="Несмотря на внезапный ливень, туристы продолжили восхождение к вершине древней горы.",
        difficulty=DifficultyLevel.MEDIUM,
        target_word_count=12,
        margin_buffer=5,
        max_word_count=17,
    ),
    Prompt(
        id="11111111-1111-1111-1111-111111111106",
        type=PromptType.TRANSLATION,
        source_language="ru",
        target_language="en",
        content="Регулярная физическая активность и здоровое питание укрепляют иммунитет и улучшают настроение.",
        difficulty=DifficultyLevel.MEDIUM,
        target_word_count=11,
        margin_buffer=5,
        max_word_count=16,
    ),

    # Mode A: Translation (Russian -> English) - Hard
    Prompt(
        id="11111111-1111-1111-1111-111111111107",
        type=PromptType.TRANSLATION,
        source_language="ru",
        target_language="en",
        content="Экономическая стабильность в условиях глобальной неопределенности требует взвешенных и стратегически выверенных решений.",
        difficulty=DifficultyLevel.HARD,
        target_word_count=13,
        margin_buffer=6,
        max_word_count=19,
    ),
    Prompt(
        id="11111111-1111-1111-1111-111111111108",
        type=PromptType.TRANSLATION,
        source_language="ru",
        target_language="en",
        content="Междисциплинарный подход в научных исследованиях позволяет выявлять фундаментальные закономерности сложных биологических систем.",
        difficulty=DifficultyLevel.HARD,
        target_word_count=14,
        margin_buffer=6,
        max_word_count=20,
    ),

    # Mode B: Situation / Image - Easy
    Prompt(
        id="22222222-2222-2222-2222-222222222201",
        type=PromptType.SITUATION_IMAGE,
        source_language="en",
        target_language="en",
        content="You are ordering your favorite meal at a lively restaurant. Tell the waiter what you want and ask for a recommendation.",
        image_url="https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400",
        difficulty=DifficultyLevel.EASY,
        target_word_count=12,
        margin_buffer=5,
        max_word_count=17,
    ),
    Prompt(
        id="22222222-2222-2222-2222-222222222202",
        type=PromptType.SITUATION_IMAGE,
        source_language="en",
        target_language="en",
        content="Describe a relaxing sunny morning in a garden filled with blooming colorful flowers.",
        image_url="https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=400",
        difficulty=DifficultyLevel.EASY,
        target_word_count=10,
        margin_buffer=5,
        max_word_count=15,
    ),

    # Mode B: Situation / Image - Medium
    Prompt(
        id="22222222-2222-2222-2222-222222222203",
        type=PromptType.SITUATION_IMAGE,
        source_language="en",
        target_language="en",
        content="You arrive at the airport and discover your flight was delayed by three hours. Express your reaction and next steps.",
        image_url="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400",
        difficulty=DifficultyLevel.MEDIUM,
        target_word_count=14,
        margin_buffer=6,
        max_word_count=20,
    ),
    Prompt(
        id="22222222-2222-2222-2222-222222222204",
        type=PromptType.SITUATION_IMAGE,
        source_language="en",
        target_language="en",
        content="Describe the bustling atmosphere of an evening tech conference with attendees exchanging innovative ideas.",
        image_url="https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=400",
        difficulty=DifficultyLevel.MEDIUM,
        target_word_count=13,
        margin_buffer=6,
        max_word_count=19,
    ),

    # Mode B: Situation / Image - Hard
    Prompt(
        id="22222222-2222-2222-2222-222222222205",
        type=PromptType.SITUATION_IMAGE,
        source_language="en",
        target_language="en",
        content="Explain how emerging automation technologies impact modern workplace culture and employee collaboration.",
        image_url="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400",
        difficulty=DifficultyLevel.HARD,
        target_word_count=16,
        margin_buffer=7,
        max_word_count=23,
    ),
]


class PromptStore:
    """In-memory catalog of curated prompts."""

    def __init__(self, prompts: Optional[List[Prompt]] = None) -> None:
        self._prompts = prompts or CURATED_PROMPTS

    def get_prompt(self, prompt_id: str) -> Optional[Prompt]:
        """Lookup prompt by UUID."""
        for p in self._prompts:
            if p.id == prompt_id:
                return p
        return None

    def filter_prompts(
        self,
        mode: Optional[PromptType] = None,
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
        difficulty: Optional[DifficultyLevel] = None,
        limit: int = 10,
    ) -> List[Prompt]:
        """Filter prompts by criteria."""
        results = self._prompts
        if mode:
            results = [p for p in results if p.type == mode]
        if source_language:
            results = [p for p in results if p.source_language == source_language]
        if target_language:
            results = [p for p in results if p.target_language == target_language]
        if difficulty:
            results = [p for p in results if p.difficulty == difficulty]
        return results[:limit]

    def select_prompt_for_session(self, request: SessionCreateRequest) -> Prompt:
        """Select a matching prompt or generate an adapted prompt based on request constraints."""
        candidates = self.filter_prompts(
            mode=request.mode,
            difficulty=request.difficulty,
            limit=5,
        )
        if not candidates:
            candidates = self.filter_prompts(mode=request.mode, limit=5)

        base_prompt = candidates[0] if candidates else self._prompts[0]

        # Adapt word count budget based on user requested target_word_count & margin_buffer
        target_words = request.target_word_count
        buffer = request.margin_buffer
        max_words = target_words + buffer

        return Prompt(
            id=str(uuid.uuid4()),
            type=request.mode,
            source_language=request.source_language,
            target_language=request.target_language,
            content=base_prompt.content,
            image_url=base_prompt.image_url,
            difficulty=request.difficulty,
            target_word_count=target_words,
            margin_buffer=buffer,
            max_word_count=max_words,
        )


prompt_store = PromptStore()
