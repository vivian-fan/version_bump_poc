# This script is add intent into intent_management_file
import os
import sys
import shutil
import yaml
import git
import json

# Read intent from intent.yml from feature branch
# Because the intent has been merged from feature branch to target branch
# We can get it from target branch
target_branch = str(sys.argv[1])

target_path = './' + target_branch
if os.path.exists(target_path):
    shutil.rmtree(target_path)
os.mkdir(target_path)

username = "vivian-fan"
password = sys.argv[2]
remote = f"https://{username}:{password}@github.com/vivian-fan/version_bump_poc.git"

clone_repo_target = git.Repo.clone_from(remote, target_path, branch=target_branch)

with open(target_path + '/intent.yml', 'r') as intent_file:
    intent_file_content = yaml.safe_load(intent_file)

# Read intent_list from .github/intent.yml from target branch

with open(target_path + '/.github/intent.yml', 'r') as intent_mgmt_file:
    intent_mgmt_content = yaml.safe_load(intent_mgmt_file)
    
print('debug:', 'intent_file: ', intent_file_content, 'intent_mgmt_file: ', intent_mgmt_content)

# Append intent in intent_list
intent_id = str(sys.argv[3])
for file_key in intent_file_content['intent']:
    intent_mgmt_content['intent'][file_key].append({'id': intent_id, 'intent': intent_file_content['intent'][file_key]})
    
with open(target_path + '/.github/intent.yml', 'w') as intent_mgmt_file:
    intent_mgmt_file.seek(0)
    intent_mgmt_file.write( yaml.dump(intent_mgmt_content, default_flow_style=False))

with open(target_path + '/.github/intent.yml', 'r') as intent_mgmt_file:
    intent_mgmt_content = yaml.safe_load(intent_mgmt_file)
print('debug', 'intent_mgmt_content after add: ', intent_mgmt_content)

# Push back to target branch
try:
    repo = git.Repo(target_path)
    repo.git.add(update=True)
    repo.index.commit('add intent to' + target_branch)
    repo.git.push("origin", target_branch)
except Exception as e:
    print('Errors occured while pushing the code', e) 
