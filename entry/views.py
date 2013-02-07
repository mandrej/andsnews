import webapp2
from google.appengine.api import users
from webapp2_extras.i18n import lazy_gettext as _
from webapp2_extras.appengine.users import login_required, admin_required
from wtforms import Form, widgets, FormField, FieldList, fields, validators
from models import Entry, ENTRY_IMAGES
from common import  BaseHandler, Paginator, Filter, TagsField, EmailField, make_thumbnail
from settings import LIMIT, TIMEOUT
PER_PAGE = 6

class Index(BaseHandler):
    def get(self, field=None, value=None):
        f = Filter(field, value)
        filters = [Entry._properties[k] == v for k, v in f.parameters.items()]
        query = Entry.query(*filters).order(-Entry.date)

        page = int(self.request.get('page', 1))
        paginator = Paginator(query, per_page=PER_PAGE)
        objects, has_next = paginator.page(page)

        data = {'objects': objects,
                'filter': f.parameters,
                'filter_url': f.url,
                'filter_title': f.title,
                'page': page,
                'has_next': has_next,
                'has_previous': page > 1}
        self.render_template('entry/index.html', data)

class Detail(BaseHandler):
    def get(self, slug):
        obj = Entry.get_by_id(slug)
        if obj is None:
            webapp2.abort(404)
        self.render_template('entry/detail.html', {'object': obj, 'filter': None})

class RequiredIf(validators.Required):
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
    name = fields.TextField(_('New Image'))
#    blob = fields.FileField(validators=[RequiredIf('name')])
    blob = fields.FileField()

class ImgEditForm(Form):
    name = fields.TextField(_('Image'))
    num = fields.IntegerField()
    delete = fields.BooleanField(_('remove'))

class AddForm(Form):
    headline = fields.TextField(_('Headline'), validators=[validators.DataRequired()])
    slug = fields.TextField(_('Slug'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    author = fields.TextField(_('Author'), validators=[validators.DataRequired()])
    summary = fields.TextAreaField(_('Summary'), validators=[validators.DataRequired()])
    date = fields.DateTimeField(_('Posted'), validators=[validators.DataRequired()])
    body = fields.TextAreaField(_('Article'), validators=[validators.DataRequired()])
    newimages = FieldList(FormField(ImgAddForm))

    def validate_slug(self, field):
        if Entry.get_by_id(field.data):
            raise validators.ValidationError(_('Record with this slug already exist'))

class EditForm(Form):
    headline = fields.TextField(_('Headline'), validators=[validators.DataRequired()])
    tags = TagsField(_('Tags'), description='Comma separated values')
    author = fields.TextField(_('Author'), validators=[validators.DataRequired()])
    summary = fields.TextAreaField(_('Summary'), validators=[validators.DataRequired()])
    date = fields.DateTimeField(_('Posted'), validators=[validators.DataRequired()])
    body = fields.TextAreaField(_('Article'), validators=[validators.DataRequired()])
    front = fields.SelectField(_('Front image'), coerce=int)
    images = FieldList(FormField(ImgEditForm), min_entries=0, max_entries=ENTRY_IMAGES)
    newimages = FieldList(FormField(ImgAddForm))

class Add(BaseHandler):
    @login_required
    def get(self, form=None):
        if form is None:
            form = AddForm()
            form.newimages.append_entry()
        self.render_template('entry/form.html', {'form': form, 'object': None, 'filter': None})

    def post(self):
        form = AddForm(formdata=self.request.POST)
        if form.validate():
            obj = Entry(id=form.slug.data)
            obj.add(form.data)
            self.redirect(self.index_urls['Entry'])
        else:
            self.render_template('entry/form.html', {'form': form, 'object': None, 'filter': None})

def front_choices(obj):
    choices = [(img.num, img.name) for img in obj.image_list]
    choices.insert(0, (-1, '---'))
    return choices

class Edit(BaseHandler):
    @login_required
    def get(self, slug, form=None):
        obj = Entry.get_by_id(slug)
        user = users.get_current_user()
        is_admin = users.is_current_user_admin()
        if not is_admin:
            if user != obj.author:
                webapp2.abort(403)
        if form is None:
            form = EditForm(obj=obj)
            form.front.choices = front_choices(obj)
            for img in obj.image_list:
                form.images.append_entry(img)
            form.newimages.append_entry()
        self.render_template('entry/form.html', {'form': form, 'object': obj, 'filter': None})

    def post(self, slug):
        obj = Entry.get_by_id(slug)
        form = EditForm(formdata=self.request.POST)
        form.front.choices = front_choices(obj)
        if form.validate():
            obj.edit(form.data)
            self.redirect(self.index_urls['Entry'])
        else:
            self.render_template('entry/form.html', {'form': form, 'object': obj, 'filter': None})

def thumb(request, slug, size):
    out, mime = make_thumbnail('Entry', slug, size)
    if out:
        response = webapp2.Response(content_type=mime)
        response.headers['Cache-Control'] = 'public, max-age=%s' % (TIMEOUT*600)
        if size == 'normal':
            response.headers['Content-Disposition'] = 'inline; filename=%s' % slug
        response.write(out)
        return response
    else:
        webapp2.abort(503)