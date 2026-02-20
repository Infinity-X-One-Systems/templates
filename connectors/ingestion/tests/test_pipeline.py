from __future__ import annotations

import time

import httpx
import pytest
import respx

from pipeline import IngestionJob, IngestionPipeline, RateLimiter, RetryConfig


@pytest.mark.asyncio
async def test_rate_limiter_acquire() -> None:
    """Two back-to-back acquires at 10 rps must take at least 1/10 s."""
    limiter = RateLimiter(max_requests_per_second=10.0)
    start = time.monotonic()
    await limiter.acquire()
    await limiter.acquire()
    elapsed = time.monotonic() - start
    assert elapsed >= 0.09


@respx.mock
@pytest.mark.asyncio
async def test_fetch_success() -> None:
    respx.get("https://example.com/data").mock(
        return_value=httpx.Response(200, text="hello")
    )
    pipeline = IngestionPipeline(rate_limit_rps=1000.0, respect_robots=False)
    job = IngestionJob(url="https://example.com/data")
    result = await pipeline.fetch(job)

    assert result.status_code == 200
    assert result.content == "hello"
    assert result.error is None
    assert result.attempt == 1


@respx.mock
@pytest.mark.asyncio
async def test_fetch_retry_on_error() -> None:
    call_count = 0

    def _side_effect(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise httpx.ConnectError("connection refused")
        return httpx.Response(200, text="ok")

    respx.get("https://example.com/flaky").mock(side_effect=_side_effect)

    pipeline = IngestionPipeline(
        rate_limit_rps=1000.0,
        retry_config=RetryConfig(max_attempts=3, backoff_base=0.01, max_wait=0.05),
        respect_robots=False,
    )
    job = IngestionJob(url="https://example.com/flaky")
    result = await pipeline.fetch(job)

    assert result.status_code == 200
    assert result.attempt == 3
    assert result.error is None


@respx.mock
@pytest.mark.asyncio
async def test_robots_txt_blocks_disallowed() -> None:
    respx.get("https://restricted.com/robots.txt").mock(
        return_value=httpx.Response(
            200, text="User-agent: *\nDisallow: /private/\n"
        )
    )

    pipeline = IngestionPipeline(rate_limit_rps=1000.0, respect_robots=True)
    job = IngestionJob(url="https://restricted.com/private/data")
    result = await pipeline.fetch(job)

    assert result.error == "Blocked by robots.txt"
    assert result.status_code is None


@respx.mock
@pytest.mark.asyncio
async def test_batch_fetch() -> None:
    respx.get("https://example.com/a").mock(return_value=httpx.Response(200, text="a"))
    respx.get("https://example.com/b").mock(return_value=httpx.Response(200, text="b"))
    respx.get("https://example.com/c").mock(return_value=httpx.Response(200, text="c"))

    pipeline = IngestionPipeline(rate_limit_rps=1000.0, respect_robots=False)
    jobs = [
        IngestionJob(url="https://example.com/a"),
        IngestionJob(url="https://example.com/b"),
        IngestionJob(url="https://example.com/c"),
    ]
    results = await pipeline.fetch_batch(jobs)

    assert len(results) == 3
    assert all(r.status_code == 200 for r in results)
    contents = {r.content for r in results}
    assert contents == {"a", "b", "c"}

    stats = pipeline.get_stats()
    assert stats.jobs_total == 3
    assert stats.jobs_success == 3
    assert stats.jobs_failed == 0
