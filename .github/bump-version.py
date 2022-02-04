import os
import sys
import shutil
import yaml
import git
from json.decoder import JSONDecodeError

def get_intents():
    with open('intent.yml', 'r') as stream:
        return yaml.safe_load(stream)

def get_version_from_branch(branch_name, spec_file_name):
    spec_content = {}
    with open(branch_name + '/' + spec_file_name, 'r') as spec_content:
        spec_content = yaml.safe_load(spec_content)
    return spec_content['info']['version']

def minor_bump(version):
    major, minor, patch = version.split('.')
    return major + '.' + str(int(minor) + 1) + '.' + patch
    
def major_bump(version):
    major, minor, patch = version.split('.')
    return str(int(major) + 1) + '.' + '0' + '.' + patch

def is_less_than(version1, version2):
    version1 = version1.replace('.', '')
    version2 = version2.replace('.', '')
    return version1 < version2

def compute_version(intent, latest_release_version, target_branch_version):
    next_version = None
    if intent == 'minor':
        next_version = minor_bump(latest_release_version) 
    else:
        next_version = major_bump(latest_release_version)
    if is_less_than(next_version, target_branch_version):
        next_version = target_branch_version
    return next_version
    
# Get target_branch and release branch version
target_branch = str(sys.argv[1])

release_path = './release'
target_path = './' + target_branch

if os.path.exists(release_path):
    shutil.rmtree(release_path)

if os.path.exists(target_path):
    shutil.rmtree(target_path)

os.mkdir(release_path)
os.mkdir(target_path)

clone_repo_target = None
clone_repo_release = None

clone_repo_target = git.Repo.clone_from('https://github.com/vivian-fan/version_bump_poc.git', target_path, branch=target_branch)

release_branches = []

for branch in clone_repo_target.refs:
    if branch.__str__().startswith('origin/production_release'):
        release_branches.append(branch.__str__())
release_branches.sort()
latest_release_branch = release_branches[-1].replace('origin/', '')
clone_repo_release = git.Repo.clone_from('https://github.com/vivian-fan/version_bump_poc.git', release_path, branch=latest_release_branch)

# Do a loop to calculate version for each root yaml file
intents = get_intents()

# intent_list = {'include': []}
# intent_list = []
intent_list = ""

for file_name, intent in intents['intent'].items():
  file = file_name + '.yml'
  latest_release_version = get_version_from_branch('./release', file)
  target_branch_version = get_version_from_branch('./' + target_branch, file)
  next_version = compute_version(intent, latest_release_version, target_branch_version)
  intent_list += (";" + file + "," + next_version)
#   intent_list['include'].append({"file": file, "version": next_version})
#   intent_list.append([file, next_version])
  
shutil.rmtree(release_path)
shutil.rmtree(target_path)

print(intent_list)
