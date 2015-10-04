import unittest


def name(make, model):
    s1 = set(make.split())
    s2 = set(model.split())
    if s1 & s2:  # contain word in make and model
        return model
    else:
        return '%s %s' % (make, model)


class ModelNameTest(unittest.TestCase):
    pass

    def test_name(self):
        print name('Canon', 'Canon EOS 5D Mark III')
        print name('NIKON CORPORATION', 'NIKON D700')
        print name('OLYMPUS IMAGING CORP.', 'E-P1')
        print name('SONY', 'DSC-W110')
        print name('PENTACON', 'Luxmedia 8403')