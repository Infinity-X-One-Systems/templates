"""GitHub API connector with rate-limit awareness and PAT/App token auth."""
from __future__ import annotations

import logging
import time
from typing import Any

import httpx
from pydantic import BaseModel, Field, SecretStr

logger = logging.getLogger(__name__)

_GITHUB_BASE_URL = "https://api.github.com"
_API_VERSION = "2022-11-28"


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class ConnectorError(Exception):
    """Base error for all GitHub connector failures."""


class AuthenticationError(ConnectorError):
    """Raised when credentials are rejected."""


class RateLimitError(ConnectorError):
    """Raised when the GitHub rate limit is exceeded."""

    def __init__(self, message: str, reset_at: int | None = None) -> None:
        super().__init__(message)
        self.reset_at = reset_at


class NotFoundError(ConnectorError):
    """Raised when a requested resource does not exist."""


class APIError(ConnectorError):
    """Raised for any other non-2xx response."""


# ---------------------------------------------------------------------------
# Models — requests
# ---------------------------------------------------------------------------


class DispatchInput(BaseModel):
    repo: str
    owner: str
    event_type: str
    client_payload: dict[str, Any] = Field(default_factory=dict)


class CreateIssueInput(BaseModel):
    owner: str
    repo: str
    title: str
    body: str = ""
    labels: list[str] = Field(default_factory=list)
    assignees: list[str] = Field(default_factory=list)


class UpdateProjectItemInput(BaseModel):
    project_id: str
    item_id: str
    field_id: str
    value: Any


class WorkflowRunsInput(BaseModel):
    owner: str
    repo: str
    workflow_id: str | None = None
    branch: str | None = None
    status: str | None = None
    per_page: int = Field(default=30, ge=1, le=100)
    page: int = Field(default=1, ge=1)


# ---------------------------------------------------------------------------
# Models — responses
# ---------------------------------------------------------------------------


class Issue(BaseModel):
    id: int
    number: int
    title: str
    html_url: str
    state: str
    body: str | None = None


class WorkflowRun(BaseModel):
    id: int
    name: str | None = None
    status: str | None = None
    conclusion: str | None = None
    html_url: str
    created_at: str
    updated_at: str


class WorkflowRunsResponse(BaseModel):
    total_count: int
    workflow_runs: list[WorkflowRun]


class RepoHealth(BaseModel):
    name: str
    full_name: str
    private: bool
    open_issues_count: int
    stargazers_count: int
    forks_count: int
    default_branch: str
    archived: bool
    disabled: bool


class RateLimitInfo(BaseModel):
    limit: int
    remaining: int
    reset: int
    used: int


# ---------------------------------------------------------------------------
# Connector
# ---------------------------------------------------------------------------


