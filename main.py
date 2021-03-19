from flask import Flask, abort, jsonify, request, make_response
from werkzeug.http import generate_etag
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from api import cloud, photo
from api.helpers import get_exif
from api.config import CONFIG

app = Flask(__name__)


@app.route('/api/<verb>/bucket_info', methods=['GET', 'PUT'])
def bucket_info(verb):
    """
    verb: get|add|del|set
    """
    if request.method == 'GET':
        param = {'verb': verb}  # get|set
    else:
        param = request.json
    return jsonify(cloud.bucketInfo(param))


@app.route('/api/thumb/<filename>', methods=['GET'])
def thumb(filename):
    inp = BytesIO()
    out = BytesIO()
    size = int(request.args.get('size', 0))
    assert size > 0

    blob = photo.storage_blob(filename)
    if blob:
        blob.download_to_file(inp)
        try:
            image_from_buffer = Image.open(inp)
        except UnidentifiedImageError as e:
            return ('', 204)
        else:
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
        response.headers['Content-Disposition'] = f'attachment; filename={filename}'
        return response
    abort(404, description='Resource not found')


@app.route('/api/exif/<filename>', methods=['GET'])
def exif(filename):
    inp = BytesIO()

    blob = photo.storage_blob(filename)
    if blob:
        blob.download_to_file(inp)
        _buffer = inp.getvalue()
        out = get_exif(_buffer)
        out['date'] = out['date'].strftime(CONFIG['date_time_format'])
        if out.get('dim', None) is None:
            image_from_buffer = Image.open(BytesIO(_buffer))
            out['dim'] = list(image_from_buffer.size)

        return out

    abort(404, description='Resource not found')


@app.route('/api/counters', methods=['GET'])
def collection():
    return jsonify(photo.counters_stat())


@app.route('/api/search', methods=['GET'])
def search():
    filters = []
    page = request.args.get('_page', None)
    per_page = int(request.args.get('per_page'))
    for key in ('text', 'tags', 'year', 'month', 'model', 'lens', 'nick'):
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

    objects, token, error = photo.results(filters, page, per_page)
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
def add():
    """ ImmutableMultiDict([('photos', <FileStorage: u'selo.jpg' ('image/jpeg')>), ...]) """
    resList = []
    files = request.files.getlist('photos')
    for fs in files:
        response = photo.add(fs)
        resList.append(response)
    return jsonify(resList)


@app.route('/api/edit', defaults={'id': None}, methods=['PUT'])
@app.route('/api/edit/<int:id>', methods=['PUT'])
def edit(id):
    response = photo.edit(id, request.json)
    return jsonify(response)


@app.route('/api/remove/<filename>', methods=['DELETE'])
def remove(filename):
    """ Remove unpublished photo """
    response = photo.removeFromBucket(filename)
    return jsonify(response)


@app.route('/api/delete/<int:id>', methods=['DELETE'])
def delete(id):
    response = photo.remove(id)
    return jsonify(response['success'])


@app.route('/api/<verb>', methods=['POST'])
def runner(verb):
    token = request.json.get('token', None)
    assert token is not None, 'Token cannot be null'

    if verb == 'fix':
        runner = cloud.Fixer()
    elif verb == 'repair':
        runner = cloud.Repair()
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
