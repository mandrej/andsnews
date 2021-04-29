import os
import json

current_directory = os.path.dirname(__file__)
parent_directory = os.path.split(current_directory)[0]

CONFIG = {}
with open(os.path.join(parent_directory, 'config.json')) as file:
    CONFIG = json.load(file)

CREDENTIALS = {}
with open(os.path.join(parent_directory, 'andsnews-7c373307f6e8.json')) as file:
    CREDENTIALS = json.load(file)
