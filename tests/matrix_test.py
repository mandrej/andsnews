import unittest
from itertools import combinations

res = [[u'milan', u'portrait'], [u'djordje', u'mihailo', u'milan'], [u'katarina', u'mihailo', u'svetlana'], [u'ana'],
       [u'ana', u'iva'], [u'ana', u'portrait'], [u'mihailo', u'wedding'], [u'katarina', u'mihailo', u'wedding'],
       [u'djordje', u'katarina', u'mihailo'], [u'mihailo', u'portrait'], [u'djordje', u'katarina'],
       [u'djordje', u'iva', u'masa'], [u'iva', u'portrait'], [u'iva', u'wedding'], [u'iva', u'portrait'],
       [u'iva', u'portrait'], [u'b&w', u'iva', u'portrait'], [u'masa', u'portrait'], [u'masa', u'portrait'], [u'masa'],
       [u'masa'], [u'djordje'], [u'djordje', u'portrait'], [u'djordje']]


class MatrixTest(unittest.TestCase):
    def test_matrix(self):
        """
        milan only, milan + svetlana, milan + ana, ...
        svetlana + milan, sveltlana only, svetlana + ana, ...

        :return: matrix
        """
        names = [u'milan', u'svetlana', u'ana', u'mihailo', u'milos', u'katarina', u'iva', u'masa', u'djordje']
        NAMES = dict([(name, index) for index, name in enumerate(names)])
        RES = []
        for tag in res:
            tmp = []
            for name in tag:
                try:
                    # print NAMES[name]
                    tmp.append(NAMES[name])
                except KeyError:
                    # print -1
                    tmp.append(-1)
            RES.append(tmp)

        # print RES

        # for x, y in combinations(names, 2):
        #     print '{0}\t{1}'.format(NAMES[x], NAMES[y])
        MATRIX = []
        for n in range(9):
            MATRIX.append([0] * 9)

        matrix = {}
        for x, y in combinations(names, 2):
            key = '%s, %s' % (x, y)
            matrix[key] = 0
            pair = set((x, y))
            for tags in res:
                if pair & set(tags) == pair:
                    matrix[key] += 1
                    # print '%s, %s in %s' % (x, y, tags)

        print matrix

        for x, y in combinations(names, 2):
            pair = set((x, y))
            for tag in res:
                if pair & set(tag) == pair:
                    MATRIX[NAMES[x]][NAMES[y]] += 1
                    MATRIX[NAMES[y]][NAMES[x]] = MATRIX[NAMES[x]][NAMES[y]]
                    # print '%s, %s in %s' % (x, y, tag)

        print MATRIX
        # print '--------enumerate(names)----------'
        # for k, v in matrix.items():
        #     print k, v
