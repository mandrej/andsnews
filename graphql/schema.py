import logging
import graphene
from google.appengine.ext import ndb
from models import Photo, PHOTO_FILTER
from api import Cached, available_filters, SearchPaginator

CACHED = Cached()


class CounterType(graphene.ObjectType):
    field_name = graphene.String()
    count = graphene.Int()
    name = graphene.String()
    serving_url = graphene.String()
    repr_stamp = graphene.DateTime()


class PhotoFields(graphene.AbstractType):
    aperture = graphene.Float()
    author = graphene.String()
    color = graphene.String()
    date = graphene.DateTime()
    dim = graphene.List(graphene.Int)
    filename = graphene.String()
    focal_length = graphene.Int()
    headline = graphene.String()
    iso = graphene.Int()
    kind = graphene.String(required=True, default_value='photo')
    lens = graphene.String()
    model = graphene.String()
    serving_url = graphene.String()
    shutter = graphene.String()
    slug = graphene.String()
    tags = graphene.List(graphene.String)
    year = graphene.String()


class PhotoInput(graphene.InputObjectType, PhotoFields):
    pass


class PhotoType(graphene.ObjectType, PhotoFields):
    id = graphene.ID(required=True)


class ResultType(graphene.ObjectType):
    page = graphene.String()
    next_page = graphene.String()
    number_found = graphene.Int()
    error = graphene.String()
    objects = graphene.List(PhotoType)


class ValuesType(graphene.ObjectType):
    year = graphene.List(graphene.Int)
    tags = graphene.List(graphene.String)
    model = graphene.List(graphene.String)
    color = graphene.List(graphene.String)
    author = graphene.List(graphene.String)


class Query(graphene.ObjectType):
    count = graphene.Int()
    filters = graphene.List(CounterType)
    values = graphene.Field(ValuesType)

    result = graphene.Field(
        ResultType,
        find=graphene.String(required=True),
        page=graphene.String(),
        per_page=graphene.Int(required=True))

    @staticmethod
    def resolve_count(cls, info):
        return Photo.query().count()

    @staticmethod
    def resolve_values(cls, info):
        res = {}
        data = CACHED.counters
        for field in PHOTO_FILTER:
            _list = [counter.value for counter in data[field]]
            if field == 'year':
                res[field] = sorted(_list, reverse=True)
            else:
                res[field] = sorted(_list)

        return ValuesType(**res)

    @staticmethod
    def resolve_filters(cls, info):
        data = CACHED.counters
        _list = available_filters(data)
        return [CounterType(
            field_name=item['field_name'],
            count=item['count'],
            name=str(item['name']),
            serving_url=item['serving_url'],
            repr_stamp=item['repr_stamp']) for item in _list]

    @staticmethod
    def resolve_result(cls, info, **kwargs):
        find = kwargs.get('find')
        page = kwargs.get('page')
        per_page = kwargs.get('per_page')
        paginator = SearchPaginator(find, per_page=per_page)
        objects, number_found, token, error = paginator.page(page)
        return ResultType(
            page=page if page else 'FP',
            next_page=token,
            number_found=number_found,
            error=error,
            objects=[PhotoType(
                id=obj.key.urlsafe(),
                aperture=obj.aperture,
                author=obj.author.email(),
                color=obj.color,
                date=obj.date,
                dim=obj.dim,
                filename=obj.filename,
                focal_length=obj.focal_length,
                headline=obj.headline,
                iso=obj.iso,
                lens=obj.lens,
                model=obj.model,
                serving_url=obj.serving_url,
                shutter=obj.shutter,
                slug=obj.slug,
                tags=obj.tags,
                year=str(obj.year)
            ) for obj in objects]
        )


class UpdatePhoto(graphene.Mutation):
    class Arguments:
        id = graphene.String(required=True)
        photo_data = PhotoInput(required=True)

    ok = graphene.Boolean()
    photo = graphene.Field(PhotoType)

    def mutate(self, info, id, photo_data):
        key = ndb.Key(urlsafe=id)
        if key is None:
            return UpdatePhoto(photo=None, ok=False)

        obj = key.get()
        _new = obj.edit(photo_data)
        return UpdatePhoto(photo=_new, ok=True)


class RemovePhoto(graphene.Mutation):
    class Arguments:
        id = graphene.String()

    ok = graphene.Boolean()

    def mutate(self, info, id):
        key = ndb.Key(urlsafe=id)
        if key is not None:
            key.get().remove()
            return RemovePhoto(ok=True)
        return RemovePhoto(ok=False)


class Mutation(graphene.ObjectType):
    update = UpdatePhoto.Field()
    remove = RemovePhoto.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
