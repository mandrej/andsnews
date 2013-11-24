import cgi
import json

import webapp2
from google.appengine.api import users
from google.appengine.ext import blobstore
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.appengine.users import login_required
from models import Photo, img_palette, incr_count, decr_count, range_names
from lib import colorific
from wtforms import Form, fields, validators
from handlers import BaseHandler
from common import Paginator, Filter, EmailField, TagsField


class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
        query = Photo.query(*filters).order(-Photo.date)

        page = int(self.request.get('page', 1))
        paginator = Paginator(query)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'idx': (page - 1) * paginator.per_page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('photo/index.html', data)


class Detail(BaseHandler):
    def get(self, slug, field=None, value=None):
        f = Filter(field, value)
        filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
        query = Photo.query(*filters).order(-Photo.date)
        paginator = Paginator(query)
        page, prev, obj, next = paginator.triple(slug)

        data = {'object': obj,
                'next': next,
                'previous': prev,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page}
        self.render_template('photo/detail.html', data)


class Palette(BaseHandler):
    def get(self, slug):
        obj = Photo.get_by_id(slug)
        buf = blobstore.BlobReader(obj.blob_key).read()
        palette = img_palette(buf)

        data = {'active': {'color': obj.rgb,
                           'hex': obj.hex,
                           'class': obj.color},
                'palette': [
                    {'prominence': '%.1f%%' % (100 * c.prominence,),
                     'color': c.value,
                     'hex': colorific.rgb_to_hex(c.value),
                     'class': range_names(c.value)} for c in palette.colors]}

        if palette.bgcolor:
            data['bgcolor'] = {'prominence': '%.1f%%' % (100 * palette.bgcolor.prominence,),
                               'color': palette.bgcolor.value,
                               'hex': colorific.rgb_to_hex(palette.bgcolor.value),
                               'class': range_names(palette.bgcolor.value)}

        self.render_json(data)

    def post(self, slug):
        obj = Photo.get_by_id(slug)
        new_rgb = json.loads(self.request.get('rgb'))
        if new_rgb != obj.rgb:
            decr_count('Photo', 'color', obj.color)
            obj.rgb = new_rgb
            obj.hue, obj.lum, obj.sat = range_names(new_rgb)
            obj.put()
            incr_count('Photo', 'color', obj.color)
            self.render_json({'success': True})
        else:
            self.render_json({'success': False})


class AddForm(Form):
    headline = fields.TextField(_('Headline'), validators=[validators.DataRequired()])
    slug = fields.TextField(_('Slug'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    photo = fields.FileField(_('Photo'))

    def validate_slug(self, field):
        if Photo.get_by_id(field.data):
            raise validators.ValidationError(_('Record with this slug already exist'))

    def validate_photo(self, field):
        if not isinstance(field.data, cgi.FieldStorage):
            raise validators.ValidationError(_('Wrong type.'))


class EditForm(Form):
    headline = fields.TextField(_('Headline'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    author = EmailField(_('Author'), validators=[validators.DataRequired()])
    date = fields.DateTimeField(_('Taken'), validators=[validators.DataRequired()])
    model = fields.TextField(_('Camera model'))
    aperture = fields.FloatField(_('Aperture'))
    shutter = fields.TextField(_('Shutter speed'))
    focal_length = fields.FloatField(_('Focal length'))
    iso = fields.IntegerField('%s (ISO)' % _('Sensitivity'))
    crop_factor = fields.FloatField(_('Crop factor'))
    lens = fields.TextField(_('Lens type'))


class Add(BaseHandler):
    @login_required
    def get(self, form=None):
        upload_url = blobstore.create_upload_url(webapp2.uri_for('photo_add'))
        if form is None:
            form = AddForm()
        self.render_template('photo/form.html', {'form': form, 'upload_url': upload_url, 'filter': None})

    def post(self):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            obj = Photo(id=form.slug.data)
            obj.add(form.data)
            self.redirect_to('photo_edit', slug=obj.key.string_id())
        else:
            upload_url = blobstore.create_upload_url(webapp2.uri_for('photo_add'))
            self.render_template('photo/form.html', {'form': form, 'upload_url': upload_url, 'filter': None})


class Edit(BaseHandler):
    @login_required
    def get(self, slug, form=None):
        obj = Photo.get_by_id(slug)
        user = users.get_current_user()
        is_admin = users.is_current_user_admin()
        if not is_admin:
            if user != obj.author:
                self.abort(403)
        if form is None:
            form = EditForm(obj=obj)
        self.render_template('photo/form.html', {'form': form, 'object': obj, 'filter': None})

    def post(self, slug):
        obj = Photo.get_by_id(slug)
        form = EditForm(formdata=self.request.POST)
        if form.validate():
            obj.edit(form.data)
            self.redirect_to('photo_all')
        else:
            self.render_template('photo/form.html', {'form': form, 'object': obj, 'filter': None})