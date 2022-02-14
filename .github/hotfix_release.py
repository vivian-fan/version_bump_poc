# Goal: recompute versions on develop and master branch
# return {'include': [{'file': 'internal', 'version': 1.1.0, 'branch': 'master'}, {'file': 'external', 'version': 1.1.0, 'branch': 'develop'}, {'file': 'data_science', 'version': 1.1.0, 'branch': 'master'}]}

import os
import sys
import shutil
import yaml
import git
import json


def get_remote():
    username = "vivian-fan"
    password = sys.argv[1]
    remote = f"https://{username}:{password}@github.com/vivian-fan/hotfix_release_version.git"
    return remote


def get_clone_repo(remote, path, branch):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    clone_repo = git.Repo.clone_from(remote, path, branch=branch)
    return clone_repo


def get_intents(path):
    with open(path + "/.github/intent.yml", "r") as intent_mgmt_file:
        intent_mgmt_content = yaml.safe_load(intent_mgmt_file)
    return intent_mgmt_content


def get_version_from_branch(path, file):
    file += '.yml'
    with open(path + "/" + file, "r") as spec_file:
        spec_content = yaml.safe_load(spec_file)
    return spec_content["info"]["version"]


def minor_bump(version):
    major, minor, patch = version.split(".")
    return major + "." + str(int(minor) + 1) + "." + patch


def major_bump(version):
    major, minor, patch = version.split(".")
    return str(int(major) + 1) + "." + "0" + "." + patch


def is_less_than(version1, version2):
    version1 = version1.replace(".", "")
    version2 = version2.replace(".", "")
    return version1 < version2


def compute_version(intent, latest_release_version, target_branch_version):
    next_version = None
    if intent == "minor":
        next_version = minor_bump(latest_release_version)
    else:
        next_version = major_bump(latest_release_version)
    if is_less_than(next_version, target_branch_version):
        next_version = target_branch_version
    return next_version


def recalculate_version(version_matrix, intent_dic, target_branch):
    for file in intent_dic:
        file_name = file + ".yml"
        latest_release_version = get_version_from_branch("./release", file)
        target_branch_version = get_version_from_branch("./" + target_branch, file)
        new_version = compute_version(
            intent_dic[file], latest_release_version, target_branch_version
        )
        version_matrix["include"].append(
            {"file": file_name, "version": new_version, "branch": target_branch}
        )


def combine_intent(master_intents):
    intent_dic = {}
    for file in master_intents["intent"]:
        if len(master_intents["intent"][file]) != 0:
            intent = "minor"
            for intent_item in master_intents["intent"][file]:
                if intent_item["intent"] == "major":
                    intent = "major"
            intent_dic[file] = intent
    return intent_dic


version_matrix = {"include": []}

remote = get_remote()

master_path = "./master"
clone_repo_master = get_clone_repo(remote, master_path, "master")
master_intents = get_intents(master_path)

dev_path = "./develop"
clone_repo_master = get_clone_repo(remote, dev_path, "develop")
dev_intents = get_intents(dev_path)

release_path = "./release"
release_branches = []
for branch in clone_repo_master.refs:
    if branch.__str__().startswith("origin/production_release"):
        release_branches.append(branch.__str__())
release_branches.sort()
latest_release_branch = release_branches[-1].replace("origin/", "")
clone_repo_release = get_clone_repo(remote, release_path, latest_release_branch)

# Recalculate version on develop branch
intent_dic_dev = combine_intent(dev_intents)
recalculate_version(version_matrix, intent_dic_dev, "develop")


# Recalculate version on master branch
intent_dic_master = combine_intent(master_intents)
recalculate_version(version_matrix, intent_dic_master, "master")

print(json.dumps(version_matrix))
