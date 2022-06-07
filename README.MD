# Git Interface API microseervice 
## Instaltion and local run for development
### Instalation
```
pip3 install -r requirements.txt
```
### run
```
python3 -m flask run --host=0.0.0.0
```
### Build docker container and run
```
docker build --tag git-int-api .
docker run -d -p 5000:5000 git-int-api
```
## API Endpoints
This microservice expose next API end point
-----
```GET /api/v1/getfile```
```
{
    "user_token": "{{git_hub_token}}",
    "repo_name": "zhhuta/webapp"
}
```
-----
```GET /api/v1/getfiles```
```
{
    "user_token": "{{git_hub_token}}",
    "repo_name": "zhhuta/webapp",
    "file_path": "main.go"
}
```
-----
```PUT /api/v1/addfile```
```
{
    "user_token": "{{git_hub_token}}",
    "repo_name": "zhhuta/webapp",
    "branch_name": "branch_{{randomString}}",
    "file_path": "src/main{{randomString}}.go",
    "file_data": "UG9ydCA1MDAwIGlzIGluIHVzZSBieSBhbm90aGVyIHByb2dyYW0uIEVpdGhlciBpZGVudGlmeSBhbmQgc3RvcCB0aGF0IHByb2dyYW0sIG9yIHN0YXJ0IHRoZSBzZXJ2ZXIgd2l0aCBhIGRpZmZlcmVudCBwb3J0Lgo=",
    "commit_message":"Commit Message {{randomString}}"

}
```
-----
```PUT /api/v1/updatefile```
```

    "user_token": "{{git_hub_token}}",
    "repo_name": "zhhuta/webapp",
    "branch_name": "branch_{{randomString}}",
    "file_path": "main3.go",
    "file_data": "UG9ydCA1MDAwIGlzIGluIHVzZSBieSBhbm90aGVyIHByb2dyYW0uIEVpdGhlciBpZGVudGlmeSBhbmQgc3RvcCB0aGF0IHByb2dyYW0sIG9yIHN0YXJ0IHRoZSBzZXJ2ZXIgd2l0aCBhIGRpZmZlcmVudCBwb3J0Lgo=",
    "commit_message":"Commit Message"

}
```
-----
```POST /api/v1/createpr```
```
{
    "user_token": "{{git_hub_token}}",
    "repo_name": "zhhuta/webapp",
    "branch_name": "branch_ixiSi",
    "pr_title": "Zhhuat test PR",
    "pr_message": "pr_message that will apear"
}
```

for more details load postman collection  
```
github_interface.postman_collection.json
```

## Body JSON params
```
    "user_token": "GitHub Personal token",
    "repo_name": "zhhuta/webapp", # repo name 
    "branch_name": "{{branch name}}",
    "file_path": "path/filename.txt",
    "file_data": "UG9ydCA1MDAwIGlzIGluIHVzZSBieSBhbm90aGVyIHByb2dyYW0uIEVpdGhlciBpZGVudGlmeSBhbmQgc3RvcCB0aGF0IHByb2dyYW0sIG9yIHN0YXJ0IHRoZSBzZXJ2ZXIgd2l0aCBhIGRpZmZlcmVudCBwb3J0Lgo=",#base64encoded file content
    "commit_message":"Commit Message"
    "pr_title": "Pull Request Tittle",
    "pr_message": "Pull Request Message"
```