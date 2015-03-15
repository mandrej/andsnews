import cgi
import json
from collections import defaultdict, OrderedDict

from google.appengine.ext import blobstore
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.appengine.users import login_required

from models import Photo, img_palette, incr_count, decr_count, range_names
from palette import rgb_to_hex
from wtforms import Form, fields, validators
from handlers import BaseHandler, csrf_protected, Paginator, EmailField, TagsField
from config import CROPS, PHOTOS_PER_PAGE


class Index(BaseHandler):
    def get(self, field=None, value=None):
        page = int(self.request.get('page', 1))
        query = Photo.query_for(field, value)
        paginator = Paginator(query, per_page=PHOTOS_PER_PAGE)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('photo/index.html', data)


class Detail(BaseHandler):
    def get(self, field=None, value=None):
        slug = self.request.get('slug', None)
        page = int(self.request.get('page', 1))
        query = Photo.query_for(field, value)
        paginator = Paginator(query, per_page=PHOTOS_PER_PAGE)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'slug': slug,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('photo/detail.html', data)


class Palette(BaseHandler):
    def get(self, slug):
        obj = Photo.get_by_id(slug)
        blob_reader = blobstore.BlobReader(obj.blob_key, buffer_size=1024*1024)
        buff = blob_reader.read()
        palette = img_palette(buff)

        data = {'active': {'color': obj.rgb,
                           'hex': obj.hex,
                           'class': obj.color},
                'palette': [
                    {'prominence': '%.1f%%' % (100 * c.prominence,),
                     'color': c.value,
                     'hex': rgb_to_hex(c.value),
                     'class': range_names(c.value)} for c in palette.colors]}

        if palette.bgcolor:
            data['bgcolor'] = {'prominence': '%.1f%%' % (100 * palette.bgcolor.prominence,),
                               'color': palette.bgcolor.value,
                               'hex': rgb_to_hex(palette.bgcolor.value),
                               'class': range_names(palette.bgcolor.value)}

        self.render_json(data)

    def post(self, slug):
        def characterise(hue, lum, sat):
            if lum in ('dark', 'light',) or sat == 'monochrome':
                return lum
            else:
                return hue

        obj = Photo.get_by_id(slug)
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
                'similar_url': self.uri_for('photo_all_filter', page=1, field='color', value=obj.color)
            })
        else:
            self.render_json({'success': False})


class AddForm(Form):
    headline = fields.StringField(_('Headline'), validators=[validators.DataRequired()])
    slug = fields.StringField(_('Slug'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    photo = fields.FileField(_('Photo'))

    def validate_slug(self, field):
        if Photo.get_by_id(field.data):
            raise validators.ValidationError(_('Record with this slug already exist'))

    def validate_photo(self, field):
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
    crop_factor = fields.FloatField(_('Crop factor'))
    lens = fields.StringField(_('Lens type'))


class Add(BaseHandler):
    @login_required
    def get(self, form=None):
        upload_url = blobstore.create_upload_url(self.uri_for('photo_add'))
        if form is None:
            form = AddForm()
        self.render_template('admin/photo_form.html', {'form': form, 'upload_url': upload_url, 'filter': None})

    @csrf_protected
    def post(self):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            obj = Photo(id=form.slug.data)
            obj.add(form.data)
            self.redirect_to('photo_edit', slug=obj.key.string_id())
        else:
            upload_url = blobstore.create_upload_url(self.uri_for('photo_add'))
            self.render_template('admin/photo_form.html', {'form': form, 'upload_url': upload_url, 'filter': None})


def crop_dict():
    v = defaultdict(list)
    for key, value in sorted(CROPS.iteritems()):
        v[value].append(key)
    return OrderedDict(sorted(v.items()))


class Edit(BaseHandler):
    @login_required
    def get(self, slug, form=None):
        obj = Photo.get_by_id(slug)
        if not any([self.is_admin, self.user == obj.author]):
            self.abort(403)
        if form is None:
            form = EditForm(obj=obj)
            if obj.model and obj.focal_length:
                try:
                    form.crop_factor.data = CROPS[obj.model]
                except KeyError:
                    form.crop_factor.data = 1.6

        self.render_template('admin/photo_form.html', {
            'form': form, 'object': obj, 'filter': None, 'crops': crop_dict()})

    @csrf_protected
    def post(self, slug):
        obj = Photo.get_by_id(slug)
        form = EditForm(formdata=self.request.POST)
        if form.validate():
            obj.edit(form.data)
            self.redirect_to('photo_admin', page=1)
        else:
            self.render_template('admin/photo_form.html', {
                'form': form, 'object': obj, 'filter': None, 'crops': crop_dict()})