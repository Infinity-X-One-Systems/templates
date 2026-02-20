"""Tests for the GitHub API connector."""
from __future__ import annotations

import httpx
import pytest
import respx

from src.connector import (
    APIError,
    AuthenticationError,
    CreateIssueInput,
    DispatchInput,
    GitHubConnector,
    Issue,
    NotFoundError,
    RateLimitError,
    RepoHealth,
    UpdateProjectItemInput,
    WorkflowRunsInput,
    WorkflowRunsResponse,
)

BASE = "https://api.github.com"


def _issue_payload(number: int = 1) -> dict:
    return {
        "id": 100 + number,
        "number": number,
        "title": f"Issue {number}",
        "html_url": f"https://github.com/owner/repo/issues/{number}",
        "state": "open",
        "body": "Test body",
    }


def _repo_payload() -> dict:
    return {
        "name": "repo",
        "full_name": "owner/repo",
        "private": False,
        "open_issues_count": 5,
        "stargazers_count": 42,
        "forks_count": 3,
        "default_branch": "main",
        "archived": False,
        "disabled": False,
    }


def _runs_payload() -> dict:
    return {
        "total_count": 1,
        "workflow_runs": [
            {
                "id": 99,
                "name": "CI",
                "status": "completed",
                "conclusion": "success",
                "html_url": "https://github.com/owner/repo/actions/runs/99",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:01:00Z",
            }
        ],
    }


# ---------------------------------------------------------------------------
# trigger_dispatch()
# ---------------------------------------------------------------------------


async def test_trigger_dispatch_success(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/repos/owner/repo/dispatches").mock(
        return_value=httpx.Response(204)
    )
    connector = GitHubConnector(token="ghp_test")
    inp = DispatchInput(
        owner="owner",
        repo="repo",
        event_type="deploy",
        client_payload={"env": "prod"},
    )
    await connector.trigger_dispatch(inp)


async def test_trigger_dispatch_401(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/repos/owner/repo/dispatches").mock(
        return_value=httpx.Response(401, text="Bad credentials")
    )
    connector = GitHubConnector(token="ghp_test")
    inp = DispatchInput(owner="owner", repo="repo", event_type="deploy")
    with pytest.raises(AuthenticationError):
        await connector.trigger_dispatch(inp)


# ---------------------------------------------------------------------------
# create_issue()
# ---------------------------------------------------------------------------


async def test_create_issue_success(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/repos/owner/repo/issues").mock(
        return_value=httpx.Response(201, json=_issue_payload(7))
    )
    connector = GitHubConnector(token="ghp_test")
    inp = CreateIssueInput(
        owner="owner",
        repo="repo",
        title="Bug report",
        body="Something broke",
        labels=["bug"],
    )
    result = await connector.create_issue(inp)

    assert isinstance(result, Issue)
    assert result.number == 7
    assert result.title == "Issue 7"


async def test_create_issue_not_found(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/repos/owner/missing/issues").mock(
        return_value=httpx.Response(404, text="Not Found")
    )
    connector = GitHubConnector(token="ghp_test")
    inp = CreateIssueInput(owner="owner", repo="missing", title="Test")
    with pytest.raises(NotFoundError):
        await connector.create_issue(inp)


# ---------------------------------------------------------------------------
# get_workflow_runs()
# ---------------------------------------------------------------------------


async def test_get_workflow_runs(respx_mock: respx.MockRouter) -> None:
    respx_mock.get(f"{BASE}/repos/owner/repo/actions/runs").mock(
        return_value=httpx.Response(200, json=_runs_payload())
    )
    connector = GitHubConnector(token="ghp_test")
    inp = WorkflowRunsInput(owner="owner", repo="repo")
    result = await connector.get_workflow_runs(inp)

    assert isinstance(result, WorkflowRunsResponse)
    assert result.total_count == 1
    assert result.workflow_runs[0].conclusion == "success"


async def test_get_workflow_runs_specific_workflow(respx_mock: respx.MockRouter) -> None:
    respx_mock.get(f"{BASE}/repos/owner/repo/actions/workflows/ci.yml/runs").mock(
        return_value=httpx.Response(200, json=_runs_payload())
    )
    connector = GitHubConnector(token="ghp_test")
    inp = WorkflowRunsInput(owner="owner", repo="repo", workflow_id="ci.yml")
    result = await connector.get_workflow_runs(inp)
    assert result.total_count == 1


# ---------------------------------------------------------------------------
# get_repo_health()
# ---------------------------------------------------------------------------


async def test_get_repo_health(respx_mock: respx.MockRouter) -> None:
    respx_mock.get(f"{BASE}/repos/owner/repo").mock(
        return_value=httpx.Response(200, json=_repo_payload())
    )
    connector = GitHubConnector(token="ghp_test")
    result = await connector.get_repo_health("owner", "repo")

    assert isinstance(result, RepoHealth)
    assert result.full_name == "owner/repo"
    assert result.stargazers_count == 42


async def test_get_repo_health_not_found(respx_mock: respx.MockRouter) -> None:
    respx_mock.get(f"{BASE}/repos/owner/ghost").mock(
        return_value=httpx.Response(404, text="Not Found")
    )
    connector = GitHubConnector(token="ghp_test")
    with pytest.raises(NotFoundError):
        await connector.get_repo_health("owner", "ghost")


# ---------------------------------------------------------------------------
# Rate limit handling
# ---------------------------------------------------------------------------


async def test_rate_limit_raises(respx_mock: respx.MockRouter) -> None:
    respx_mock.get(f"{BASE}/repos/owner/repo").mock(
        return_value=httpx.Response(
            200,
            json=_repo_payload(),
            headers={
                "x-ratelimit-remaining": "0",
                "x-ratelimit-reset": "9999999999",
            },
        )
    )
    connector = GitHubConnector(token="ghp_test")
    with pytest.raises(RateLimitError) as exc_info:
        await connector.get_repo_health("owner", "repo")
    assert exc_info.value.reset_at == 9999999999


# ---------------------------------------------------------------------------
# update_project_item() — GraphQL
# ---------------------------------------------------------------------------


async def test_update_project_item(respx_mock: respx.MockRouter) -> None:
    gql_resp = {
        "data": {
            "updateProjectV2ItemFieldValue": {
                "projectV2Item": {"id": "PVTI_abc"}
            }
        }
    }
    respx_mock.post(f"{BASE}/graphql").mock(
        return_value=httpx.Response(200, json=gql_resp)
    )
    connector = GitHubConnector(token="ghp_test")
    inp = UpdateProjectItemInput(
        project_id="PVT_abc",
        item_id="PVTI_abc",
        field_id="PVTF_abc",
        value={"text": "Done"},
    )
    result = await connector.update_project_item(inp)
    assert "data" in result


async def test_update_project_item_graphql_error(respx_mock: respx.MockRouter) -> None:
    respx_mock.post(f"{BASE}/graphql").mock(
        return_value=httpx.Response(
            200,
            json={"errors": [{"message": "Field not found"}]},
        )
    )
    connector = GitHubConnector(token="ghp_test")
    inp = UpdateProjectItemInput(
        project_id="PVT_abc",
        item_id="PVTI_abc",
        field_id="PVTF_bad",
        value={"text": "Done"},
    )
    with pytest.raises(APIError, match="GraphQL errors"):
        await connector.update_project_item(inp)


# ---------------------------------------------------------------------------
# Token masking
# ---------------------------------------------------------------------------


def test_token_not_in_repr() -> None:
    c = GitHubConnector(token="ghp_super_secret")
    assert "ghp_super_secret" not in repr(c._token)
