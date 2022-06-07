#import base64
import base64

from github import Github, GithubException

import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True




@app.route('/', methods=['GET'])
def home():
    return '''<h1> Simple git interface </h1>
<p>A prototype API for working with github.</p>'''


@app.route('/api/v1/getfile', methods=['GET'])
def api_getfile():
    content = request.get_json()
    g = Github(content["user_token"])
    repo = g.get_repo(content["repo_name"])
    try:
        content = repo.get_contents(content["file_path"])
    except GithubException as err:
        return jsonify(err)
    return jsonify(content.content)


@app.route('/api/v1/getfiles', methods=['GET'])
def api_getallfiles():
    content = request.get_json()
    g = Github(content["user_token"])
    repo = g.get_repo(content["repo_name"])
    try:
        contents = repo.get_contents("")
    except GithubException as err:
        return jsonify(err)
    a = []
    for i in contents:
        a.append(i.path)
    return jsonify(a)


@app.route('/api/v1/addfile', methods=['PUT'])
def api_addfile():
    content = request.get_json()
    g = Github(content["user_token"])
    repo = g.get_repo(content["repo_name"])
    source = repo.get_branch("master")

    repo.create_git_ref(ref=f"refs/heads/{content['branch_name']}", sha=source.commit.sha)
    repo.create_file(content["file_path"], content["commit_message"], base64.b64decode(content["file_data"]),
                         branch=content['branch_name'])
    return jsonify(f"file add to new branch {content['branch_name']}")

@app.route('/api/v1/updatefile', methods=['PUT'])
def api_updatefile():
    content = request.get_json()
    g = Github(content["user_token"])
    repo = g.get_repo(content["repo_name"])
    source = repo.get_branch("master")
    repo.create_git_ref(ref=f"refs/heads/{content['branch_name']}", sha=source.commit.sha)
    repo.update_file(content["file_path"], content["commit_message"], base64.b64decode(content["file_data"]),
                     branch=content['branch_name'], sha=source.commit.sha)
    return jsonify("file has been updated")

@app.route('/api/v1/createpr', methods=['POST'])
def api_createpr():
    content = request.get_json()
    g = Github(content["user_token"])
    repo = g.get_repo(content["repo_name"])
    pr = repo.create_pull(title=content["pr_title"], body=content["pr_message"], head=content['branch_name'],
                          base="master")
    return jsonify(pr.html_url)


def main():
    app.run()


if __name__ == '__main__':  # pragma: no cover
    main()


base64.b64encode()