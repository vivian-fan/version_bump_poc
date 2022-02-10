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

clone_repo_target = git.Repo.clone_from('https://github.com/vivian-fan/version_bump_poc.git', target_path, branch=target_branch)

with open(target_path + '/intent.yml', 'r') as intent_file:
    intent_file_content = yaml.safe_load(intent_file)

# Read intent_list from .github/intent.yml from target branch

with open(target_path + '/.github/intent.yml', 'r') as intent_mgmt_file:
    intent_mgmt_content = yaml.safe_load(intent_mgmt_file)
    
print('debug:', 'intent_file: ', intent_file_content, 'intent_mgmt_file: ', intent_mgmt_content)

# Append intent in intent_list

# Push back to target branch
