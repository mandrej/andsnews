import cgi
import json
from google.appengine.ext import blobstore
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.appengine.users import login_required
from models import Photo, img_palette, incr_count, decr_count, range_names
from lib import colorific
from wtforms import Form, fields, validators
from handlers import BaseHandler, csrf_protected, Paginator, Filter, EmailField, TagsField, touch_appcache


class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
        query = Photo.query(*filters).order(-Photo.date)

        page = int(self.request.get('page', 1))
        paginator = Paginator(query)
        objects, has_next = paginator.page(page)

        if field and value:
            base_url = self.uri_for('photo_filter_all', field=field, value=value)
        else:
            base_url = self.uri_for('photo_all')

        data = {'previous_url': '%s?page=%s' % (base_url, (page - 1)) if page > 1 else None,
                'current_url': '%s?page=%s' % (base_url, page),
                'next_url': '%s?page=%s' % (base_url, (page + 1)) if has_next else None,
                'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page}
        if self.request.headers.get('X-Requested-With', '') == 'XMLHttpRequest':
            if objects:
                self.render_template('photo/index_page.html', data)
            else:
                self.abort(404)
        else:
            self.render_template('photo/index.html', data)


class Detail(BaseHandler):
    def get(self, slug, field=None, value=None):
        f = Filter(field, value)
        filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
        query = Photo.query(*filters).order(-Photo.date)

        paginator = Paginator(query)
        page, previous, obj, next = paginator.triple(slug)
        if field and value:
            previous_url = self.uri_for('photo_filter', field=field, value=value, slug=previous.key.string_id()) if previous else None
            current_url = self.uri_for('photo_filter', field=field, value=value, slug=obj.key.string_id())
            next_url = self.uri_for('photo_filter', field=field, value=value, slug=next.key.string_id()) if next else None
        else:
            previous_url = self.uri_for('photo', slug=previous.key.string_id()) if previous else None
            current_url = self.uri_for('photo', slug=obj.key.string_id())
            next_url = self.uri_for('photo', slug=next.key.string_id()) if next else None

        data = {'previous_url': previous_url,
                'current_url': current_url,
                'next_url': next_url,
                'object': obj,
                'filter': {'field': field, 'value': value} if field and value else None,
                'page': page}
        if self.request.headers.get('X-Requested-With', '') == 'XMLHttpRequest':
            if obj:
                self.render_template('photo/detail_page.html', data)
            else:
                self.abort(404)
        else:
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


class Edit(BaseHandler):
    @login_required
    def get(self, slug, form=None):
        obj = Photo.get_by_id(slug)
        if not any([self.is_admin, self.user == obj.author]):
            self.abort(403)
        if form is None:
            form = EditForm(obj=obj)
        self.render_template('admin/photo_form.html', {'form': form, 'object': obj, 'filter': None})

    @csrf_protected
    @touch_appcache
    def post(self, slug):
        obj = Photo.get_by_id(slug)
        form = EditForm(formdata=self.request.POST)
        if form.validate():
            obj.edit(form.data)
            self.redirect_to('photo_admin')
        else:
            self.render_template('admin/photo_form.html', {'form': form, 'object': obj, 'filter': None})