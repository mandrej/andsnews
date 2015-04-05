__author__ = 'milan'

import logging

from mapreduce import operation as op
from models import rounding
from config import ASA, LENGTHS


def calculate_palette(entity):
    yield entity.palette_async()
    yield op.db.Put(entity)


def calculate_dimension(entity):
    yield entity.dim_async()
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