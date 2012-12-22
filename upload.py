import webapp2
from google.appengine.ext.webapp import blobstore_handlers

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    # 2 step
    def post(self):
        upload_files = self.get_uploads('photo')
        blob_info = upload_files[0]
        self.redirect('/photos/%s/bind' % blob_info.key())

app = webapp2.WSGIApplication([
    ('/upload', UploadHandler),
#    ('/serve/([^/]+)?', ServeHandler)
    ], debug=True)