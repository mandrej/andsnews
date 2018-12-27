import datetime

from flask import Flask, abort, jsonify, request, make_response
from google.appengine.ext import ndb, deferred

from views.api import CustomJSONEncoder, SearchPaginator, counters_values, available_filters
from views.config import LIMIT, START_MSG
from views.mapper import push_message, Missing, Indexer, Builder, Unbound
from views.models import Photo, slugify

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder


@app.route('/api/counter/<col>', methods=['GET'])
def collection(col):
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
    objects, _, token, error = paginator.page(page)

    return jsonify({
        'objects': objects,
        'filter': {'field': 'search', 'value': find.strip()},
        '_page': page if page else 'FP',
        '_next': token,
        'error': error
    })


@app.route('/api/message', methods=['POST'])
def notify():
    token = request.json.get('token', None)
    text = request.json.get('text', None)
    push_message(token, text)
    return jsonify(True)


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
    """ ImmutableMultiDict([('photos', <FileStorage: u'selo.jpg' ('image/jpeg')>), ...]) """
    resList = []
    email = request.form.get('email')
    files = request.files.getlist('photos')
    for fs in files:
        obj = Photo(headline=fs.filename, email=email)
        res = obj.add(fs)
        resList.append(res)
    return jsonify(resList)


@app.route('/api/edit/<safe_key>', methods=['PUT'])
def put(safe_key):
    key = ndb.Key(urlsafe=safe_key)
    if key is None:
        abort(404)
    obj = key.get()
    res = obj.edit(request.json)
    return jsonify(res)


@app.route('/api/delete/<safe_key>', methods=['DELETE'])
def delete(safe_key):
    key = ndb.Key(urlsafe=safe_key)
    if key is None:
        abort(404)
    key.get().remove()
    return jsonify(True)


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
