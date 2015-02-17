__author__ = 'milan'

import logging

from google.appengine.ext import blobstore

from mapreduce import operation as op
from models import rounding, img_palette, range_names
from config import ASA, LENGTHS


def calculate_palette(entity):
    blob_reader = blobstore.BlobReader(entity.blob_key, buffer_size=1024*1024)
    buff = blob_reader.read()
    palette = img_palette(buff)
    if palette.bgcolor:
        entity.rgb = palette.bgcolor.value
    else:
        entity.rgb = palette.colors[0].value
    entity.hue, entity.lum, entity.sat = range_names(entity.rgb)

    yield op.db.Put(entity)


def current_fix(entity):
    logging.info(entity.headline)
    if entity.focal_length and entity.crop_factor:
        value = int(entity.focal_length * entity.crop_factor)
        entity.eqv = rounding(value, LENGTHS)
    if entity.iso:
        value = int(entity.iso)
        entity.iso = rounding(value, ASA)

    yield op.db.Put(entity)