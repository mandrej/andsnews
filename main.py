import datetime
import logging

from flask import Flask, abort, jsonify, request, make_response
from flask.json import JSONEncoder

from google.appengine.api import users
from google.appengine.ext import ndb, deferred
from views.api import SearchPaginator, counters_values, available_filters
from views.config import START_MSG
from views.models import Photo, slugify
from views.mapper import push_message, Missing, Indexer, Builder, Unbound

LIMIT = 24


class CustomJSONEncoder(JSONEncoder):
    """ json mapper helper """
    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, ndb.Model):
            return obj.serialize()
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, users.User):
            return obj.email()
        return JSONEncoder.default(self, obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder


@app.route('/api/counter/<col>', methods=['GET'])
def counters(col):
    if col == 'values':
        return jsonify(counters_values())
    elif col == 'filters':
        return jsonify({
            'count': Photo.query().count(),
            'filters': available_filters()
        })


@app.route('/api/search/<find>', methods=['GET'])
def search(find):
    page = request.args.get('_page', None)
    per_page = int(request.args.get('per_page', LIMIT))
    paginator = SearchPaginator(find, per_page=per_page)
    objects, number_found, token, error = paginator.page(page)

    return jsonify({
        'objects': objects,
        'filter': {'field': 'search', 'value': find.strip()},
        # 'number_found': number_found,
        '_page': page if page else 'FP',
        '_next': token,
        'error': error
    })


@app.route('/api/message', methods=['POST'])
def notify():
    token = request.json.get('token', None)
    text = request.json.get('text', None)
    push_message(token, text)


@app.route('/api/<verb>/<field>', methods=['POST'])
def background_runner(verb, field=None):
    token = request.json.get('token', None)
    assert token is not None, 'Token cannot be null'

    if field and verb == 'rebuild':
        runner = Builder()
        runner.VALUES = []
        runner.FIELD = field
    else:
        if verb == 'reindex':
            runner = Indexer()
        elif verb == 'unbound':
            runner = Unbound()
        elif verb == 'missing':
            runner = Missing()

    runner.KIND = Photo
    runner.TOKEN = token
    push_message(runner.TOKEN, START_MSG)
    deferred.defer(runner.run, _queue='background')
    return jsonify(True)


@app.route('/api/add', methods=['POST'])
def post():
    resList = []
    email = request.form.get('email')
    files = request.files.getlist['photos']
    # ImmutableMultiDict([('photos', <FileStorage: u'selo.jpg' ('image/jpeg')>), ('photos', <FileStorage: u'brdo.jpg' ('image/jpeg')>)])
    for fs in files:
        obj = Photo(headline=fs.filename, email=email)
        res = obj.add(fs)
        resList.append(res)
    return jsonify(resList)


@app.route('/api/edit/<safe_key>', methods=['PUT'])
def put(safe_key=None):
    key = ndb.Key(urlsafe=safe_key)
    if key is None:
        abort(404)
    obj = key.get()

    data = request.json
    # fix tags
    if 'tags' in data:
        tags = data['tags']
    else:
        tags = []

    data['tags'] = sorted(tags)
    # fix author
    if 'author' in data:
        email = data['author']
        data['author'] = users.User(email=email)

    # fix empty values
    values = map(lambda x: x if x != '' else None, data.values())
    data = dict(zip(data.keys(), values))
    # fix date
    dt = data['date'].strip().split('.')[0]  # no millis
    data['date'] = datetime.datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S')

    if data['focal_length']:
        data['focal_length'] = round(float(data['focal_length']), 1)
    if data['aperture']:
        data['aperture'] = float(data['aperture'])
    if data['iso']:
        data['iso'] = int(data['iso'])
    res = obj.edit(data)
    return jsonify(res)


@app.route('/api/delete/<safe_key>', methods=['DELETE'])
def delete(safe_key):
    key = ndb.Key(urlsafe=safe_key)
    if key is None:
        abort(404)
    key.get().remove()


@app.route('/api/download/<safe_key>', methods=['GET'])
def download(safe_key):
    key = ndb.Key(urlsafe=safe_key)
    if key is None:
        abort(404)
    obj = key.get()
    response = make_response(obj.buffer)
    response.headers['Content-Type'] = 'image/jpeg'
    response.headers['Content-Disposition'] = 'attachment; filename=%s.jpg' % str(slugify(obj.headline))
    return response
