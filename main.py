from flask import Flask, abort, jsonify, request, make_response
from werkzeug.http import generate_etag
from io import BytesIO
from PIL import Image
from api import cloud, photo
from api.helpers import push_message
from api.config import CONFIG

app = Flask(__name__)


@app.route('/api/thumb/<filename>', methods=['GET'])
def thumb(filename):
    inp = BytesIO()
    out = BytesIO()
    size = int(request.args.get('size', 0))
    assert size > 0

    blob = photo.storage_blob(filename)
    if blob:
        blob.download_to_file(inp)
        image_from_buffer = Image.open(inp)
        image_from_buffer.thumbnail((size, size), Image.BICUBIC)
        image_from_buffer.save(out, image_from_buffer.format)
        data = out.getvalue()

        response = make_response(data)
        response.headers['Content-Type'] = blob.content_type
        response.headers['Cache-Control'] = CONFIG['cache_control']
        response.headers['E-Tag'] = generate_etag(data)
        return response
    abort(404, description='Resource not found')


@app.route('/api/download/<filename>', methods=['GET'])
def download(filename):
    inp = BytesIO()

    blob = photo.storage_blob(filename)
    if blob:
        blob.download_to_file(inp)
        data = inp.getvalue()

        response = make_response(data)
        response.headers['Content-Type'] = blob.content_type
        response.headers['Content-Disposition'] = 'attachment; filename='.format(
            filename)
        return response
    abort(404, description='Resource not found')


@app.route('/api/counters', methods=['GET'])
def collection():
    return jsonify(cloud.counters_stat())


@app.route('/api/search', methods=['GET'])
def search():
    filters = []
    page = request.args.get('_page', None)
    per_page = int(request.args.get('per_page'))
    for key in ('text', 'tags', 'year', 'month', 'model', 'nick'):
        if key == 'year' or key == 'month':
            val = request.args.get(key, None)
            if val:
                filters.append((key, '=', int(val)))
        elif key == 'tags':
            for tag in request.args.getlist('tags'):
                filters.append((key, '=', tag))
        else:
            val = request.args.get(key, None)
            if val:
                filters.append((key, '=', val))

    objects, token, error = cloud.results(filters, page, per_page)
    return jsonify({
        'objects': objects,
        '_page': page if page else 'FP',
        '_next': token,
        'error': error
    })


@app.route('/api/user', methods=['POST'])
def user():
    data = request.json.get('user', None)
    uid = cloud.login_user(data)
    return jsonify({"uid": uid})


@app.route('/api/user/register', methods=['PUT'])
def update_user():
    uid = request.json.get('uid', None)
    token = request.json.get('token', None)
    changed = cloud.register_user(uid, token)
    return jsonify({"changed": changed})


@app.route('/api/registrations', methods=['GET'])
def registrations():
    return jsonify(cloud.registrations())


@app.route('/api/add', methods=['POST'])
def post():
    """ ImmutableMultiDict([('photos', <FileStorage: u'selo.jpg' ('image/jpeg')>), ...]) """
    resList = []
    email = request.form.get('email')
    files = request.files.getlist('photos')
    for fs in files:
        response = photo.add(fs, email)
        resList.append(response)
    return jsonify(resList)


@app.route('/api/edit/<int:id>', methods=['PUT'])
def put(id):
    response = photo.edit(id, request.json)
    return jsonify(response)


@app.route('/api/delete/<int:id>', methods=['DELETE'])
def delete(id):
    response = photo.remove(id)
    return jsonify(response['success'])


@app.route('/api/message', methods=['POST'])
def notify():
    token = request.json.get('token', None)
    text = request.json.get('text', None)
    success = push_message(token, text)
    return jsonify(success)


@app.route('/api/<verb>', methods=['POST'])
def runner(verb):
    token = request.json.get('token', None)
    assert token is not None, 'Token cannot be null'

    if verb == 'fix':
        runner = cloud.Fixer()
    # elif verb == 'unbound':
    #     runner = Unbound()
    # elif verb == 'missing':
    #     runner = Missing()
    else:
        return jsonify(False)

    runner.TOKEN = token
    runner.run()
    return jsonify(True)


@app.route('/api/<verb>/<field>', methods=['POST'])
def rebuilder(verb, field):
    token = request.json.get('token', None)
    assert token is not None, 'Token cannot be null'
    if field and verb == 'rebuild':
        tally = cloud.rebuilder(field, token)
        return jsonify(tally)
    else:
        return jsonify(False)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=6060, debug=True)