class GitHubConnector:
    """Async GitHub REST API connector.

    Supports Personal Access Tokens and GitHub App installation tokens.
    Checks rate-limit headers on every response and raises :class:`RateLimitError`
    before quota is exhausted.
    """

    def __init__(
        self,
        token: str | SecretStr,
        base_url: str = _GITHUB_BASE_URL,
        timeout: float = 30.0,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._token: SecretStr = (
            token if isinstance(token, SecretStr) else SecretStr(token)
        )
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = http_client

        logger.debug("GitHubConnector initialised (token=****)")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "GitHubConnector":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token.get_secret_value()}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": _API_VERSION,
            "Content-Type": "application/json",
        }

    def _check_rate_limit(self, response: httpx.Response) -> None:
        remaining = response.headers.get("x-ratelimit-remaining")
        reset = response.headers.get("x-ratelimit-reset")
        if remaining is not None and int(remaining) == 0:
            raise RateLimitError(
                f"GitHub rate limit exhausted. Resets at {reset}.",
                reset_at=int(reset) if reset else None,
            )

    def _raise_for_status(self, response: httpx.Response) -> None:
        self._check_rate_limit(response)
        if response.status_code == 401:
            raise AuthenticationError(
                f"GitHub auth failed (status 401): {response.text}"
            )
        if response.status_code == 403:
            raise AuthenticationError(
                f"GitHub forbidden (status 403): {response.text}"
            )
        if response.status_code == 404:
            raise NotFoundError(f"Resource not found (status 404): {response.text}")
        if response.status_code == 422:
            raise APIError(
                f"GitHub validation failed (status 422): {response.text}"
            )
        if response.status_code >= 400:
            raise APIError(
                f"GitHub API error (status {response.status_code}): {response.text}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def trigger_dispatch(self, inp: DispatchInput) -> None:
        """Fire a repository_dispatch event."""
        client = await self._get_client()
        payload = {
            "event_type": inp.event_type,
            "client_payload": inp.client_payload,
        }
        logger.debug(
            "trigger_dispatch owner=%s repo=%s event=%s",
            inp.owner,
            inp.repo,
            inp.event_type,
        )
        response = await client.post(
            f"{self._base_url}/repos/{inp.owner}/{inp.repo}/dispatches",
            headers=self._headers(),
            json=payload,
        )
        self._raise_for_status(response)

    async def create_issue(self, inp: CreateIssueInput) -> Issue:
        """Create a new issue and return it."""
        client = await self._get_client()
        payload: dict[str, Any] = {"title": inp.title, "body": inp.body}
        if inp.labels:
            payload["labels"] = inp.labels
        if inp.assignees:
            payload["assignees"] = inp.assignees

        logger.debug("create_issue owner=%s repo=%s title=%r", inp.owner, inp.repo, inp.title)

        response = await client.post(
            f"{self._base_url}/repos/{inp.owner}/{inp.repo}/issues",
            headers=self._headers(),
            json=payload,
        )
        self._raise_for_status(response)
        return Issue.model_validate(response.json())

    async def update_project_item(self, inp: UpdateProjectItemInput) -> dict[str, Any]:
        """Update a field value on a GitHub Projects (v2) item via GraphQL."""
        client = await self._get_client()
        mutation = """
        mutation UpdateField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: $value
          }) {
            projectV2Item { id }
          }
        }
        """
        variables = {
            "projectId": inp.project_id,
            "itemId": inp.item_id,
            "fieldId": inp.field_id,
            "value": inp.value,
        }

        logger.debug(
            "update_project_item project=%s item=%s field=%s",
            inp.project_id,
            inp.item_id,
            inp.field_id,
        )

        response = await client.post(
            f"{self._base_url}/graphql",
            headers=self._headers(),
            json={"query": mutation, "variables": variables},
        )
        self._raise_for_status(response)
        data = response.json()
        if "errors" in data:
            raise APIError(f"GraphQL errors: {data['errors']}")
        return data

    async def get_workflow_runs(self, inp: WorkflowRunsInput) -> WorkflowRunsResponse:
        """List workflow runs for a repository or a specific workflow."""
        client = await self._get_client()
        params: dict[str, Any] = {
            "per_page": inp.per_page,
            "page": inp.page,
        }
        if inp.branch:
            params["branch"] = inp.branch
        if inp.status:
            params["status"] = inp.status

        if inp.workflow_id:
            url = f"{self._base_url}/repos/{inp.owner}/{inp.repo}/actions/workflows/{inp.workflow_id}/runs"
        else:
            url = f"{self._base_url}/repos/{inp.owner}/{inp.repo}/actions/runs"

        logger.debug("get_workflow_runs owner=%s repo=%s", inp.owner, inp.repo)

        response = await client.get(url, headers=self._headers(), params=params)
        self._raise_for_status(response)
        return WorkflowRunsResponse.model_validate(response.json())

    async def get_repo_health(self, owner: str, repo: str) -> RepoHealth:
        """Fetch basic repository metadata as a health check."""
        client = await self._get_client()
        logger.debug("get_repo_health owner=%s repo=%s", owner, repo)
        response = await client.get(
            f"{self._base_url}/repos/{owner}/{repo}",
            headers=self._headers(),
        )
        self._raise_for_status(response)
        return RepoHealth.model_validate(response.json())
