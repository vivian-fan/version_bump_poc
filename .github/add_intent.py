# This script is add intent into intent_management_file
import os
import sys
import shutil
import yaml
import git
import json

def get_remote():
    username = "vivian-fan"
    password = sys.argv[2]
    remote = f"https://{username}:{password}@github.com/vivian-fan/version_bump_poc.git"
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
    if len(intent_mgmt_content) == 0:
        intent_mgmt_content['intent'] = []
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

target_branch = str(sys.argv[1])
feature_branch = str(sys.argv[3])

target_path = "./" + target_branch
feature_path = "./" + feature_branch

clone_repo_target = get_clone_repo(remote, target_path, target_branch)
clone_repo_feature = get_clone_repo(remote, feature_path, feature_branch)

intent_file_content = get_intent(feature_path)
intent_mgmt_content = get_intents(target_path)
    
print('debug:', 'intent_file: ', intent_file_content, 'intent_mgmt_file: ', intent_mgmt_content)

# Append intent in intent_list
intent_id = str(sys.argv[3])
for file_key in intent_file_content['intent']:
    intent_mgmt_content['intent'][file_key].append({'id': intent_id, 'intent': intent_file_content['intent'][file_key]})
    
push_to_origin(intent_mgmt_content, target_path, target_branch)
