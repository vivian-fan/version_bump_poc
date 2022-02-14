# This script is delete intent into intent_management_file
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


def get_intent(path):
    with open(path + "/intent.yml", "r") as intent_file:
        intent_content = yaml.safe_load(intent_file)
    return intent_content


def push_to_origin(intent_mgmt_content, target_path, target_branch):
    with open(target_path + "/.github/intent.yml", "w") as intent_mgmt_file:
        intent_mgmt_file.seek(0)
        intent_mgmt_file.write(yaml.dump(intent_mgmt_content, default_flow_style=False))
    try:
        repo = git.Repo(target_path)
        repo.git.add(update=True)
        repo.index.commit("add intent to " + target_branch)
        repo.git.push("origin", target_branch)
    except Exception as e:
        print("Errors occured while pushing the code", e)


remote = get_remote()
# Clone master branch
# Read intent_list from /.github/intent.yml as master_intents
# master_intents = ???
# delete the intent in the released_intents from master_intents
# Push back to master
master_path = "./master"
clone_repo_master = get_clone_repo(remote, master_path, "master")
master_intents = get_intents(master_path)

# Clone develop branch
# Read intent_list from /.github/intent.yml as dev_intents
# dev_intents = ???
# delete the intent in the released_intents from dev_intents
# Push back to develop
dev_path = "./develop"
clone_repo_master = get_clone_repo(remote, dev_path, "develop")
dev_intents = get_intents(dev_path)

# Clone latest_release branch
# Read intent_list from /.github/intent.yml as released_intents
# released_intents = ???
release_path = "./release"
release_branches = []
for branch in clone_repo_master.refs:
    if branch.__str__().startswith("origin/production_release"):
        release_branches.append(branch.__str__())
release_branches.sort()
latest_release_branch = release_branches[-1].replace("origin/", "")
clone_repo_release = get_clone_repo(remote, release_path, latest_release_branch)
released_intents = get_intents(release_path)

print(
    "Before: ",
    "master:",
    master_intents,
    "develop:",
    dev_intents,
    "released: ",
    released_intents,
)

# If the event is PR merge, add hotfix to release
event = sys.argv[2]
if event == "pull_request":
    print('pull request triggered')
    hotfix_branch = sys.argv[3]
    hotfix_path = "./hotfix"
    clone_repo_hotfix = get_clone_repo(remote, hotfix_path, hotfix_branch)
    hotfix_intent = get_intent(hotfix_path)
    for file in hotfix_intent["intent"]:
        released_intents["intent"][file].append(
            {"id": hotfix_branch, "intent": hotfix_intent["intent"][file]}
        )

# Delete released_intents from master_intents
for file in released_intents['intent']:
    if file in master_intents['intent']:
        for intent_dic in released_intents['intent'][file]:
            if intent_dic in master_intents['intent'][file]:
                master_intents['intent'][file].remove(intent_dic)

push_to_origin(master_intents, master_path, 'master')

# Delete released_intents from dev_intents
for file in released_intents['intent']:
    if file in dev_intents['intent']:
        for intent_dic in released_intents['intent'][file]:
            if intent_dic in dev_intents['intent'][file]:
                print('debug iterate, ', intent_dic, ' will be removed')
                dev_intents['intent'][file].remove(intent_dic)
                
print('debug', dev_intents)

push_to_origin(dev_intents, dev_path, 'develop')

# Delete released_intents from dev_intents
for file in released_intents['intent']:
    released_intents['intent'][file] = []

push_to_origin(released_intents, release_path, latest_release_branch)

print(
    "After: ",
    "master:",
    master_intents,
    "develop:",
    dev_intents,
    "released: ",
    released_intents,
)
