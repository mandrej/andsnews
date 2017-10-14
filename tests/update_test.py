import unittest
from views.models import Photo


class UpdateTest(unittest.TestCase):
    def setUp(self):
        self.obj = Photo.get_by_id('mirodjija')

    def test_add(self):
        new_pairs = [('date', 2016), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro')]
        old_pairs = []
        self.obj.update_filters(new_pairs, old_pairs)

    def test_edit(self):
        new_pairs = [('date', 2016), ('tags', 'street'), ('model', 'SIGMA dp2 Quattro')]
        old_pairs = [('date', 2016), ('tags', 'new'), ('model', 'SIGMA dp2 Quattro')]
        self.obj.update_filters(new_pairs, old_pairs)

    def test_del(self):
        new_pairs = []
        old_pairs = [('date', 2016), ('tags', 'street'), ('model', 'SIGMA dp2 Quattro')]
        self.obj.update_filters(new_pairs, old_pairs)
