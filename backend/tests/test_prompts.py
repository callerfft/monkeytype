"""Prompts catalog endpoint tests."""

import pytest
import httpx


@pytest.mark.asyncio
async def test_list_all_prompts(async_client: httpx.AsyncClient):
    """GET /api/v1/prompts returns curated prompt items."""
    res = await async_client.get("/api/v1/prompts")
    assert res.status_code == 200
    prompts = res.json()
    assert isinstance(prompts, list)
    assert len(prompts) >= 5

    sample = prompts[0]
    assert "id" in sample
    assert "type" in sample
    assert "content" in sample
    assert "target_word_count" in sample
    assert "margin_buffer" in sample
    assert sample["max_word_count"] == sample["target_word_count"] + sample["margin_buffer"]


@pytest.mark.asyncio
async def test_filter_prompts_by_mode(async_client: httpx.AsyncClient):
    """Filter prompts specifically for Mode A or Mode B."""
    res_a = await async_client.get("/api/v1/prompts?mode=translation")
    assert res_a.status_code == 200
    for p in res_a.json():
        assert p["type"] == "translation"

    res_b = await async_client.get("/api/v1/prompts?mode=situation_image")
    assert res_b.status_code == 200
    for p in res_b.json():
        assert p["type"] == "situation_image"


@pytest.mark.asyncio
async def test_filter_prompts_by_difficulty(async_client: httpx.AsyncClient):
    """Filter prompts by difficulty level."""
    for diff in ["easy", "medium", "hard"]:
        res = await async_client.get(f"/api/v1/prompts?difficulty={diff}")
        assert res.status_code == 200
        for p in res.json():
            assert p["difficulty"] == diff
