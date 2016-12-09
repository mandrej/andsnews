import unittest
from models import update_filters

class UpdateTest(unittest.TestCase):
    def test_add(self):
        new_pairs = [('date', 2016), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro')]
        old_pairs = []
        update_filters(new_pairs, old_pairs)

    def test_edit(self):
        new_pairs = [('date', 2016), ('tags', 'street'), ('model', 'SIGMA dp2 Quattro')]
        old_pairs = [('date', 2016), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro')]
        update_filters(new_pairs, old_pairs)

    def test_del(self):
        new_pairs = []
        old_pairs = [('date', 2016), ('tags', 'street'), ('model', 'SIGMA dp2 Quattro')]
        update_filters(new_pairs, old_pairs)
