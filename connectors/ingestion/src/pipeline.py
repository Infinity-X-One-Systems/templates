from __future__ import annotations

import asyncio
import time
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from pydantic import BaseModel, Field


class RetryConfig(BaseModel):
    max_attempts: int = 3
    backoff_base: float = 2.0
    max_wait: float = 60.0


class IngestionJob(BaseModel):
    url: str
    method: str = "GET"
    headers: dict = Field(default_factory=dict)
    body: Optional[str] = None
    priority: int = 0


class IngestionResult(BaseModel):
    job_id: str
    url: str
    status_code: Optional[int] = None
    content: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float
    attempt: int


class PipelineStats(BaseModel):
    jobs_total: int
    jobs_success: int
    jobs_failed: int
    avg_duration_ms: float


class RateLimiter:
    """Token-bucket rate limiter enforcing a maximum requests-per-second rate."""

    def __init__(self, max_requests_per_second: float = 2.0) -> None:
        self.max_rps = max_requests_per_second
        self._min_interval = 1.0 / max_requests_per_second
        self._last_call: float = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            wait = self._min_interval - (now - self._last_call)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_call = time.monotonic()


class RobotsTxtChecker:
    """Fetches and caches robots.txt per domain to enforce crawl rules."""

    def __init__(self) -> None:
        # None value means "no restrictions found" for that domain
        self._cache: dict[str, Optional[RobotFileParser]] = {}

    async def is_allowed(self, url: str, user_agent: str = "*") -> bool:
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain not in self._cache:
            robots_url = f"{domain}/robots.txt"
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(robots_url, timeout=5.0)
                if response.status_code == 200:
                    parser.parse(response.text.splitlines())
                    self._cache[domain] = parser
                else:
                    self._cache[domain] = None
            except Exception:
                self._cache[domain] = None

        cached = self._cache.get(domain)
        if cached is None:
            return True
        return cached.can_fetch(user_agent, url)


class IngestionPipeline:
    """Async HTTP ingestion pipeline with rate limiting, retries, and robots.txt support."""

    def __init__(
        self,
        rate_limit_rps: float = 2.0,
        retry_config: Optional[RetryConfig] = None,
        respect_robots: bool = True,
    ) -> None:
        self._rate_limiter = RateLimiter(max_requests_per_second=rate_limit_rps)
        self._retry_config = retry_config or RetryConfig()
        self._respect_robots = respect_robots
        self._robots_checker = RobotsTxtChecker() if respect_robots else None
        self._results: list[IngestionResult] = []

    async def fetch(self, job: IngestionJob) -> IngestionResult:
        job_id = f"{job.url}-{id(job)}"

        if self._respect_robots and self._robots_checker:
            allowed = await self._robots_checker.is_allowed(job.url)
            if not allowed:
                result = IngestionResult(
                    job_id=job_id,
                    url=job.url,
                    error="Blocked by robots.txt",
                    duration_ms=0.0,
                    attempt=0,
                )
                self._results.append(result)
                return result

        last_error: Optional[str] = None
        duration_ms: float = 0.0

        for attempt in range(1, self._retry_config.max_attempts + 1):
            await self._rate_limiter.acquire()
            start = time.monotonic()
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.request(
                        method=job.method,
                        url=job.url,
                        headers=job.headers,
                        content=job.body,
                        timeout=30.0,
                    )
                duration_ms = (time.monotonic() - start) * 1000
                result = IngestionResult(
                    job_id=job_id,
                    url=job.url,
                    status_code=response.status_code,
                    content=response.text,
                    duration_ms=duration_ms,
                    attempt=attempt,
                )
                self._results.append(result)
                return result
            except Exception as exc:
                duration_ms = (time.monotonic() - start) * 1000
                last_error = str(exc)
                if attempt < self._retry_config.max_attempts:
                    wait = min(
                        self._retry_config.backoff_base * (2 ** (attempt - 1)),
                        self._retry_config.max_wait,
                    )
                    await asyncio.sleep(wait)

        result = IngestionResult(
            job_id=job_id,
            url=job.url,
            error=last_error,
            duration_ms=duration_ms,
            attempt=self._retry_config.max_attempts,
        )
        self._results.append(result)
        return result

    async def fetch_batch(self, jobs: list[IngestionJob]) -> list[IngestionResult]:
        sorted_jobs = sorted(jobs, key=lambda j: j.priority, reverse=True)
        return await asyncio.gather(*[self.fetch(job) for job in sorted_jobs])

    def get_stats(self) -> PipelineStats:
        total = len(self._results)
        success = sum(
            1 for r in self._results if r.error is None and r.status_code is not None
        )
        failed = total - success
        avg_duration = (
            sum(r.duration_ms for r in self._results) / total if total > 0 else 0.0
        )
        return PipelineStats(
            jobs_total=total,
            jobs_success=success,
            jobs_failed=failed,
            avg_duration_ms=avg_duration,
        )


if __name__ == "__main__":
    async def _main() -> None:
        pipeline = IngestionPipeline(rate_limit_rps=2.0)
        print("IngestionPipeline initialized.")
        stats = pipeline.get_stats()
        print(f"Stats: {stats}")

    asyncio.run(_main())
