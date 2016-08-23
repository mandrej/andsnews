from __future__ import division
from StringIO import StringIO

import re
from PIL import Image
import webapp2
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.appengine.users import admin_required
from google.appengine.ext import ndb

from wtforms import Form, FormField, FieldList, fields, validators
from models import Entry, ENTRY_IMAGES
from handlers import BaseHandler, csrf_protected, xss_protected, Paginator, TagsField
from config import TIMEOUT, ENTRIES_PER_PAGE

SMALL = 60, 60


class Index(BaseHandler):
    @xss_protected
    def get(self, field=None, value=None):
        page = self.request.get('page', None)
        query = Entry.query_for(field, value)
        paginator = Paginator(query, per_page=ENTRIES_PER_PAGE)
        objects, token = paginator.page(page)

        data = {'objects': objects,
                'filter': {'field': field, 'value': value} if (field and value) else None,
                'page': page,
                'next': token}
        self.render_template('entry/index.html', data)


class Detail(BaseHandler):
    def get(self, safe_key):
        obj = ndb.Key(urlsafe=safe_key).get()
        if obj is None:
            self.abort(404)
        self.render_template('entry/detail.html', {'object': obj, 'filter': None})


class RequiredIf(validators.DataRequired):
    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(RequiredIf, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if other_field is None:
            raise Exception(_('This field is required if other "%s" present.') % self.other_field_name)
        if bool(other_field.data):
            super(RequiredIf, self).__call__(form, field)


class ImgAddForm(Form):
    name = fields.StringField(_('New Image'))
    #    blob = fields.FileField(validators=[RequiredIf('name')])
    blob = fields.FileField()


class ImgEditForm(Form):
    name = fields.StringField(_('Image'))
    num = fields.IntegerField()
    delete = fields.BooleanField(_('remove'))


class AddForm(Form):
    headline = fields.StringField(_('Headline'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    author = fields.StringField(_('Author'), validators=[validators.DataRequired()])
    summary = fields.TextAreaField(_('Summary'), validators=[validators.DataRequired()])
    date = fields.DateTimeField(_('Posted'), validators=[validators.DataRequired()])
    body = fields.TextAreaField(_('Article'), validators=[validators.DataRequired()])


class EditForm(Form):
    headline = fields.StringField(_('Headline'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    author = fields.StringField(_('Author'), validators=[validators.DataRequired()])
    summary = fields.TextAreaField(_('Summary'), validators=[validators.DataRequired()])
    date = fields.DateTimeField(_('Posted'), validators=[validators.DataRequired()])
    body = fields.TextAreaField(_('Article'), validators=[validators.DataRequired()])


class Add(BaseHandler):
    @admin_required
    def get(self, form=None):
        if form is None:
            form = AddForm()
        self.render_template('admin/entry_form.html', {'form': form, 'object': None, 'filter': None})

    @csrf_protected
    def post(self):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            obj = Entry(headline=form.headline.data)
            obj.add(form.data)
            self.redirect_to('entry_admin')
        else:
            self.render_template('admin/entry_form.html', {'form': form, 'object': None, 'filter': None})


class Edit(BaseHandler):
    @admin_required
    def get(self, safe_key, form=None):
        obj = ndb.Key(urlsafe=safe_key).get()
        if not any([self.is_admin, self.user == obj.author]):
            self.abort(403)
        if form is None:
            form = EditForm(obj=obj)
        self.render_template('admin/entry_form.html', {'form': form, 'object': obj, 'filter': None})

    @csrf_protected
    def post(self, safe_key):
        obj = ndb.Key(urlsafe=safe_key).get()
        form = EditForm(formdata=self.request.POST)
        if form.validate():
            obj.edit(form.data)
            self.redirect_to('entry_admin')
        else:
            self.render_template('admin/entry_form.html', {'form': form, 'object': obj, 'filter': None})
