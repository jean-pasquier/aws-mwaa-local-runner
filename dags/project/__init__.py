import os

this_dir = os.path.dirname(os.path.abspath(__file__))
version_file = 'VERSION'


with open(os.path.join(this_dir, version_file)) as f:
    VERSION = f.read()

