import os
import json

CONFIG = {}
current_directory = os.path.dirname(__file__)
parent_directory = os.path.split(current_directory)[0]

with open(os.path.join(parent_directory, 'config.json')) as file:
    CONFIG = json.load(file)
