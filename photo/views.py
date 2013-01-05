import cgi
import datetime
import webapp2
from google.appengine.api import users
from google.appengine.ext import ndb, blobstore
#from django.contrib.admin.widgets import AdminSplitDateTime
from webapp2_extras.i18n import lazy_gettext as _
from models import Photo
from wtforms import Form, TextField, SelectField, FileField, DateTimeField, IntegerField, DecimalField, SubmitField, validators
from common import TIMEOUT, BaseHandler, Paginator, Filter, make_thumbnail
from settings import FAMILY
import logging

class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
        query = Photo.query(*filters).order(-Photo.date)

        page = int(self.request.GET.get('page', 1))
        paginator = Paginator(query)
        objects, has_next = paginator.page(page)

        data = {'kind': 'Photo',
                'objects': objects,
                'filter': f.parameters,
                'filter_url': f.url,
                'filter_title': f.title,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('photo/index.html', data)

class Detail(BaseHandler):
    def get(self, slug, field=None, value=None):
        if 'page' not in self.request.GET or 'pic' not in self.request.GET:
            obj = Photo.get_by_id(slug)
            if obj is None:
                webapp2.abort(404)
            self.render_template('photo/detail.html',
                {'object': obj, 'next': None, 'previous': None, 'page': 0, 'filter': None}) # TODO remove double image

        f = Filter(field, value)
        filters = [Photo._properties[k] == v for k, v in f.parameters.items()]
        query = Photo.query(*filters).order(-Photo.date)

        page = int(self.request.GET.get('page', 1))
        pic = int(self.request.GET.get('pic', 1))
        paginator = Paginator(query)
        previous, obj, next, numbers = paginator.triple(page, pic)

        data = {'object': obj,
                'next': next,
                'previous': previous,
                'filter': f.parameters,
                'filter_url': f.url,
                'filter_title': f.title,
                'page': page,
                'num': (page - 1)*paginator.per_page + pic,
                'numbers': numbers}
        self.render_template('photo/detail.html', data)

class EmailField(SelectField):
    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(*args, **kwargs)
        user = users.get_current_user()
        email = user.email()
        if not email in FAMILY:
            FAMILY.append(email)
        self.choices = [(x, x) for x in FAMILY]

class AddForm(Form):
    headline = TextField(_('Headline'), validators=[validators.DataRequired()])
    slug = TextField(_('Slug'), validators=[validators.DataRequired()])
    tags = TextField(_('Tags'), description='Comma separated values')
    author = EmailField(_('Author'), validators=[validators.DataRequired()])
    photo = FileField(_('Photo'))

    def validate_slug(self, field):
        if Photo.get_by_id(field.data):
            raise validators.ValidationError(_('Record with this slug already exist'))

    def validate_photo(self, field):
        if not isinstance(field.data, cgi.FieldStorage):
            raise validators.ValidationError(_('This field is required.'))

class EditForm(Form):
    headline = TextField(_('Headline'), validators=[validators.DataRequired()])
    slug = TextField(_('Slug'), validators=[validators.DataRequired()])
    tags = TextField(_('Tags'), description='Comma separated values')
    author = EmailField(_('Author'), validators=[validators.DataRequired()])
    date = DateTimeField(_('Taken'), validators=[validators.DataRequired()])
    model = TextField(_('Camera model'))
    aperture = DecimalField(_('Aperture'), places=1, rounding=True)
    shutter = TextField(_('Shutter speed'))
    focal_length = IntegerField(_('Focal length'))
    iso = IntegerField('%s (ISO)' % _('Sensitivity'))
    crop_factor = DecimalField(_('Crop factor'), places=1, rounding=True)
    lens = TextField(_('Lens type'))

class Add(BaseHandler):
    #@login_required
    def get(self, form=None):
        upload_url = blobstore.create_upload_url('/photos/add')
        if form is None:
            form = AddForm()
        self.render_template('photo/form.html', {'form': form, 'upload_url': upload_url, 'filter': None})

    def post(self):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            logging.error(form.data)
            obj = Photo(id=form.slug.data)
            obj.add(form.data)
            self.redirect('%s/edit' % obj.get_absolute_url())
        else:
            upload_url = blobstore.create_upload_url('/photos/add')
            self.render_template('photo/form.html', {'form': form, 'upload_url': upload_url, 'filter': None})

class Edit(BaseHandler):
    #@login_required
    def get(self, slug, form=None):
        obj = Photo.get_by_id(slug)
        user = users.get_current_user()
        is_admin = users.is_current_user_admin()
        if not is_admin:
            if user != obj.author:
                webapp2.abort(403)
        if form is None:
            form = EditForm(obj=obj)
            form.populate_obj({
                'headline': obj.headline,
                'slug': obj.key.string_id(),
                'tags': ', '.join(obj.tags),
                'author': user.email,
                'model': obj.model,
                'aperture': obj.aperture,
                'shutter': obj.shutter,
                'focal_length': obj.focal_length,
                'iso': obj.iso,
                'date': obj.date or datetime.datetime.now(),
                'crop_factor': obj.crop_factor,
                'lens': obj.lens
            })
        self.render_template('photo/form.html', {'form': form, 'object': obj, 'filter': None})

    def post(self, slug):
        obj = Photo.get_by_id(slug)
        form = EditForm(formdata=self.request.POST)
        if form.validate():
            obj.edit(form.data)
            self.redirect('/photos')
        else:
            self.render_template('photo/form.html', {'form': form, 'object': obj, 'filter': None})

def thumb(request, slug, size):
    out, mime = make_thumbnail('Photo', slug, size)
    if out:
        response = webapp2.Response(content_type=mime)
        response.headers['Cache-Control'] = 'public, max-age=%s' % (TIMEOUT*600)
        if size == 'normal':
            response.headers['Content-Disposition'] = 'inline; filename=%s' % slug
        response.out.write(out)
        return response
    else:
        webapp2.abort(503)