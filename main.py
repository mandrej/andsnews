from flask import Flask, abort, jsonify, request, make_response
from google.appengine.ext import ndb, deferred

from views.api import CustomJSONEncoder, Paginator, counters_values, available_filters
from views.config import LIMIT, START_MSG
from views.mapper import push_message, Missing, Builder, Unbound, Fixer
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


@app.route('/api/search', methods=['GET'])
def search():
    page = request.args.get('_page', None)
    per_page = int(request.args.get('per_page', LIMIT))
    query = Photo.query()

    for key in ('text', 'tags', 'year', 'month', 'model', 'nick'):
        if key == 'year' or key == 'month':
            val = request.args.get(key, None)
            if val:
                query = query.filter(Photo._properties[key] == int(val))
        elif key == 'tags':
            for tag in request.args.getlist('tags'):
                query = query.filter(Photo._properties[key] == tag)
        else:
            val = request.args.get(key, None)
            if val:
                query = query.filter(Photo._properties[key] == val)

    query = query.order(-Photo.date)
    paginator = Paginator(query, per_page=per_page)
    objects, token, error = paginator.page(page)

    return jsonify({
        'objects': objects,
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


@app.route('/api/<verb>', methods=['POST'])
def background_runner(verb):
    token = request.json.get('token', None)
    assert token is not None, 'Token cannot be null'

    if verb == 'unbound':
        runner = Unbound()
    elif verb == 'missing':
        runner = Missing()
    elif verb == 'fix':
        runner = Fixer()
    else:
        return jsonify(False)

    runner.KIND = Photo
    runner.TOKEN = token
    push_message(runner.TOKEN, START_MSG)
    deferred.defer(runner.run, _queue='background')
    return jsonify(True)


@app.route('/api/<verb>/<field>', methods=['POST'])
def background_build(verb, field):
    token = request.json.get('token', None)
    assert token is not None, 'Token cannot be null'

    if field and verb == 'rebuild':
        runner = Builder()
        runner.VALUES = []
        runner.FIELD = field
    else:
        return jsonify(False)

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
        response = obj.add(fs)
        resList.append(response)
    return jsonify(resList)


@app.route('/api/edit/<safe_key>', methods=['PUT'])
def put(safe_key):
    key = ndb.Key(urlsafe=safe_key)
    if key is None:
        abort(404)
    obj = key.get()
    response = obj.edit(request.json)
    return jsonify(response)


@app.route('/api/delete/<safe_key>', methods=['DELETE'])
def delete(safe_key):
    key = ndb.Key(urlsafe=safe_key)
    if key is None:
        abort(404)
    response = key.get().remove()
    return jsonify(response['success'])


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
