from flask import Flask, abort, jsonify, request, make_response
from werkzeug.http import generate_etag
from io import BytesIO
from PIL import Image
import cloud
import photo
from helpers import slugify, push_message
from config import LIMIT

app = Flask(__name__)


@app.route('/api/thumb/<safekey>', methods=['GET'])
@app.route('/api/thumb/<safekey>/<int:size>', methods=['GET'])
def thumb(safekey, size=None):
    obj, inp = photo.storage_download(safekey)

    image_from_buffer = Image.open(inp)
    if size:
        image_from_buffer.thumbnail((size, size), Image.BICUBIC)

    out = BytesIO()
    image_from_buffer.save(out, image_from_buffer.format)
    data = out.getvalue()

    response = make_response(data)
    response.headers['Content-Type'] = 'image/jpeg'
    response.headers['Cache-Control'] = 'public, max-age=86400, no-transform'
    response.headers['E-Tag'] = generate_etag(data)
    return response


@app.route('/api/download/<safekey>', methods=['GET'])
def download(safekey):
    obj, inp = photo.storage_download(safekey)

    out = BytesIO()
    image_from_buffer = Image.open(inp)
    image_from_buffer.save(out, image_from_buffer.format)
    data = out.getvalue()

    response = make_response(data)
    response.headers['Content-Type'] = 'image/jpeg'
    response.headers['Content-Disposition'] = 'attachment; filename={}.jpg'.format(
        slugify(obj['headline']))
    return response


@app.route('/api/counter/<col>', methods=['GET'])
def collection(col):
    if col == 'values':
        return jsonify(cloud.counters_values())
    elif col == 'total':
        return jsonify(cloud.photo_count())
    elif col == 'last':
        return jsonify(cloud.last_entry())
    elif col == 'stat':
        return jsonify(cloud.counters_counts())


@app.route('/api/search', methods=['GET'])
def search():
    filters = []
    page = request.args.get('_page', None)
    per_page = int(request.args.get('per_page', LIMIT))
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
    cloud.login_user(data)
    return jsonify({"success": True})


@app.route('/api/user/register', methods=['PUT'])
def update_user():
    uid = request.json.get('uid', None)
    token = request.json.get('token', None)
    cloud.register_user(uid, token)
    return jsonify({"success": True})


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


@app.route('/api/edit/<safekey>', methods=['PUT'])
def put(safekey):
    response = photo.edit(safekey, request.json)
    return jsonify(response)


@app.route('/api/delete/<safekey>', methods=['DELETE'])
def delete(safekey):
    response = photo.remove(safekey)
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


@app.route('/api/_ah/warmup')
def warmup():
    return 'warmup', 200, {}


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=6060, debug=True)
