import webapp2
from google.appengine.ext import blobstore
from models import Photo
import logging

class UploadHandler(webapp2.RequestHandler):
    def post(self):
        data = dict(self.request.POST)
        blob_info = blobstore.parse_blob_info(data['photo'])
        logging.error(blob_info)
        obj = Photo(id=data['slug'], headline=data['headline'])
        data['blob_key'] = blob_info.key()
        obj.add(data)
        self.redirect_to('/%s/edit' % obj.get_absolute_url())

app = webapp2.WSGIApplication([
    webapp2.Route(r'/upload', handler=UploadHandler),
    ], debug=True)