import cgi
import json

from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import ndb
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.appengine.users import admin_required
from PIL import Image
from StringIO import StringIO

from palette import extract_colors
from models import Photo, incr_count, decr_count, range_names, rgb_hls
from palette import rgb_to_hex
from wtforms import Form, fields, validators
from handlers import BaseHandler, csrf_protected, xss_protected, Paginator, EmailField, TagsField
from config import PHOTOS_PER_PAGE, PHOTOS_MAX_PAGE


class Index(BaseHandler):
    @xss_protected
    def get(self, field=None, value=None):
        page = self.request.get('page', None)
        safe_key = self.request.get('safe_key', None)
        query = Photo.query_for(field, value)
        paginator = Paginator(query, per_page=PHOTOS_PER_PAGE)
        objects, token = paginator.page(page)

        if not objects:
            self.abort(404)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'max': PHOTOS_MAX_PAGE,
                'next': token}

        if safe_key is not None:
            data['safe_key'] = safe_key
            self.render_template('photo/detail.html', data)
        else:
            self.render_template('photo/index.html', data)


class Detail(BaseHandler):
    def get(self, safe_key, field=None, value=None):
        key = ndb.Key(urlsafe=safe_key).get()
        query = Photo.query_for(field, value)
        objects = query.filter(Photo._key == key).fetch(1)
        if not objects:
            self.abort(404)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'safe_key': safe_key}
        self.render_template('photo/detail.html', data)


class Palette(BaseHandler):
    """
    Palette(
        colors=[
            Color(value=(211, 73, 74), prominence=0.27075757575757575),
            Color(value=(69, 101, 103), prominence=0.08575757575757575),
            Color(value=(69, 1, 2), prominence=0.06818181818181818),
            Color(value=(88, 57, 60), prominence=0.0353030303030303)],
        bgcolor=
            Color(value=(164, 14, 12), prominence=0.4356060606060606))
    """
    def get(self, safe_key):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)
        img = Image.open(StringIO(obj.buffer))
        img.thumbnail((100, 100), Image.ANTIALIAS)
        palette = extract_colors(img)
        if palette.bgcolor:
            colors = [palette.bgcolor] + palette.colors
        else:
            colors = palette.colors

        data = {'active': {'color': obj.rgb,
                           'hls': rgb_hls(obj.rgb),
                           'hex': obj.hex,
                           'class': obj.color},
                'palette': [
                    {'prominence': '%.1f%%' % (100 * c.prominence,),
                     'color': c.value,
                     'hls': rgb_hls(c.value),
                     'hex': rgb_to_hex(c.value),
                     'class': range_names(c.value)} for c in colors]}

        self.render_json(data)

    def post(self, safe_key):
        def characterise(hue, lum, sat):
            if lum in ('dark', 'light',) or sat == 'monochrome':
                return lum
            else:
                return hue

        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.render_json({'success': False})
        new_rgb = json.loads(self.request.get('rgb'))
        new_range_names = range_names(new_rgb)
        new_color = characterise(*new_range_names)
        if new_rgb != obj.rgb or new_color != obj.color:
            decr_count('Photo', 'color', obj.color)
            obj.rgb = new_rgb
            obj.hue, obj.lum, obj.sat = new_range_names
            obj.put()
            incr_count('Photo', 'color', obj.color)
            self.render_json({
                'success': True,
                'similar_url': self.uri_for('photo_all_filter', field='color', value=obj.color)
            })
        else:
            self.render_json({'success': False})


class AddForm(Form):
    headline = fields.StringField(_('Headline'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    author = EmailField(_('Author'), validators=[validators.DataRequired()])
    photo = fields.FileField(_('Photo'))

    @staticmethod
    def validate_photo(form, field):
        if not isinstance(field.data, cgi.FieldStorage):
            raise validators.ValidationError(_('Nothing to upload.'))


class EditForm(Form):
    headline = fields.StringField(_('Headline'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    author = EmailField(_('Author'), validators=[validators.DataRequired()])
    date = fields.DateTimeField(_('Taken'), validators=[validators.DataRequired()])
    model = fields.StringField(_('Camera model'))
    aperture = fields.FloatField(_('Aperture'), validators=[validators.Optional()])
    shutter = fields.StringField(_('Shutter speed'))
    focal_length = fields.FloatField(_('Focal length'))
    iso = fields.IntegerField('%s (ISO)' % _('Sensitivity'), validators=[validators.Optional()])
    lens = fields.StringField(_('Lens type'))


class Add(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    @admin_required
    def get(self, form=None):
        if form is None:
            form = AddForm(author=self.user)
        self.render_template('admin/photo_form.html', {'form': form, 'filter': None})

    @csrf_protected
    def post(self):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            obj = Photo(headline=form.headline.data)
            response = obj.add(form.data)
            if response['success']:
                self.redirect_to('photo_edit', safe_key=obj.key.urlsafe())
            else:
                form.photo.errors.append(response['message'])
                self.render_template('admin/photo_form.html', {'form': form, 'filter': None})
        else:
            self.render_template('admin/photo_form.html', {'form': form, 'filter': None})


class Edit(BaseHandler):
    @admin_required
    def get(self, safe_key, form=None):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)
        if not any([self.is_admin, self.user == obj.author]):
            self.abort(403)
        if form is None:
            form = EditForm(obj=obj)

        self.render_template('admin/photo_form.html', {
            'form': form, 'object': obj, 'filter': None})

    @csrf_protected
    def post(self, safe_key):
        obj = ndb.Key(urlsafe=safe_key).get()
        form = EditForm(formdata=self.request.POST)
        if form.validate():
            obj.edit(form.data)
            self.redirect_to('photo_admin')
        else:
            self.render_template('admin/photo_form.html', {
                'form': form, 'object': obj, 'filter': None})
