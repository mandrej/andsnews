__author__ = 'milan'

import logging

from PIL import Image

from palette import extract_colors
from mapreduce import operation as op
from models import rounding, range_names
from config import ASA, LENGTHS


def calculate_palette(entity):
    # yield entity.palette_async()
    img = entity.image_from_buffer
    img.thumbnail((100, 100), Image.ANTIALIAS)
    palette = extract_colors(img)
    if palette.bgcolor:
        entity.rgb = palette.bgcolor.value
    else:
        entity.rgb = palette.colors[0].value
        entity.hue, entity.lum, entity.sat = range_names(entity.rgb)

    yield op.db.Put(entity)


def calculate_dimension(entity):
    # yield entity.dim_async()
    entity.dim = entity.image_from_buffer.size
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