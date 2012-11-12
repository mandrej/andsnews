from google.appengine.ext import ndb, deferred
from google.appengine.api import memcache
from django.shortcuts import redirect, render
from django.template.defaultfilters import filesizeformat
from models import Photo, Entry, Comment, Feed, Counter, KEYS, range_names
from lib.comm import Filter, Paginator, admin_required, json_response, make_thumbnail, \
    count_colors, count_property, make_cloud, median
from django.conf import settings

def memcache_delete(request, key):
    if request.is_ajax():
        memcache.delete(key)
        return json_response(None)

def build(request, key):
    if request.is_ajax():
        kind, field = key.split('_')
        content = count_property(kind, field)
        return json_response(content)

def create(request, key):
    if request.is_ajax():
        kind, field = key.split('_')
        if field == 'colors':
            content = count_colors()
        else:
            content = make_cloud(kind, field)
        return json_response(content)

def memcahe_content(request):
    if request.is_ajax():
        data = {}
        for key in KEYS:
            data[key] = memcache.get(key)
        return json_response(data)

@admin_required
def index(request, tmpl='admin/index.html'):
    data = {
        'photo_count': Photo.query().order(-Photo.date).count(), 
        'entry_count': Entry.query().order(-Entry.date).count(), 
        'comment_count': Comment.query().order(-Comment.date).count(), 
        'feeds_count': Feed.query().order(-Feed.date).count()
    }
    data.update(memcache.get_multi(KEYS))
    return render(request, tmpl, data)

@admin_required
def comments(request, tmpl='admin/comments.html'):
    query = Comment.query().order(-Comment.date)
    page = int(request.GET.get('page', 1))
    paginator = Paginator(query, 10)
    objects, has_next = paginator.page(page)
    
    data = {'objects': objects, 'page': page, 'has_next': has_next, 'has_previous': page > 1}
    return render(request, tmpl, data)

def delete_small(parentkind, oldkey):
    """ deferred.defer(delete_small, *args) """
    key = ndb.Key.from_old_key(oldkey)
    obj = key.get()
    if parentkind == 'Photo': obj.small = None
    elif parentkind == 'Entry': obj.small = None
    obj.put()

def comment_save(request):
    if request.is_ajax():
        key = ndb.Key(urlsafe=request.POST['key'])
        obj = key.get()
        obj.body = request.POST['body']
        obj.put()
        return json_response({'success': True})

def comment_delete(request):
    if request.is_ajax():
        key = ndb.Key(urlsafe=request.POST['key'])
        key.delete()
        return json_response({'success': True})

def thumbnail_delete(request):
    if request.is_ajax():
        params = request.POST
        args = [params['kind'], params['key']]
        deferred.defer(delete_small, *args)
        return json_response({'success': True})

def thumbnail_make(request):
    if request.is_ajax():
        params = request.POST
        parentkind = params['kind']
        slug = params['slug']
        no = small = '---'

        deferred.defer(make_thumbnail, parentkind, slug, 'small')

        if small != no: small = filesizeformat(len(small))
        return json_response({'success': True, 'small': small})

def thumbnail_color(request):
    if request.is_ajax():
        params = request.POST
        parentkind = params['kind']
        slug = params['slug']
        
        obj = ndb.Key(parentkind, slug, 'Picture', slug).get()
        obj.rgb = median(obj.small)
        obj.put()
        photo = ndb.Key(parentkind, slug).get()
        photo.hue, photo.lum, photo.sat = range_names(*obj.hls)
        photo.put()
        return json_response({'success': True, 'hex': obj.hex})

@admin_required
def thumbnails(request, kind, field=None, value=None, per_page=settings.PER_PAGE, tmpl='admin/thumbnails.html'):
    f = Filter(field, value)
    model = ndb.Model._kind_map.get(kind)
    filters = [model._properties[k] == v for k, v in f.parameters.items()]
    query = model.query(*filters).order(-model.date)
    
    page = int(request.GET.get('page', 1))
    paginator = Paginator(query, per_page=per_page)
    objects, has_next = paginator.page(page)
    
    data = {'objects': objects,
            'filter': f.parameters,
            'kind': kind,
            'page': page,
            'has_next': has_next,
            'has_previous': page > 1}
    data['archive'] = make_cloud(kind, 'date')
    data['link'] = '/admin/%s/thumbnails/date' % kind.lower()
    return render(request, tmpl, data)

@admin_required
def info(request, oldkey, tmpl='admin/info.html'):
    if request.is_ajax():
        key = ndb.Key.from_old_key(oldkey)
        return render(request, tmpl, {'object': key.get()})

@admin_required
def feeds(request, tmpl='admin/feeds.html'):
    query = Feed.query().order(-Feed.date)
    if request.method == 'POST':
        feed_slug = request.POST.get('action:feed')
        if feed_slug:
            if feed_slug == 'all':
                k = [x.key().name() for x in query]
                memcache.delete_multi(k)
            else:
                memcache.delete(feed_slug)
        return redirect('/admin/feeds')
    else:
        return render(request, tmpl, {'objects': query})

@admin_required
def counters(request, per_page=settings.PER_PAGE, tmpl='admin/counters.html'):
    cntx = ndb.get_context()
    cntx.set_cache_policy(False)
    if request.method == 'POST':
        if request.POST.get('action:delete'):
            key = ndb.Key(urlsafe=request.POST.get('action:delete'))
            key.delete()
        elif request.POST.get('action:edit'):
            input_id = request.POST.get('action:edit')
            key = ndb.Key(urlsafe=input_id)
            obj = key.get()
            obj.count = int(request.POST.get('count.%s' % input_id))
            obj.put()
        return redirect('/admin/counters')
    else:
        query = Counter.query().order(Counter.field)
        page = int(request.GET.get('page', 1))
        paginator = Paginator(query, per_page=per_page)
        objects, has_next = paginator.page(page)

        data = {'objects': objects, 'page': page, 'has_next': has_next, 'has_previous': page > 1}
        return render(request, tmpl, data)
