from io import BytesIO
from flask import Flask, abort, jsonify, request, make_response
from werkzeug.http import generate_etag
from PIL import Image
from api import cloud, photo
from api.helpers import get_exif, latinize, push_message
from api.config import CONFIG

app = Flask(__name__)


@app.route('/_ah/warmup')
def warmup():
    return 'warmup', 200, {}


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
        im = Image.open(inp)

        im.thumbnail((size, size), Image.BICUBIC)
        icc_profile = im.info.get('icc_profile')
        if icc_profile:
            im.save(out, im.format, icc_profile=icc_profile)
        else:
            im.save(out, im.format)

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
        data = inp.getvalue()

        out = get_exif(data)
        out['date'] = out['date'].strftime(CONFIG['date_time_format'])
        if out.get('dim', None) is None:
            image_from_buffer = Image.open(BytesIO(data))
            out['dim'] = list(image_from_buffer.size)
        if out.get('flash', None) is None:
            out['flash'] = False
        return out

    abort(404, description='Resource not found')


@app.route('/api/counters', methods=['GET'])
def collection():
    return jsonify(photo.counters_stat())


@app.route('/api/search', methods=['GET'])
def search():
    page = None
    per_page = None
    filters = []
    # Return an iterator of (key, value) pairs.
    params = request.args.items(multi=True)
    for key, val in params:
        if key in ('_page', 'per_page', 'text', 'tags', 'year', 'month', 'model', 'lens', 'nick') and val:
            if key == '_page':
                page = val
            elif key == 'per_page':
                per_page = int(val)
            elif key == 'year' or key == 'month':
                filters.append((key, '=', int(val)))
            elif key == 'text':
                filters.append((key, '=', latinize(val)))
            else:
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
    json_ = request.get_json(silent=True)
    assert json_ is not None, 'Cannot get user'
    uid = cloud.login_user(json_['user'])
    return jsonify({"uid": uid})


@app.route('/api/user/register', methods=['PUT'])
def update_user():
    json_ = request.get_json(silent=True)
    assert json_ is not None, 'Cannot get token'
    uid = json_['uid']
    token = json_['token']
    changed = cloud.register_user(uid, token)
    return jsonify({"changed": changed})


@app.route('/api/registrations', methods=['GET'])
def registrations():
    return jsonify(cloud.registrations())


@app.route('/api/add', methods=['POST'])
def add():
    """ ImmutableMultiDict([('photos', <FileStorage: u'selo.jpg' ('image/jpeg')>), ...]) """
    response_list = []
    files = request.files.getlist('photos')
    for fs_ in files:
        response = photo.add(fs_)
        response_list.append(response)
    return jsonify(response_list)


@app.route('/api/edit', defaults={'id_': None}, methods=['PUT'])
@app.route('/api/edit/<int:id_>', methods=['PUT'])
def edit(id_):
    response = photo.edit(id_, request.json)
    return jsonify(response)


@app.route('/api/remove/<filename>', methods=['DELETE'])
def remove(filename):
    """ Remove unpublished photo """
    response = photo.remove_from_bucket(filename)
    return jsonify(response)


@app.route('/api/delete/<int:id_>', methods=['DELETE'])
def delete(id_):
    response = photo.remove(id_)
    return jsonify(response['success'])


@app.route('/api/<verb>', methods=['POST'])
def runner(verb):
    json_ = request.get_json(silent=True)
    assert json_ is not None, 'Cannot get token'
    token = json_['token']

    job = None
    if verb == 'fix':
        job = cloud.Fixer()
    elif verb == 'repair':
        job = cloud.Repair()

    if job:
        job.TOKEN = token
        job.run()
        return jsonify(True)
    else:
        return jsonify(False)


@app.route('/api/<verb>/<field>', methods=['POST'])
def rebuilder(verb, field):
    json_ = request.get_json(silent=True)
    assert json_ is not None, 'Cannot get token'
    token = json_['token']
    if field and verb == 'rebuild':
        tally = cloud.rebuilder(field, token)
        return jsonify(tally)
    else:
        return jsonify(False)


@app.route('/api/message/send', methods=['POST'])
def push():
    json_ = request.get_json(silent=True)
    assert json_ is not None, 'Cannot get token'
    token = json_['token']
    message = json_['message']
    return push_message(token, message)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=6060, debug=True)
