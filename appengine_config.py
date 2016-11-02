import os.path


# https://github.com/GoogleCloudPlatform/google-cloud-python/issues/2032#issuecomment-236226525
def patched_expanduser(path):
    return path

os.path.expanduser = patched_expanduser
