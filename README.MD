# Git Interface API microservice

A small REST wrapper around the GitHub API: read files, add or update a file on a branch, and open a pull request.

## Run locally

```
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/flask --app app run --host=0.0.0.0     # add --debug only on your own machine
```

## Run tests

```
.venv/bin/python -m pytest
```

## Docker

```
docker build --tag git-int-api .
docker run -d -p 5000:5000 git-int-api
```

The container runs gunicorn as a non-root user.

## Authentication

Send a GitHub token in a header:

```
Authorization: Bearer <github_token>
```

The old `user_token` field in the JSON body still works, but the header is preferred because request bodies are often logged.

## Endpoints

Parameters can go in the query string or a JSON body. `base_branch` and `ref` are optional and default to the repo's default branch (`main`, `master`, ...).

| Method | Path | Required | Optional | Returns |
|---|---|---|---|---|
| GET | `/healthz` | | | `{"status": "ok"}` |
| GET | `/api/v1/getfile` | `repo_name`, `file_path` | `ref` | `{path, sha, ref, content}` (content is base64) |
| GET | `/api/v1/getfiles` | `repo_name` | `file_path` (directory, default root), `ref` | list of paths |
| PUT | `/api/v1/addfile` | `repo_name`, `branch_name`, `file_path`, `file_data`, `commit_message` | `base_branch` | `201 {message, branch, branch_created, commit}` |
| PUT | `/api/v1/updatefile` | same as `addfile` | `base_branch` | `{message, branch, branch_created, commit}` |
| POST | `/api/v1/createpr` | `repo_name`, `branch_name`, `pr_title` | `pr_message`, `base_branch` | `201 {url, number}` |

`file_data` is the base64-encoded file content. `addfile` and `updatefile` create `branch_name` from `base_branch` if it doesn't exist, and reuse it if it does.

Errors come back as JSON, `{"error": "..."}`, with a matching status: 400 for bad input, 401 for a missing token, and GitHub's own status (404, 422, ...) for GitHub errors.

### Examples

```
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  "http://localhost:5000/api/v1/getfiles?repo_name=zhhuta/webapp"

curl -X PUT -H "Authorization: Bearer $GITHUB_TOKEN" -H "Content-Type: application/json" \
  -d '{"repo_name": "zhhuta/webapp", "branch_name": "feat-x", "file_path": "src/x.go",
       "file_data": "'"$(base64 < x.go)"'", "commit_message": "Add x.go"}' \
  http://localhost:5000/api/v1/addfile

curl -X POST -H "Authorization: Bearer $GITHUB_TOKEN" -H "Content-Type: application/json" \
  -d '{"repo_name": "zhhuta/webapp", "branch_name": "feat-x", "pr_title": "Add x.go"}' \
  http://localhost:5000/api/v1/createpr
```

A Postman collection is in `github_interface.postman_collection.json`.
