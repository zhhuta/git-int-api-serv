import base64
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from github import GithubException

import app as app_module

AUTH = {"Authorization": "Bearer test-token"}
DATA = base64.b64encode(b"hello").decode()


def not_found():
    return GithubException(404, {"message": "Not Found"}, None)


@pytest.fixture
def repo(monkeypatch):
    repo = MagicMock()
    repo.default_branch = "main"
    gh = MagicMock()
    gh.get_repo.return_value = repo
    monkeypatch.setattr(app_module, "Github", MagicMock(return_value=gh))
    return repo


@pytest.fixture
def client():
    return app_module.create_app().test_client()


def test_missing_token(client, repo):
    r = client.get("/api/v1/getfiles", query_string={"repo_name": "o/r"})
    assert r.status_code == 401


def test_legacy_body_token(client, repo):
    repo.get_contents.return_value = [SimpleNamespace(path="a.txt")]
    r = client.get("/api/v1/getfiles", json={"user_token": "t", "repo_name": "o/r"})
    assert r.status_code == 200
    assert r.json == ["a.txt"]


def test_missing_field(client, repo):
    r = client.get("/api/v1/getfile", headers=AUTH, query_string={"repo_name": "o/r"})
    assert r.status_code == 400
    assert "file_path" in r.json["error"]


def test_getfile_uses_default_branch(client, repo):
    repo.get_contents.return_value = SimpleNamespace(path="a.txt", sha="s1", content="aGk=")
    r = client.get(
        "/api/v1/getfile", headers=AUTH, query_string={"repo_name": "o/r", "file_path": "a.txt"}
    )
    assert r.status_code == 200
    assert r.json["content"] == "aGk="
    repo.get_contents.assert_called_once_with("a.txt", ref="main")


def test_github_error_is_json(client, repo):
    repo.get_contents.side_effect = not_found()
    r = client.get(
        "/api/v1/getfile", headers=AUTH, query_string={"repo_name": "o/r", "file_path": "x"}
    )
    assert r.status_code == 404
    assert r.json["error"] == "Not Found"


def test_addfile_creates_branch_from_default(client, repo):
    repo.get_branch.side_effect = [not_found(), SimpleNamespace(commit=SimpleNamespace(sha="c0"))]
    repo.create_file.return_value = {"commit": SimpleNamespace(sha="c1")}
    r = client.put(
        "/api/v1/addfile",
        headers=AUTH,
        json={
            "repo_name": "o/r",
            "branch_name": "feat",
            "file_path": "a.txt",
            "file_data": DATA,
            "commit_message": "add",
        },
    )
    assert r.status_code == 201
    assert r.json["branch_created"] is True
    repo.get_branch.assert_called_with("main")
    repo.create_git_ref.assert_called_once_with(ref="refs/heads/feat", sha="c0")
    repo.create_file.assert_called_once_with("a.txt", "add", b"hello", branch="feat")


def test_addfile_rejects_bad_base64(client, repo):
    r = client.put(
        "/api/v1/addfile",
        headers=AUTH,
        json={
            "repo_name": "o/r",
            "branch_name": "feat",
            "file_path": "a.txt",
            "file_data": "not base64!!",
            "commit_message": "add",
        },
    )
    assert r.status_code == 400


def test_updatefile_uses_blob_sha_and_existing_branch(client, repo):
    repo.get_branch.return_value = SimpleNamespace(commit=SimpleNamespace(sha="c0"))
    repo.get_contents.return_value = SimpleNamespace(path="a.txt", sha="blob1")
    repo.update_file.return_value = {"commit": SimpleNamespace(sha="c2")}
    r = client.put(
        "/api/v1/updatefile",
        headers=AUTH,
        json={
            "repo_name": "o/r",
            "branch_name": "feat",
            "file_path": "a.txt",
            "file_data": DATA,
            "commit_message": "upd",
        },
    )
    assert r.status_code == 200
    assert r.json["branch_created"] is False
    repo.create_git_ref.assert_not_called()
    repo.get_contents.assert_called_once_with("a.txt", ref="feat")
    repo.update_file.assert_called_once_with("a.txt", "upd", b"hello", "blob1", branch="feat")


def test_createpr_targets_default_branch(client, repo):
    repo.create_pull.return_value = SimpleNamespace(html_url="https://x/pr/1", number=1)
    r = client.post(
        "/api/v1/createpr",
        headers=AUTH,
        json={"repo_name": "o/r", "branch_name": "feat", "pr_title": "T", "pr_message": "B"},
    )
    assert r.status_code == 201
    assert r.json == {"url": "https://x/pr/1", "number": 1}
    repo.create_pull.assert_called_once_with(title="T", body="B", head="feat", base="main")
