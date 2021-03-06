import os
import sys
import time
import shutil
import yaml
import git
import json
from jsonschema import validate

def get_remote():
    username = "vivian-fan"
    password = "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"
    remote = f"https://{username}:{password}@github.com/clari/clari-apis.git"
    return remote

  
def get_clone_repo(remote, path, branch):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    clone_repo = git.Repo.clone_from(remote, path, branch=branch)
    return clone_repo

  
def get_intent_file(path):
    intent_file = None
    all_files = os.listdir(path)
    for file in all_files:
        if file.endswith("intent.yml"):
            intent_file = file
    return intent_file


def read_intents(path, intent_file):
    with open(path + "/" + intent_file, "r") as intent_content:
        return yaml.safe_load(intent_content)
      
      
feature_branch = str(sys.argv[1])

feature_path = "./" + feature_branch

remote = get_remote()

clone_repo_feature = get_clone_repo(remote, feature_path, feature_branch)

intent_file = get_intent_file(feature_path)
if intent_file == None:
  print(False)
  sys.exit("Cannot find intent file")
  
intent_content = read_intents(feature_path, intent_file)

schema = """
type: object
properties:
  intent:
    type: [array, object]
"""

try:
    validate(intent_content, yaml.safe_load(schema))
except jsonschema.exceptions.ValidationError as error:
    print(False)
    sys.exit("Cannot find intent section")

for file, version in intent_content['intent'].items():
  if version != "major" and version !="minor":
    print(False)
    sys.exit("Cannot read version " + version)
    
print(True)
