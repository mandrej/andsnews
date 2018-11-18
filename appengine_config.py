import sys

for path in ['lib']:
    if path not in sys.path:
        sys.path[0:0] = [path]
