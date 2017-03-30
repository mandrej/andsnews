import webapp2


class WarmUp(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('successful')

app = webapp2.WSGIApplication([
    ('/_ah/warmup', WarmUp),
])
