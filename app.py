"""Git Interface API: a small REST wrapper around the GitHub API (PyGitHub)."""

import base64
import binascii
import os

from flask import Flask, jsonify, request
from github import Auth, Github, GithubException


class ApiError(Exception):
    """An error returned to the client as JSON with an HTTP status."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


def get_params():
    """Merge query string and JSON body (body wins) into one dict."""
    params = dict(request.args)
    body = request.get_json(silent=True)
    if isinstance(body, dict):
        params.update(body)
    return params


def require(params, *names):
    missing = [n for n in names if not params.get(n)]
    if missing:
        raise ApiError(f"missing required field(s): {', '.join(missing)}")
    return [params[n] for n in names]


def get_token(params):
    """Token from 'Authorization: Bearer <token>' (preferred) or legacy 'user_token'."""
    header = request.headers.get("Authorization", "")
    scheme, _, value = header.partition(" ")
    if scheme.lower() in ("bearer", "token") and value.strip():
        return value.strip()
    if params.get("user_token"):
        return params["user_token"]
    raise ApiError("missing GitHub token: send 'Authorization: Bearer <token>'", 401)


def get_repo(params):
    (repo_name,) = require(params, "repo_name")
    return Github(auth=Auth.Token(get_token(params))).get_repo(repo_name)


def decode_file_data(data):
    try:
        return base64.b64decode(data, validate=True)
    except (binascii.Error, ValueError):
        raise ApiError("file_data must be a base64-encoded string")


def ensure_branch(repo, branch, base):
    """Create `branch` from `base` unless it already exists. Returns True if created."""
    try:
        repo.get_branch(branch)
        return False
    except GithubException as err:
        if err.status != 404:
            raise
    source = repo.get_branch(base)
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=source.commit.sha)
    return True


def create_app():
    app = Flask(__name__)

    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify(error=err.message), err.status

    @app.errorhandler(GithubException)
    def handle_github_error(err):
        message = err.data.get("message") if isinstance(err.data, dict) else str(err.data)
        status = err.status if isinstance(err.status, int) and 400 <= err.status < 600 else 502
        return jsonify(error=message or "GitHub API error", github_status=err.status), status

    @app.get("/")
    def home():
        return "<h1>Simple git interface</h1><p>A prototype API for working with GitHub.</p>"

    @app.get("/healthz")
    def healthz():
        return jsonify(status="ok")

    @app.get("/api/v1/getfile")
    def api_getfile():
        params = get_params()
        repo = get_repo(params)
        (file_path,) = require(params, "file_path")
        ref = params.get("ref") or repo.default_branch
        content = repo.get_contents(file_path, ref=ref)
        if isinstance(content, list):
            raise ApiError(f"'{file_path}' is a directory; use /api/v1/getfiles")
        return jsonify(path=content.path, sha=content.sha, ref=ref, content=content.content)

    @app.get("/api/v1/getfiles")
    def api_getfiles():
        params = get_params()
        repo = get_repo(params)
        path = params.get("file_path") or params.get("path") or ""
        ref = params.get("ref") or repo.default_branch
        contents = repo.get_contents(path, ref=ref)
        if not isinstance(contents, list):
            contents = [contents]
        return jsonify([c.path for c in contents])

    @app.put("/api/v1/addfile")
    def api_addfile():
        params = get_params()
        repo = get_repo(params)
        branch, file_path, file_data, message = require(
            params, "branch_name", "file_path", "file_data", "commit_message"
        )
        data = decode_file_data(file_data)
        base = params.get("base_branch") or repo.default_branch
        created = ensure_branch(repo, branch, base)
        result = repo.create_file(file_path, message, data, branch=branch)
        return jsonify(
            message=f"file added to branch {branch}",
            branch=branch,
            branch_created=created,
            commit=result["commit"].sha,
        ), 201

    @app.put("/api/v1/updatefile")
    def api_updatefile():
        params = get_params()
        repo = get_repo(params)
        branch, file_path, file_data, message = require(
            params, "branch_name", "file_path", "file_data", "commit_message"
        )
        data = decode_file_data(file_data)
        base = params.get("base_branch") or repo.default_branch
        created = ensure_branch(repo, branch, base)
        # The update needs the file's blob SHA on the target branch, not a commit SHA.
        existing = repo.get_contents(file_path, ref=branch)
        if isinstance(existing, list):
            raise ApiError(f"'{file_path}' is a directory")
        result = repo.update_file(file_path, message, data, existing.sha, branch=branch)
        return jsonify(
            message=f"file updated on branch {branch}",
            branch=branch,
            branch_created=created,
            commit=result["commit"].sha,
        )

    @app.post("/api/v1/createpr")
    def api_createpr():
        params = get_params()
        repo = get_repo(params)
        branch, title = require(params, "branch_name", "pr_title")
        base = params.get("base_branch") or repo.default_branch
        pr = repo.create_pull(
            title=title, body=params.get("pr_message", ""), head=branch, base=base
        )
        return jsonify(url=pr.html_url, number=pr.number), 201

    return app


app = create_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
