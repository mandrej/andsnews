import os.path


# builtins: - appstats: on
# def webapp_add_wsgi_middleware(app):
#     from google.appengine.ext.appstats import recording
#     app = recording.appstats_wsgi_middleware(app)
#     return app


# https://github.com/GoogleCloudPlatform/google-cloud-python/issues/2032#issuecomment-236226525
def patched_expanduser(path):
    return path

os.path.expanduser = patched_expanduser
