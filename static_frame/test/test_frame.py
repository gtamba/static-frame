from itertools import zip_longest
from itertools import combinations
import unittest
from collections import OrderedDict
import itertools as it
from collections import namedtuple
from io import StringIO
import string
import hashlib


import numpy as np

import static_frame as sf
# assuming located in the same directory
from static_frame import Index
from static_frame import IndexGO
from static_frame import IndexHierarchy
from static_frame import IndexHierarchyGO
from static_frame import Series
from static_frame import Frame
from static_frame import FrameGO
from static_frame import TypeBlocks
from static_frame import Display
from static_frame import mloc
from static_frame import DisplayConfig

from static_frame.test.test_case import TestCase


nan = np.nan


class TestUnit(TestCase):


    def test_frame_init_a(self):

        f = Frame(OrderedDict([('a', (1,2)), ('b', (3,4))]), index=('x', 'y'))
        self.assertEqual(f.to_pairs(0),
                (('a', (('x', 1), ('y', 2))), ('b', (('x', 3), ('y', 4))))
                )

        f = Frame(OrderedDict([('b', (3,4)), ('a', (1,2))]), index=('x', 'y'))
        self.assertEqual(f.to_pairs(0),
                (('b', (('x', 3), ('y', 4))), ('a', (('x', 1), ('y', 2)))))


    def test_frame_init_b(self):
        # test unusual instantiation cases

        # create a frame with a single value
        f1 = Frame(1, index=(1,2), columns=(3,4,5))
        self.assertEqual(f1.to_pairs(0),
                ((3, ((1, 1), (2, 1))), (4, ((1, 1), (2, 1))), (5, ((1, 1), (2, 1))))
                )

        # with columns not defined, we create a DF with just an index
        f2 = FrameGO(None, index=(1,2))
        f2['a'] = (-1, -1)
        self.assertEqual(f2.to_pairs(0),
                (('a', ((1, -1), (2, -1))),)
                )

        # with columns and index defined, we fill the value even if None
        f3 = Frame(None, index=(1,2), columns=(3,4,5))
        self.assertEqual(f3.to_pairs(0),
                ((3, ((1, None), (2, None))), (4, ((1, None), (2, None))), (5, ((1, None), (2, None)))))

        # auto populated index/columns based on shape
        f4 = Frame([[1,2], [3,4], [5,6]])
        self.assertEqual(f4.to_pairs(0),
                ((0, ((0, 1), (1, 3), (2, 5))), (1, ((0, 2), (1, 4), (2, 6))))
                )
        self.assertTrue(f4._index._loc_is_iloc)
        self.assertTrue(f4._columns._loc_is_iloc)


    def test_frame_init_c(self):
        f = sf.FrameGO(dict(color=('black',)))
        s = f['color']
        self.assertEqual(s.to_pairs(),
                ((0, 'black'),))

    def test_frame_from_pairs_a(self):

        frame = Frame.from_items(sorted(dict(a=[3,4,5], b=[6,3,2]).items()))
        self.assertEqual(
            list((k, list(v.items())) for k, v in frame.items()),
            [('a', [(0, 3), (1, 4), (2, 5)]), ('b', [(0, 6), (1, 3), (2, 2)])])

        frame = Frame.from_items(OrderedDict((('b', [6,3,2]), ('a', [3,4,5]))).items())
        self.assertEqual(list((k, list(v.items())) for k, v in frame.items()),
            [('b', [(0, 6), (1, 3), (2, 2)]), ('a', [(0, 3), (1, 4), (2, 5)])])


    def test_frame_getitem_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # # show that block hav ebeen consolidated
        # self.assertEqual(len(f1._blocks._blocks), 3)

        # s1 = f1['s']
        # self.assertTrue((s1.index == f1.index).all())

        # # we have not copied the index array
        # self.assertEqual(mloc(f1.index.values), mloc(s1.index.values))

        f2 = f1['r':]
        self.assertEqual(f2.columns.values.tolist(), ['r', 's', 't'])
        self.assertTrue((f2.index == f1.index).all())
        self.assertEqual(mloc(f2.index.values), mloc(f1.index.values))




    def test_frame_length_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(len(f1), 2)



    def test_frame_iloc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual((f1.iloc[0].values == f1.loc['x'].values).all(), True)
        self.assertEqual((f1.iloc[1].values == f1.loc['y'].values).all(), True)


    def test_frame_iloc_b(self):
        # this is example dervied from this question:
        # https://stackoverflow.com/questions/22927181/selecting-specific-rows-and-columns-from-numpy-array

        a = np.arange(20).reshape((5,4))
        f1 = FrameGO(a)
        a[1,1] = 3000 # ensure we made a copy
        self.assertEqual(f1.loc[[0,1,3], [0,2]].values.tolist(),
                [[0, 2], [4, 6], [12, 14]])
        self.assertEqual(f1.iloc[[0,1,3], [0,2]].values.tolist(),
                [[0, 2], [4, 6], [12, 14]])

        self.assertTrue(f1._index._loc_is_iloc)
        self.assertTrue(f1._columns._loc_is_iloc)

        f1[4] = list(range(5))
        self.assertTrue(f1._columns._loc_is_iloc)

        f1[20] = list(range(5))
        self.assertFalse(f1._columns._loc_is_iloc)

        self.assertEqual(f1.values.tolist(),
                [[0, 1, 2, 3, 0, 0],
                [4, 5, 6, 7, 1, 1],
                [8, 9, 10, 11, 2, 2],
                [12, 13, 14, 15, 3, 3],
                [16, 17, 18, 19, 4, 4]])


    def test_frame_iter_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual((f1.keys() == f1.columns).all(), True)
        self.assertEqual([x for x in f1.columns], ['p', 'q', 'r', 's', 't'])
        self.assertEqual([x for x in f1], ['p', 'q', 'r', 's', 't'])




    def test_frame_iter_array_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(
                next(iter(f1.iter_array(axis=0))).tolist(),
                [1, 30])

        self.assertEqual(
                next(iter(f1.iter_array(axis=1))).tolist(),
                [1, 2, 'a', False, True])


    def test_frame_iter_array_b(self):

        arrays = list(np.random.rand(1000) for _ in range(100))
        f1 = Frame.from_items(
                zip(range(100), arrays)
                )

        # iter columns
        post = f1.iter_array(0).apply_pool(np.sum, max_workers=4, use_threads=True)
        self.assertEqual(post.shape, (100,))
        self.assertAlmostEqual(f1.sum().sum(), post.sum())

        post = f1.iter_array(0).apply_pool(np.sum, max_workers=4, use_threads=False)
        self.assertEqual(post.shape, (100,))
        self.assertAlmostEqual(f1.sum().sum(), post.sum())


    def test_frame_setitem_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        f1['a'] = (False, True)
        self.assertEqual(f1['a'].values.tolist(), [False, True])

        # test index alginment
        f1['b'] = Series((3,2,5), index=('y', 'x', 'g'))
        self.assertEqual(f1['b'].values.tolist(), [2, 3])

        f1['c'] = Series((300,200,500), index=('y', 'j', 'k'))
        self.assertAlmostEqualItems(f1['c'].items(), [('x', nan), ('y', 300)])


    def test_frame_setitem_b(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        f1['u'] = 0

        self.assertEqual(f1.loc['x'].values.tolist(),
                [1, 2, 'a', False, True, 0])

        with self.assertRaises(Exception):
            f1['w'] = [[1,2], [4,5]]



    def test_frame_extend_columns_a(self):
        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        columns = OrderedDict(
            (('c', np.array([0, -1])), ('d', np.array([3, 5]))))

        f1.extend_columns(columns.keys(), columns.values())

        self.assertEqual(f1.columns.values.tolist(),
                ['p', 'q', 'r', 's', 't', 'c', 'd'])

        self.assertTypeBlocksArrayEqual(f1._blocks,
                [[1, 2, 'a', False, True, 0, 3],
                [30, 50, 'b', True, False, -1, 5]],
                match_dtype=object)

    def test_frame_extend_blocks_a(self):
        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))
        f1 = FrameGO.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        blocks = ([[50, 40], [30, 20]], [[50, 40], [30, 20]])
        columns = ('a', 'b', 'c', 'd')
        f1.extend_blocks(columns, blocks)

        self.assertEqual(f1.columns.values.tolist(),
                ['p', 'q', 'r', 's', 't', 'a', 'b', 'c', 'd'])

        self.assertEqual(f1.values.tolist(),
                [[1, 2, 'a', False, True, 50, 40, 50, 40],
                [30, 50, 'b', True, False, 30, 20, 30, 20]]
                )


    def test_frame_extract_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))


        f2 = f1._extract(row_key=np.array((False, True, True, False), dtype=bool))

        self.assertEqual(f2.to_pairs(0),
                (('p', (('x', 30), ('y', 2))), ('q', (('x', 34), ('y', 95))), ('r', (('x', 'b'), ('y', 'c'))), ('s', (('x', True), ('y', False))), ('t', (('x', False), ('y', False)))))


        f3 = f1._extract(row_key=np.array((True, False, False, True), dtype=bool))

        self.assertEqual(f3.to_pairs(0),
                (('p', (('w', 2), ('z', 30))), ('q', (('w', 2), ('z', 73))), ('r', (('w', 'a'), ('z', 'd'))), ('s', (('w', False), ('z', True))), ('t', (('w', False), ('z', True)))))


        # attempting to select any single row results in a problem, as the first block given to the TypeBlocks constructor is a 1d array that looks it is a (2,1) instead of a (1, 2)
        f4 = f1._extract(row_key=np.array((False, False, True, False), dtype=bool))

        self.assertEqual(
                f4.to_pairs(0),
                (('p', (('y', 2),)), ('q', (('y', 95),)), ('r', (('y', 'c'),)), ('s', (('y', False),)), ('t', (('y', False),)))
                )




    def test_frame_loc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # cases of single series extraction
        s1 = f1.loc['x']
        self.assertEqual(list(s1.items()),
                [('p', 1), ('q', 2), ('r', 'a'), ('s', False), ('t', True)])

        s2 = f1.loc[:, 'p']
        self.assertEqual(list(s2.items()),
                [('x', 1), ('y', 30)])

        self.assertEqual(
                f1.loc[['y', 'x']].index.values.tolist(),
                ['y', 'x'])

        self.assertEqual(f1['r':].columns.values.tolist(),
                ['r', 's', 't'])


    def test_frame_items_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(
                list((k, list(v.items())) for k, v in f1.items()),
                [('p', [('x', 1), ('y', 30)]), ('q', [('x', 2), ('y', 50)]), ('r', [('x', 'a'), ('y', 'b')]), ('s', [('x', False), ('y', True)]), ('t', [('x', True), ('y', False)])]
                )



    def test_frame_loc_b(self):
        # dimensionality of returned item based on selectors
        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # return a series if one axis is multi
        post = f1.loc['x', 't':]
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.index.values.tolist(), ['t'])

        post = f1.loc['y':, 't']
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.index.values.tolist(), ['y'])

        # if both are multi than we get a Frame
        post = f1.loc['y':, 't':]
        self.assertEqual(post.__class__, Frame)
        self.assertEqual(post.index.values.tolist(), ['y'])
        self.assertEqual(post.columns.values.tolist(), ['t'])

        # return a series
        post = f1.loc['x', 's':]
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.index.values.tolist(),['s', 't'])

        post = f1.loc[:, 's']
        self.assertEqual(post.__class__, Series)
        self.assertEqual(post.index.values.tolist(), ['x', 'y'])

        self.assertEqual(f1.loc['x', 's'], False)
        self.assertEqual(f1.loc['y', 'p'], 30)


    def test_frame_loc_c(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = f1.loc['x':]
        # import ipdb; ipdb.set_trace()


    def test_frame_attrs_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(str(f1.dtypes.values.tolist()),
                "[dtype('int64'), dtype('int64'), dtype('<U1'), dtype('bool'), dtype('bool')]")

        self.assertEqual(f1.size, 10)
        self.assertEqual(f1.ndim, 2)
        self.assertEqual(f1.shape, (2, 5))



    def test_frame_assign_iloc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))


        self.assertEqual(f1.assign.iloc[1,1](3000).iloc[1,1], 3000)


    def test_frame_assign_loc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(f1.assign.loc['x', 's'](3000).values.tolist(),
                [[1, 2, 'a', 3000, True], [30, 50, 'b', True, False]])

        # can assign to a columne
        self.assertEqual(
                f1.assign['s']('x').values.tolist(),
                [[1, 2, 'a', 'x', True], [30, 50, 'b', 'x', False]])


    def test_frame_assign_loc_b(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # unindexed tuple/list assingment
        self.assertEqual(
                f1.assign['s']([50, 40]).values.tolist(),
                [[1, 2, 'a', 50, True], [30, 50, 'b', 40, False]]
                )

        self.assertEqual(
                f1.assign.loc['y'](list(range(5))).values.tolist(),
                [[1, 2, 'a', False, True], [0, 1, 2, 3, 4]])




    def test_frame_assign_loc_c(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # assinging a series to a part of wone row
        post = f1.assign.loc['x', 'r':](Series((-1, -2, -3), index=('t', 'r', 's')))

        self.assertEqual(post.values.tolist(),
                [[1, 2, -2, -3, -1], [30, 50, 'b', True, False]])

        post = f1.assign.loc[['x', 'y'], 'r'](Series((-1, -2), index=('y', 'x')))

        self.assertEqual(post.values.tolist(),
                [[1, 2, -2, False, True], [30, 50, -1, True, False]])

        # ordere here does not matter
        post = f1.assign.loc[['y', 'x'], 'r'](Series((-1, -2), index=('y', 'x')))

        self.assertEqual(post.values.tolist(),
                [[1, 2, -2, False, True], [30, 50, -1, True, False]])


    def test_frame_assign_loc_d(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        value1 = Frame.from_records(((20, 21, 22),(23, 24, 25)),
                index=('x', 'y'),
                columns=('s', 't', 'w'))

        f2 = f1.assign.loc[['x', 'y'], ['s', 't']](value1)
        self.assertEqual(f2.to_pairs(0),
                (('p', (('x', 1), ('y', 30))), ('q', (('x', 2), ('y', 50))), ('r', (('x', 'a'), ('y', 'b'))), ('s', (('x', 20), ('y', 23))), ('t', (('x', 21), ('y', 24)))))



    def test_frame_assign_coercion_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))
        f2 = f1.assign.loc['x', 'r'](None)
        self.assertEqual(f2.to_pairs(0),
                (('p', (('x', 1), ('y', 30))), ('q', (('x', 2), ('y', 50))), ('r', (('x', None), ('y', 'b'))), ('s', (('x', False), ('y', True))), ('t', (('x', True), ('y', False)))))


    def test_frame_mask_loc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        self.assertEqual(
                f1.mask.loc['x', 'r':].values.tolist(),
                [[False, False, True, True, True], [False, False, False, False, False]])


        self.assertEqual(f1.mask['s'].values.tolist(),
                [[False, False, False, True, False], [False, False, False, True, False]])


    def test_frame_masked_array_loc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        # mask our the non-integers
        self.assertEqual(
                f1.masked_array.loc[:, 'r':].sum(), 83)


    def test_reindex_other_like_iloc_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        value1 = Series((100, 200, 300), index=('s', 'u', 't'))
        iloc_key1 = (0, slice(2, None))
        v1 = f1._reindex_other_like_iloc(value1, iloc_key1)

        self.assertAlmostEqualItems(v1.items(),
                [('r', nan), ('s', 100), ('t', 300)])


        value2 = Series((100, 200), index=('y', 'x'))
        iloc_key2 = (slice(0, None), 2)
        v2 = f1._reindex_other_like_iloc(value2, iloc_key2)

        self.assertAlmostEqualItems(v2.items(),
                [('x', 200), ('y', 100)])


    def test_reindex_other_like_iloc_b(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 50, 'b', True, False))

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x','y'))

        value1 = Frame.from_records(((20, 21, 22),(23, 24, 25)),
                index=('x', 'y'),
                columns=('s', 't', 'w'))

        iloc_key1 = (slice(0, None), slice(3, None))
        v1 = f1._reindex_other_like_iloc(value1, iloc_key1)

        self.assertEqual(v1.to_pairs(0),
                (('s', (('x', 20), ('y', 23))), ('t', (('x', 21), ('y', 24)))))


    def test_frame_reindex_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        # subset index reindex
        self.assertEqual(
                f1.reindex(('z', 'w')).to_pairs(axis=0),
                (('p', (('z', 65), ('w', 1))), ('q', (('z', 73), ('w', 2))), ('r', (('z', 'd'), ('w', 'a'))), ('s', (('z', True), ('w', False))), ('t', (('z', True), ('w', True)))))

        # index only with nan filling
        self.assertEqual(
                f1.reindex(('z', 'b', 'w'), fill_value=None).to_pairs(0),
                (('p', (('z', 65), ('b', None), ('w', 1))), ('q', (('z', 73), ('b', None), ('w', 2))), ('r', (('z', 'd'), ('b', None), ('w', 'a'))), ('s', (('z', True), ('b', None), ('w', False))), ('t', (('z', True), ('b', None), ('w', True)))))



    def test_frame_axis_flat_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.to_pairs(axis=1),
                (('w', (('p', 1), ('q', 2), ('r', 'a'), ('s', False), ('t', True))), ('x', (('p', 30), ('q', 34), ('r', 'b'), ('s', True), ('t', False))), ('y', (('p', 54), ('q', 95), ('r', 'c'), ('s', False), ('t', False))), ('z', (('p', 65), ('q', 73), ('r', 'd'), ('s', True), ('t', True)))))


        self.assertEqual(f1.to_pairs(axis=0),
                (('p', (('w', 1), ('x', 30), ('y', 54), ('z', 65))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('r', (('w', 'a'), ('x', 'b'), ('y', 'c'), ('z', 'd'))), ('s', (('w', False), ('x', True), ('y', False), ('z', True))), ('t', (('w', True), ('x', False), ('y', False), ('z', True)))))


    def test_frame_reindex_b(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(
                f1.reindex(columns=('q', 'p', 'w'), fill_value=None).to_pairs(0),
                (('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('p', (('w', 1), ('x', 30), ('y', 54), ('z', 65))), ('w', (('w', None), ('x', None), ('y', None), ('z', None)))))

        self.assertEqual(
                f1.reindex(columns=('q', 'p', 's')).to_pairs(0),
                (('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('p', (('w', 1), ('x', 30), ('y', 54), ('z', 65))), ('s', (('w', False), ('x', True), ('y', False), ('z', True)))))

        f2 = f1[['p', 'q']]

        self.assertEqual(
                f2.reindex(columns=('q', 'p')).to_pairs(0),
                (('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('p', (('w', 1), ('x', 30), ('y', 54), ('z', 65)))))

        self.assertEqual(
                f2.reindex(columns=('a', 'b'), fill_value=None).to_pairs(0),
                (('a', (('w', None), ('x', None), ('y', None), ('z', None))), ('b', (('w', None), ('x', None), ('y', None), ('z', None)))))


    def test_frame_reindex_c(self):
        # reindex both axis
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))


        self.assertEqual(
                f1.reindex(index=('y', 'x'), columns=('s', 'q')).to_pairs(0),
                (('s', (('y', False), ('x', True))), ('q', (('y', 95), ('x', 34)))))

        self.assertEqual(
                f1.reindex(index=('x', 'y'), columns=('s', 'q', 'u'),
                        fill_value=None).to_pairs(0),
                (('s', (('x', True), ('y', False))), ('q', (('x', 34), ('y', 95))), ('u', (('x', None), ('y', None)))))

        self.assertEqual(
                f1.reindex(index=('a', 'b'), columns=('c', 'd'),
                        fill_value=None).to_pairs(0),
                (('c', (('a', None), ('b', None))), ('d', (('a', None), ('b', None)))))


        f2 = f1[['p', 'q']]

        self.assertEqual(
                f2.reindex(index=('x',), columns=('q',)).to_pairs(0),
                (('q', (('x', 34),)),))

        self.assertEqual(
                f2.reindex(index=('y', 'x', 'q'), columns=('q',),
                        fill_value=None).to_pairs(0),
                (('q', (('y', 95), ('x', 34), ('q', None))),))


    def test_frame_reindex_d(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )

        columns = IndexHierarchy.from_labels((('a', 1), ('a', 2), ('b', 1), ('b', 2), ('b', 3)))
        f1 = Frame.from_records(records,
                columns=columns,
                index=('x', 'y', 'z'))

        # NOTE: must use HLoc on getting a single columns as otherwise looks like a multiple axis selection
        self.assertEqual(f1[sf.HLoc['a', 1]].to_pairs(),
                (('x', 1), ('y', 30), ('z', 54))
                )

        self.assertEqual(f1[sf.HLoc['b', 1]:].to_pairs(0),
                ((('b', 1), (('x', 'a'), ('y', 'b'), ('z', 'c'))), (('b', 2), (('x', False), ('y', True), ('z', False))), (('b', 3), (('x', True), ('y', False), ('z', False)))))

        # reindexing with no column matches results in NaN for all values
        self.assertTrue(
                f1.iloc[:, 1:].reindex(columns=IndexHierarchy.from_product(('b', 'a'), (10, 20))).isna().all().all())

        columns = IndexHierarchy.from_product(('b', 'a'), (3, 2))
        f2 = f1.reindex(columns=columns, fill_value=None)
        self.assertEqual(f2.to_pairs(0),
                ((('b', 3), (('x', True), ('y', False), ('z', False))), (('b', 2), (('x', False), ('y', True), ('z', False))), (('a', 3), (('x', None), ('y', None), ('z', None))), (('a', 2), (('x', 2), ('y', 34), ('z', 95)))))


    def test_frame_reindex_e(self):

        records = (
                (1, 2, 'a', False),
                (30, 34, 'b', True),
                (54, 95, 'c', False),
                (65, 73, 'd', True),
                )

        columns = IndexHierarchy.from_product(('a', 'b'), (1, 2))
        index = IndexHierarchy.from_product((100, 200), (True, False))

        f1 = Frame.from_records(records,
                columns=columns,
                index=index)

        self.assertEqual(f1.loc[(200, True):, ('b',1):].to_pairs(0),
                ((('b', 1), (((200, True), 'c'), ((200, False), 'd'))), (('b', 2), (((200, True), False), ((200, False), True)))))

        # reindex from IndexHierarchy to Index with tuples
        f2 = f1.reindex(
                index=IndexHierarchy.from_product((200, 300), (False, True)),
                columns=[('b',1),('a',1)],
                fill_value=None)
        self.assertEqual(f2.to_pairs(0),
                ((('b', 1), (((200, False), 'd'), ((200, True), 'c'), ((300, False), None), ((300, True), None))), (('a', 1), (((200, False), 65), ((200, True), 54), ((300, False), None), ((300, True), None)))))

    def test_frame_axis_interface_a(self):
        # reindex both axis
        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                (65, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.to_pairs(1),
                (('w', (('p', 1), ('q', 2), ('r', 'a'), ('s', False), ('t', True))), ('x', (('p', 30), ('q', 34), ('r', 'b'), ('s', True), ('t', False))), ('y', (('p', 54), ('q', 95), ('r', 'c'), ('s', False), ('t', False))), ('z', (('p', 65), ('q', 73), ('r', 'd'), ('s', True), ('t', True)))))

        for x in f1.iter_tuple(0):
            self.assertTrue(len(x), 4)

        for x in f1.iter_tuple(1):
            self.assertTrue(len(x), 5)


        f2 = f1[['p', 'q']]

        s1 = f2.iter_array(0).apply(np.sum)
        self.assertEqual(list(s1.items()), [('p', 150), ('q', 204)])

        s2 = f2.iter_array(1).apply(np.sum)
        self.assertEqual(list(s2.items()),
                [('w', 3), ('x', 64), ('y', 149), ('z', 138)])

        def sum_if(idx, vals):
            if idx in ('x', 'z'):
                return np.sum(vals)

        s3 = f2.iter_array_items(1).apply(sum_if)
        self.assertEqual(list(s3.items()),
                [('w', None), ('x', 64), ('y', None), ('z', 138)])



    def test_frame_group_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = tuple(f1._axis_group_iloc_items(4, axis=0)) # row iter, group by column 4

        group1, group_frame_1 = post[0]
        group2, group_frame_2 = post[1]

        self.assertEqual(group1, False)
        self.assertEqual(group2, True)

        self.assertEqual(group_frame_1.to_pairs(0),
                (('p', (('w', 2), ('x', 30), ('y', 2))), ('q', (('w', 2), ('x', 34), ('y', 95))), ('r', (('w', 'a'), ('x', 'b'), ('y', 'c'))), ('s', (('w', False), ('x', True), ('y', False))), ('t', (('w', False), ('x', False), ('y', False)))))

        self.assertEqual(group_frame_2.to_pairs(0),
                (('p', (('z', 30),)), ('q', (('z', 73),)), ('r', (('z', 'd'),)), ('s', (('z', True),)), ('t', (('z', True),))))


    def test_frame_group_b(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        # column iter, group by row 0
        post = list(f1._axis_group_iloc_items(0, axis=1))

        self.assertEqual(post[0][0], 2)
        self.assertEqual(post[0][1].to_pairs(0),
                (('p', (('w', 2), ('x', 30), ('y', 2), ('z', 30))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73)))))

        self.assertEqual(post[1][0], False)
        self.assertEqual(post[1][1].to_pairs(0),
                (('s', (('w', False), ('x', True), ('y', False), ('z', True))), ('t', (('w', False), ('x', False), ('y', False), ('z', True)))))

        self.assertEqual(post[2][0], 'a')

        self.assertEqual(post[2][1].to_pairs(0),
                (('r', (('w', 'a'), ('x', 'b'), ('y', 'c'), ('z', 'd'))),))



    def test_frame_axis_interface_b(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = list(f1.iter_group_items('s', axis=0))

        self.assertEqual(post[0][1].to_pairs(0),
                (('p', (('w', 2), ('y', 2))), ('q', (('w', 2), ('y', 95))), ('r', (('w', 'a'), ('y', 'c'))), ('s', (('w', False), ('y', False))), ('t', (('w', False), ('y', False)))))

        self.assertEqual(post[1][1].to_pairs(0),
                (('p', (('x', 30), ('z', 30))), ('q', (('x', 34), ('z', 73))), ('r', (('x', 'b'), ('z', 'd'))), ('s', (('x', True), ('z', True))), ('t', (('x', False), ('z', True)))))


        s1 = f1.iter_group('p', axis=0).apply(lambda f: f['q'].values.sum())
        self.assertEqual(list(s1.items()), [(2, 97), (30, 107)])


    def test_frame_contains_a(self):

        f1 = Frame.from_items(zip(('a', 'b'), ([20, 30, 40], [80, 10, 30])),
                index=('x', 'y', 'z'))

        self.assertTrue('a' in f1)
        self.assertTrue('b' in f1)
        self.assertFalse('x' in f1)
        self.assertFalse('y' in f1)



    def test_frame_sum_a(self):
        # reindex both axis
        records = (
                (2, 2, 3, 4.23, 50.234),
                (30, 34, 60, 80.6, 90.123),
                (2, 95, 1, 1.96, 1.54),
                (30, 73, 50, 40.23, 30.234),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = f1.sum(axis=0)
        self.assertAlmostEqualItems(list(post.items()),
                [('p', 64.0), ('q', 204.0), ('r', 114.0), ('s', 127.01999999999998), ('t', 172.131)])
        self.assertEqual(post.dtype, np.float64)

        post = f1.sum(axis=1) # sum columns, return row index
        self.assertEqual(list(f1.sum(axis=1).items()),
                [('w', 61.463999999999999), ('x', 294.72300000000001), ('y', 101.5), ('z', 223.464)])
        self.assertEqual(post.dtype, np.float64)


    def test_frame_sum_b(self):

        records = (
                (2, 2, 3),
                (30, 34, 60),
                (2, 95, 1),
                (30, 73, 50),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        post = f1.sum(axis=0)

        self.assertEqual(list(post.items()),
                [('p', 64), ('q', 204), ('r', 114)])

        self.assertEqual(list(f1.sum(axis=1).items()),
                [('w', 7), ('x', 124), ('y', 98), ('z', 153)])


    def test_frame_min_a(self):
        # reindex both axis
        records = (
                (2, 2, 3, 4.23, 50.234),
                (30, 34, 60, 80.6, 90.123),
                (2, 95, 1, 1.96, 1.54),
                (30, 73, 50, 40.23, 30.234),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertAlmostEqualItems(tuple(f1.min().items()),
                (('p', 2.0), ('q', 2.0), ('r', 1.0), ('s', 1.96), ('t', 1.54)))

        self.assertAlmostEqualItems(tuple(f1.min(axis=1).items()),
                (('w', 2.0), ('x', 30.0), ('y', 1.0), ('z', 30.0)))

    def test_frame_row_dtype_a(self):
        # reindex both axis
        records = (
                (2, 2, 3, 4.23, 50.234),
                (30, 34, 60, 80.6, 90.123),
                (2, 95, 1, 1.96, 1.54),
                (30, 73, 50, 40.23, 30.234),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1['t'].dtype, np.float64)
        self.assertEqual(f1['p'].dtype, np.int64)

        self.assertEqual(f1.loc['w'].dtype, np.float64)
        self.assertEqual(f1.loc['z'].dtype, np.float64)

        self.assertEqual(f1[['r', 's']].values.dtype, np.float64)

    def test_frame_unary_operator_a(self):

        records = (
                (2, 2, 3, False, True),
                (30, 34, 60, True, False),
                (2, 95, 1, True, True),
                (30, 73, 50, False, False),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        # raises exception with NP14
        # self.assertEqual((-f1).to_pairs(0),
        #         (('p', (('w', -2), ('x', -30), ('y', -2), ('z', -30))), ('q', (('w', -2), ('x', -34), ('y', -95), ('z', -73))), ('r', (('w', -3), ('x', -60), ('y', -1), ('z', -50))), ('s', (('w', True), ('x', False), ('y', False), ('z', True))), ('t', (('w', False), ('x', True), ('y', False), ('z', True)))))

        self.assertEqual((~f1).to_pairs(0),
                (('p', (('w', -3), ('x', -31), ('y', -3), ('z', -31))), ('q', (('w', -3), ('x', -35), ('y', -96), ('z', -74))), ('r', (('w', -4), ('x', -61), ('y', -2), ('z', -51))), ('s', (('w', True), ('x', False), ('y', False), ('z', True))), ('t', (('w', False), ('x', True), ('y', False), ('z', True)))))


    def test_frame_binary_operator_a(self):
        # constants

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual((f1 * 30).to_pairs(0),
                (('p', (('w', 60), ('x', 900), ('y', 60), ('z', 900))), ('q', (('w', 60), ('x', 1020), ('y', 2850), ('z', 2190))), ('r', (('w', 105.0), ('x', 1806.0), ('y', 36.0), ('z', 1506.0))))
                )



    def test_frame_binary_operator_b(self):

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        f2 = f1.loc[['y', 'z'], ['r']]
        f3 = f1 * f2

        self.assertAlmostEqualItems(list(f3['p'].items()),
                [('w', nan), ('x', nan), ('y', nan), ('z', nan)])
        self.assertAlmostEqualItems(list(f3['r'].items()),
                [('w', nan), ('x', nan), ('y', 1.4399999999999999), ('z', 2520.0400000000004)])

    def test_frame_binary_operator_c(self):

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        s1 = Series([0, 1, 2], index=('r', 'q', 'p'))

        self.assertEqual((f1 * s1).to_pairs(0),
                (('p', (('w', 4), ('x', 60), ('y', 4), ('z', 60))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('r', (('w', 0.0), ('x', 0.0), ('y', 0.0), ('z', 0.0)))))

        self.assertEqual((f1 * [0, 1, 0]).to_pairs(0),
                (('p', (('w', 0), ('x', 0), ('y', 0), ('z', 0))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73))), ('r', (('w', 0.0), ('x', 0.0), ('y', 0.0), ('z', 0.0)))))


    def test_frame_isin_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        post = f1.isin({'a', 73, 30})
        self.assertEqual(post.to_pairs(0),
                (('p', (('w', False), ('x', True), ('y', False), ('z', True))), ('q', (('w', False), ('x', False), ('y', False), ('z', True))), ('r', (('w', True), ('x', False), ('y', False), ('z', False))), ('s', (('w', False), ('x', False), ('y', False), ('z', False))), ('t', (('w', False), ('x', False), ('y', False), ('z', False)))))


        post = f1.isin(['a', 73, 30])
        self.assertEqual(post.to_pairs(0),
                (('p', (('w', False), ('x', True), ('y', False), ('z', True))), ('q', (('w', False), ('x', False), ('y', False), ('z', True))), ('r', (('w', True), ('x', False), ('y', False), ('z', False))), ('s', (('w', False), ('x', False), ('y', False), ('z', False))), ('t', (('w', False), ('x', False), ('y', False), ('z', False)))))


    def test_frame_transpose_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        f2 = f1.transpose()

        self.assertEqual(f2.to_pairs(0),
                (('w', (('p', 2), ('q', 2), ('r', 'a'), ('s', False), ('t', False))), ('x', (('p', 30), ('q', 34), ('r', 'b'), ('s', True), ('t', False))), ('y', (('p', 2), ('q', 95), ('r', 'c'), ('s', False), ('t', False))), ('z', (('p', 30), ('q', 73), ('r', 'd'), ('s', True), ('t', True)))))



    def test_frame_from_element_iloc_items_a(self):
        items = (((0,1), 'g'), ((1,0), 'q'))

        f1 = Frame.from_element_iloc_items(items,
                index=('a', 'b'),
                columns=('x', 'y'),
                dtype=object
                )

        self.assertEqual(f1.to_pairs(0),
                (('x', (('a', None), ('b', 'q'))), ('y', (('a', 'g'), ('b', None)))))


        items = (((0,1), .5), ((1,0), 1.5))

        f2 = Frame.from_element_iloc_items(items,
                index=('a', 'b'),
                columns=('x', 'y'),
                dtype=float
                )

        self.assertAlmostEqualItems(tuple(f2['x'].items()),
                (('a', nan), ('b', 1.5)))

        self.assertAlmostEqualItems(tuple(f2['y'].items()),
                (('a', 0.5), ('b', nan)))


    def test_frame_from_element_loc_items_a(self):
        items = ((('b', 'x'), 'g'), (('a','y'), 'q'))

        f1 = Frame.from_element_loc_items(items,
                index=('a', 'b'),
                columns=('x', 'y'),
                dtype=object
                )

        self.assertEqual(f1.to_pairs(0),
                (('x', (('a', None), ('b', 'g'))), ('y', (('a', 'q'), ('b', None)))))



    def test_frame_iter_element_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(
                [x for x in f1.iter_element()],
                [2, 2, 'a', False, False, 30, 34, 'b', True, False, 2, 95, 'c', False, False, 30, 73, 'd', True, True])

        self.assertEqual([x for x in f1.iter_element_items()],
                [(('w', 'p'), 2), (('w', 'q'), 2), (('w', 'r'), 'a'), (('w', 's'), False), (('w', 't'), False), (('x', 'p'), 30), (('x', 'q'), 34), (('x', 'r'), 'b'), (('x', 's'), True), (('x', 't'), False), (('y', 'p'), 2), (('y', 'q'), 95), (('y', 'r'), 'c'), (('y', 's'), False), (('y', 't'), False), (('z', 'p'), 30), (('z', 'q'), 73), (('z', 'r'), 'd'), (('z', 's'), True), (('z', 't'), True)])


        post = f1.iter_element().apply(lambda x: '_' + str(x) + '_')

        self.assertEqual(post.to_pairs(0),
                (('p', (('w', '_2_'), ('x', '_30_'), ('y', '_2_'), ('z', '_30_'))), ('q', (('w', '_2_'), ('x', '_34_'), ('y', '_95_'), ('z', '_73_'))), ('r', (('w', '_a_'), ('x', '_b_'), ('y', '_c_'), ('z', '_d_'))), ('s', (('w', '_False_'), ('x', '_True_'), ('y', '_False_'), ('z', '_True_'))), ('t', (('w', '_False_'), ('x', '_False_'), ('y', '_False_'), ('z', '_True_')))))




    def test_frame_iter_element_b(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        # support working with mappings
        post = f1.iter_element().apply({2: 200, False: 200})

        self.assertEqual(post.to_pairs(0),
                (('p', (('w', 200), ('x', 30), ('y', 200), ('z', 30))), ('q', (('w', 200), ('x', 34), ('y', 95), ('z', 73))), ('r', (('w', 'a'), ('x', 'b'), ('y', 'c'), ('z', 'd'))), ('s', (('w', 200), ('x', True), ('y', 200), ('z', True))), ('t', (('w', 200), ('x', 200), ('y', 200), ('z', True))))
                )


    def test_frame_sort_index_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('z', 'x', 'w', 'y'))

        self.assertEqual(f1.sort_index().to_pairs(0),
                (('p', (('w', 2), ('x', 30), ('y', 30), ('z', 2))), ('q', (('w', 95), ('x', 34), ('y', 73), ('z', 2))), ('r', (('w', 'c'), ('x', 'b'), ('y', 'd'), ('z', 'a'))), ('s', (('w', False), ('x', True), ('y', True), ('z', False))), ('t', (('w', False), ('x', False), ('y', True), ('z', False)))))


        self.assertEqual(f1.sort_index(ascending=False).to_pairs(0),
                (('p', (('z', 2), ('y', 30), ('x', 30), ('w', 2))), ('q', (('z', 2), ('y', 73), ('x', 34), ('w', 95))), ('r', (('z', 'a'), ('y', 'd'), ('x', 'b'), ('w', 'c'))), ('s', (('z', False), ('y', True), ('x', True), ('w', False))), ('t', (('z', False), ('y', True), ('x', False), ('w', False)))))


    def test_frame_sort_columns_a(self):
        # reindex both axis
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('t', 's', 'r', 'q', 'p'),
                index=('z', 'x', 'w', 'y'))

        self.assertEqual(
                f1.sort_columns().to_pairs(0),
                (('p', (('z', False), ('x', False), ('w', False), ('y', True))), ('q', (('z', False), ('x', True), ('w', False), ('y', True))), ('r', (('z', 'a'), ('x', 'b'), ('w', 'c'), ('y', 'd'))), ('s', (('z', 2), ('x', 34), ('w', 95), ('y', 73))), ('t', (('z', 2), ('x', 30), ('w', 2), ('y', 30)))))



    def test_frame_sort_values_a(self):
        # reindex both axis
        records = (
                (2, 2, 'c', False, False),
                (30, 34, 'd', True, False),
                (2, 95, 'a', False, False),
                (30, 73, 'b', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'r', 'q', 't', 's'),
                index=('z', 'x', 'w', 'y'))

        post = f1.sort_values('q')


        self.assertEqual(post.to_pairs(0),
                (('p', (('w', 2), ('y', 30), ('z', 2), ('x', 30))), ('r', (('w', 95), ('y', 73), ('z', 2), ('x', 34))), ('q', (('w', 'a'), ('y', 'b'), ('z', 'c'), ('x', 'd'))), ('t', (('w', False), ('y', True), ('z', False), ('x', True))), ('s', (('w', False), ('y', True), ('z', False), ('x', False)))))


        self.assertEqual(f1.sort_values('p').to_pairs(0),
                (('p', (('z', 2), ('w', 2), ('x', 30), ('y', 30))), ('r', (('z', 2), ('w', 95), ('x', 34), ('y', 73))), ('q', (('z', 'c'), ('w', 'a'), ('x', 'd'), ('y', 'b'))), ('t', (('z', False), ('w', False), ('x', True), ('y', True))), ('s', (('z', False), ('w', False), ('x', False), ('y', True))))
                )


    def test_frame_sort_values_b(self):
        # reindex both axis
        records = (
                (2, 2, 'c', False, False),
                (30, 34, 'd', True, False),
                (2, 95, 'a', True, False),
                (30, 73, 'b', False, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'r', 'q', 't', 's'),
                index=('z', 'x', 'w', 'y'))

        post = f1.sort_values(('p', 't'))

        self.assertEqual(post.to_pairs(0),
                (('p', (('z', 2), ('w', 2), ('y', 30), ('x', 30))), ('r', (('z', 2), ('w', 95), ('y', 73), ('x', 34))), ('q', (('z', 'c'), ('w', 'a'), ('y', 'b'), ('x', 'd'))), ('t', (('z', False), ('w', True), ('y', False), ('x', True))), ('s', (('z', False), ('w', False), ('y', True), ('x', False)))))



    def test_frame_sort_values_c(self):

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.sort_values('y', axis=0).to_pairs(0),
                (('r', (('w', 3.5), ('x', 60.2), ('y', 1.2), ('z', 50.2))), ('p', (('w', 2), ('x', 30), ('y', 2), ('z', 30))), ('q', (('w', 2), ('x', 34), ('y', 95), ('z', 73)))))



    def test_frame_relabel_a(self):
        # reindex both axis
        records = (
                (2, 2, 'c', False, False),
                (30, 34, 'd', True, False),
                (2, 95, 'a', False, False),
                (30, 73, 'b', True, True),
                )

        f1 = FrameGO.from_records(records,
                columns=('p', 'r', 'q', 't', 's'),
                index=('z', 'x', 'w', 'y'))

        f2 = f1.relabel(columns={'q': 'QQQ'})

        self.assertEqual(f2.to_pairs(0),
                (('p', (('z', 2), ('x', 30), ('w', 2), ('y', 30))), ('r', (('z', 2), ('x', 34), ('w', 95), ('y', 73))), ('QQQ', (('z', 'c'), ('x', 'd'), ('w', 'a'), ('y', 'b'))), ('t', (('z', False), ('x', True), ('w', False), ('y', True))), ('s', (('z', False), ('x', False), ('w', False), ('y', True))))
                )

        f3 = f1.relabel(index={'y': 'YYY'})

        self.assertEqual(f3.to_pairs(0),
                (('p', (('z', 2), ('x', 30), ('w', 2), ('YYY', 30))), ('r', (('z', 2), ('x', 34), ('w', 95), ('YYY', 73))), ('q', (('z', 'c'), ('x', 'd'), ('w', 'a'), ('YYY', 'b'))), ('t', (('z', False), ('x', True), ('w', False), ('YYY', True))), ('s', (('z', False), ('x', False), ('w', False), ('YYY', True)))))

        self.assertTrue((f1.mloc == f2.mloc).all())
        self.assertTrue((f2.mloc == f3.mloc).all())


    def test_frame_get_a(self):
        # reindex both axis
        records = (
                (2, 2, 'c', False, False),
                (30, 34, 'd', True, False),
                (2, 95, 'a', False, False),
                (30, 73, 'b', True, True),
                )

        f1 = FrameGO.from_records(records,
                columns=('p', 'r', 'q', 't', 's'),
                index=('z', 'x', 'w', 'y'))

        self.assertEqual(f1.get('r').values.tolist(),
                [2, 34, 95, 73])

        self.assertEqual(f1.get('a'), None)
        self.assertEqual(f1.get('w'), None)
        self.assertEqual(f1.get('a', -1), -1)

    def test_frame_isna_a(self):
        f1 = FrameGO([
                [np.nan, 2, np.nan, 0],
                [3, 4, np.nan, 1],
                [np.nan, np.nan, np.nan, 5]],
                columns=list('ABCD'))

        self.assertEqual(f1.isna().to_pairs(0),
                (('A', ((0, True), (1, False), (2, True))), ('B', ((0, False), (1, False), (2, True))), ('C', ((0, True), (1, True), (2, True))), ('D', ((0, False), (1, False), (2, False)))))

        self.assertEqual(f1.notna().to_pairs(0),
                (('A', ((0, False), (1, True), (2, False))), ('B', ((0, True), (1, True), (2, False))), ('C', ((0, False), (1, False), (2, False))), ('D', ((0, True), (1, True), (2, True)))))

    def test_frame_dropna_a(self):
        f1 = FrameGO([
                [np.nan, 2, np.nan, 0],
                [3, 4, np.nan, 1],
                [np.nan, np.nan, np.nan, np.nan]],
                columns=list('ABCD'))

        self.assertAlmostEqualFramePairs(
                f1.dropna(axis=0, condition=np.all).to_pairs(0),
                (('A', ((0, nan), (1, 3.0))), ('B', ((0, 2.0), (1, 4.0))), ('C', ((0, nan), (1, nan))), ('D', ((0, 0.0), (1, 1.0)))))

        self.assertAlmostEqualFramePairs(
                f1.dropna(axis=1, condition=np.all).to_pairs(0),
                (('A', ((0, nan), (1, 3.0), (2, nan))), ('B', ((0, 2.0), (1, 4.0), (2, nan))), ('D', ((0, 0.0), (1, 1.0), (2, nan)))))


        f2 = f1.dropna(axis=0, condition=np.any)
        # dropping to zero results in an empty DF in the same manner as Pandas; not sure if this is correct or ideal
        self.assertEqual(f2.shape, (0, 4))

        f3 = f1.dropna(axis=1, condition=np.any)
        self.assertEqual(f3.shape, (0, 0))

    def test_frame_dropna_b(self):
        f1 = FrameGO([
                [np.nan, 2, 3, 0],
                [3, 4, np.nan, 1],
                [0, 1, 2, 3]],
                columns=list('ABCD'))

        self.assertEqual(f1.dropna(axis=0, condition=np.any).to_pairs(0),
                (('A', ((2, 0.0),)), ('B', ((2, 1.0),)), ('C', ((2, 2.0),)), ('D', ((2, 3.0),))))
        self.assertEqual(f1.dropna(axis=1, condition=np.any).to_pairs(0),
                (('B', ((0, 2.0), (1, 4.0), (2, 1.0))), ('D', ((0, 0.0), (1, 1.0), (2, 3.0)))))



    def test_frame_fillna_a(self):
        dtype = np.dtype

        f1 = FrameGO([
                [np.nan, 2, 3, 0],
                [3, 4, np.nan, 1],
                [0, 1, 2, 3]],
                columns=list('ABCD'))

        f2 = f1.fillna(0)
        self.assertEqual(f2.to_pairs(0),
                (('A', ((0, 0.0), (1, 3.0), (2, 0.0))), ('B', ((0, 2.0), (1, 4.0), (2, 1.0))), ('C', ((0, 3.0), (1, 0.0), (2, 2.0))), ('D', ((0, 0.0), (1, 1.0), (2, 3.0)))))

        post = f2.dtypes
        self.assertEqual(post.to_pairs(),
                (('A', dtype('float64')), ('B', dtype('float64')), ('C', dtype('float64')), ('D', dtype('float64'))))

        f3 = f1.fillna(None)
        self.assertEqual(f3.to_pairs(0),
                (('A', ((0, None), (1, 3.0), (2, 0.0))), ('B', ((0, 2.0), (1, 4.0), (2, 1.0))), ('C', ((0, 3.0), (1, None), (2, 2.0))), ('D', ((0, 0.0), (1, 1.0), (2, 3.0)))))

        post = f3.dtypes
        self.assertEqual(post.to_pairs(),
                (('A', dtype('O')), ('B', dtype('O')), ('C', dtype('O')), ('D', dtype('O'))))


    def test_frame_empty_a(self):

        f1 = FrameGO(index=('a', 'b', 'c'))
        f1['w'] = Series.from_items(zip('cebga', (10, 20, 30, 40, 50)))
        f1['x'] = Series.from_items(zip('abc', range(3, 6)))
        f1['y'] = Series.from_items(zip('abcd', range(2, 6)))
        f1['z'] = Series.from_items(zip('qabc', range(7, 11)))

        self.assertEqual(f1.to_pairs(0),
                (('w', (('a', 50), ('b', 30), ('c', 10))), ('x', (('a', 3), ('b', 4), ('c', 5))), ('y', (('a', 2), ('b', 3), ('c', 4))), ('z', (('a', 8), ('b', 9), ('c', 10)))))


    def test_frame_from_csv_a(self):
        # header, mixed types, no index

        s1 = StringIO('count,score,color\n1,1.3,red\n3,5.2,green\n100,3.4,blue\n4,9.0,black')

        f1 = Frame.from_csv(s1)
        post = f1.iloc[:, :2].sum(axis=0)
        self.assertEqual(post.to_pairs(),
                (('count', 108.0), ('score', 18.9)))
        self.assertEqual(f1.shape, (4, 3))
        self.assertEqual(f1.dtypes.iter_element().apply(str).to_pairs(),
                (('count', 'int64'), ('score', 'float64'), ('color', '<U5')))

        s2 = StringIO('color,count,score\nred,1,1.3\ngreen,3,5.2\nblue,100,3.4\nblack,4,9.0')

        f2 = Frame.from_csv(s2)
        self.assertEqual(f2['count':].sum().to_pairs(),
                (('count', 108.0), ('score', 18.9)))
        self.assertEqual(f2.shape, (4, 3))
        self.assertEqual(f2.dtypes.iter_element().apply(str).to_pairs(),
                (('color', '<U5'), ('count', 'int64'), ('score', 'float64')))


        # add junk at beginning and end
        s3 = StringIO('junk\ncolor,count,score\nred,1,1.3\ngreen,3,5.2\nblue,100,3.4\nblack,4,9.0\njunk')

        f3 = Frame.from_csv(s3, skip_header=1, skip_footer=1)
        self.assertEqual(f3.shape, (4, 3))
        self.assertEqual(f3.dtypes.iter_element().apply(str).to_pairs(),
                (('color', '<U5'), ('count', 'int64'), ('score', 'float64')))



    def test_frame_from_csv_b(self):
        filelike = StringIO('''count,number,weight,scalar,color,active
0,4,234.5,5.3,'red',False
30,50,9.234,5.434,'blue',True''')
        f1 = Frame.from_csv(filelike)

        self.assertEqual(f1.columns.values.tolist(),
                ['count', 'number', 'weight', 'scalar', 'color', 'active'])


    def test_frame_from_csv_c(self):

        s1 = StringIO('color,count,score\nred,1,1.3\ngreen,3,5.2\nblue,100,3.4\nblack,4,9.0')
        f1 = Frame.from_csv(s1, index_column='color')
        self.assertEqual(f1.to_pairs(0),
                (('count', (('red', 1), ('green', 3), ('blue', 100), ('black', 4))), ('score', (('red', 1.3), ('green', 5.2), ('blue', 3.4), ('black', 9.0)))))


    def test_frame_to_csv_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        file = StringIO()
        f1.to_csv(file)
        file.seek(0)
        self.assertEqual(file.read(),
'index,p,q,r,s,t\nw,2,2,a,False,False\nx,30,34,b,True,False\ny,2,95,c,False,False\nz,30,73,d,True,True')

        file = StringIO()
        f1.to_csv(file, include_index=False)
        file.seek(0)
        self.assertEqual(file.read(),
'p,q,r,s,t\n2,2,a,False,False\n30,34,b,True,False\n2,95,c,False,False\n30,73,d,True,True')

        file = StringIO()
        f1.to_csv(file, include_index=False, include_columns=False)
        file.seek(0)
        self.assertEqual(file.read(),
'2,2,a,False,False\n30,34,b,True,False\n2,95,c,False,False\n30,73,d,True,True')


    def test_frame_to_tsv_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))

        file = StringIO()
        f1.to_tsv(file)
        file.seek(0)
        self.assertEqual(file.read(),
'index\tp\tq\tr\ts\tt\nw\t2\t2\ta\tFalse\tFalse\nx\t30\t34\tb\tTrue\tFalse\ny\t2\t95\tc\tFalse\tFalse\nz\t30\t73\td\tTrue\tTrue')




    def test_frame_and_a(self):

        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('w', 'x', 'y', 'z'))
        f2 = FrameGO([
                [np.nan, 2, 3, 0],
                [3, 4, np.nan, 1],
                [0, 1, 2, 3]],
                columns=list('ABCD'))

        self.assertEqual(f1.all(axis=0).to_pairs(),
                (('p', True), ('q', True), ('r', True), ('s', False), ('t', False)))

        self.assertEqual(f1.any(axis=0).to_pairs(),
                (('p', True), ('q', True), ('r', True), ('s', True), ('t', True)))

        self.assertEqual(f1.all(axis=1).to_pairs(),
                (('w', False), ('x', False), ('y', False), ('z', True)))

        self.assertEqual(f1.any(axis=1).to_pairs(),
                (('w', True), ('x', True), ('y', True), ('z', True)))



    def test_frame_unique_a(self):

        records = (
                (2, 2, 3.5),
                (30, 34, 60.2),
                (2, 95, 1.2),
                (30, 73, 50.2),
                )
        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f1.unique().tolist(),
                [1.2, 2.0, 3.5, 30.0, 34.0, 50.2, 60.2, 73.0, 95.0])

        records = (
                (2, 2, 2),
                (30, 34, 34),
                (2, 2, 2),
                (30, 73, 73),
                )
        f2 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('w', 'x', 'y', 'z'))

        self.assertEqual(f2.unique().tolist(), [2, 30, 34, 73])

        self.assertEqual(f2.unique(axis=0).tolist(),
                [[2, 2, 2], [30, 34, 34], [30, 73, 73]])
        self.assertEqual(f2.unique(axis=1).tolist(),
                [[2, 2], [30, 34], [2, 2], [30, 73]])


    def test_frame_duplicated_a(self):

        a1 = np.array([[50, 50, 32, 17, 17], [2,2,1,3,3]])
        f1 = Frame(a1, index=('a', 'b'), columns=('p', 'q', 'r', 's','t'))

        self.assertEqual(f1.duplicated(axis=1).to_pairs(),
                (('p', True), ('q', True), ('r', False), ('s', True), ('t', True)))

        self.assertEqual(f1.duplicated(axis=0).to_pairs(),
                (('a', False), ('b', False)))


    def test_frame_duplicated_b(self):

        a1 = np.array([[50, 50, 32, 17, 17], [2,2,1,3,3]])
        f1 = Frame(a1, index=('a', 'b'), columns=('p', 'q', 'r', 's','t'))

        self.assertEqual(f1.drop_duplicated(axis=1, exclude_first=True).to_pairs(1),
                (('a', (('p', 50), ('r', 32), ('s', 17))), ('b', (('p', 2), ('r', 1), ('s', 3)))))

    def test_frame_from_concat_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'a'))

        records = (
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f2 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'a'))

        records = (
                (2, 2, 'a', False, False),
                (30, 73, 'd', True, True),
                )

        f3 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'a'))

        f = Frame.from_concat((f1, f2, f3), axis=1, columns=range(15))

        # no blocks are copied or reallcoated
        self.assertEqual(f.mloc.tolist(),
                f1.mloc.tolist() + f2.mloc.tolist() + f3.mloc.tolist()
                )
        # order of index is retained
        self.assertEqual(f.to_pairs(1),
                (('x', ((0, 2), (1, 2), (2, 'a'), (3, False), (4, False), (5, 2), (6, 95), (7, 'c'), (8, False), (9, False), (10, 2), (11, 2), (12, 'a'), (13, False), (14, False))), ('a', ((0, 30), (1, 34), (2, 'b'), (3, True), (4, False), (5, 30), (6, 73), (7, 'd'), (8, True), (9, True), (10, 30), (11, 73), (12, 'd'), (13, True), (14, True)))))


    def test_frame_from_concat_b(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'a'))

        records = (
                (2, 95, 'c', False, False),
                (30, 73, 'd', True, True),
                )

        f2 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'b'))

        records = (
                (2, 2, 'a', False, False),
                (30, 73, 'd', True, True),
                )

        f3 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'c'))

        f = Frame.from_concat((f1, f2, f3), axis=1, columns=range(15))

        self.assertEqual(f.index.values.tolist(),
                ['a', 'b', 'c', 'x'])

        self.assertAlmostEqualFramePairs(f.to_pairs(1),
                (('a', ((0, 30), (1, 34), (2, 'b'), (3, True), (4, False), (5, nan), (6, nan), (7, nan), (8, nan), (9, nan), (10, nan), (11, nan), (12, nan), (13, nan), (14, nan))), ('b', ((0, nan), (1, nan), (2, nan), (3, nan), (4, nan), (5, 30), (6, 73), (7, 'd'), (8, True), (9, True), (10, nan), (11, nan), (12, nan), (13, nan), (14, nan))), ('c', ((0, nan), (1, nan), (2, nan), (3, nan), (4, nan), (5, nan), (6, nan), (7, nan), (8, nan), (9, nan), (10, 30), (11, 73), (12, 'd'), (13, True), (14, True))), ('x', ((0, 2), (1, 2), (2, 'a'), (3, False), (4, False), (5, 2), (6, 95), (7, 'c'), (8, False), (9, False), (10, 2), (11, 2), (12, 'a'), (13, False), (14, False))))
                )


        f = Frame.from_concat((f1, f2, f3), union=False, axis=1, columns=range(15))

        self.assertEqual(f.index.values.tolist(),
                ['x'])
        self.assertEqual(f.to_pairs(0),
                ((0, (('x', 2),)), (1, (('x', 2),)), (2, (('x', 'a'),)), (3, (('x', False),)), (4, (('x', False),)), (5, (('x', 2),)), (6, (('x', 95),)), (7, (('x', 'c'),)), (8, (('x', False),)), (9, (('x', False),)), (10, (('x', 2),)), (11, (('x', 2),)), (12, (('x', 'a'),)), (13, (('x', False),)), (14, (('x', False),))))


    def test_frame_from_concat_c(self):
        records = (
                (2, 2, False),
                (30, 34, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 't'),
                index=('x', 'a'))

        records = (
                ('c', False),
                ('d', True),
                )
        f2 = Frame.from_records(records,
                columns=('r', 's',),
                index=('x', 'a'))

        # get combined columns as they are unique
        f = Frame.from_concat((f1, f2), axis=1)
        self.assertEqual(f.to_pairs(0),
                (('p', (('x', 2), ('a', 30))), ('q', (('x', 2), ('a', 34))), ('t', (('x', False), ('a', False))), ('r', (('x', 'c'), ('a', 'd'))), ('s', (('x', False), ('a', True))))
                )


    def test_frame_from_concat_d(self):
        records = (
                (2, 2, False),
                (30, 34, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('a', 'b'))

        records = (
                (2, 2, False),
                (30, 34, False),
                )

        f2 = Frame.from_records(records,
                columns=('p', 'q', 'r'),
                index=('c', 'd'))

        f = Frame.from_concat((f1, f2), axis=0)

        # block copmatible will result in attempt to keep vertical types
        self.assertEqual(
                [str(x) for x in f.dtypes.values.tolist()],
                ['int64', 'int64', 'bool'])

        self.assertEqual(f.to_pairs(0),
                (('p', (('a', 2), ('b', 30), ('c', 2), ('d', 30))), ('q', (('a', 2), ('b', 34), ('c', 2), ('d', 34))), ('r', (('a', False), ('b', False), ('c', False), ('d', False)))))


    def test_frame_from_concat_e(self):

        f1 = Frame.from_items(zip(
                ('a', 'b', 'c'),
                ((1, 2), (1, 2), (False, True))
                ))

        f = Frame.from_concat((f1, f1, f1), index=range(6))
        self.assertEqual(
                f.to_pairs(0),
                (('a', ((0, 1), (1, 2), (2, 1), (3, 2), (4, 1), (5, 2))), ('b', ((0, 1), (1, 2), (2, 1), (3, 2), (4, 1), (5, 2))), ('c', ((0, False), (1, True), (2, False), (3, True), (4, False), (5, True)))))
        self.assertEqual(
                [str(x) for x in f.dtypes.values.tolist()],
                ['int64', 'int64', 'bool'])

        f = Frame.from_concat((f1, f1, f1), axis=1, columns=range(9))

        self.assertEqual(f.to_pairs(0),
                ((0, ((0, 1), (1, 2))), (1, ((0, 1), (1, 2))), (2, ((0, False), (1, True))), (3, ((0, 1), (1, 2))), (4, ((0, 1), (1, 2))), (5, ((0, False), (1, True))), (6, ((0, 1), (1, 2))), (7, ((0, 1), (1, 2))), (8, ((0, False), (1, True)))))

        self.assertEqual([str(x) for x in f.dtypes.values.tolist()],
                ['int64', 'int64', 'bool', 'int64', 'int64', 'bool', 'int64', 'int64', 'bool'])

    def test_frame_from_concat_f(self):
        # force a reblock before concatenating

        a1 = np.array([1, 2, 3])
        a2 = np.array([10,50,30])
        a3 = np.array([1345,2234,3345])
        a4 = np.array([False, True, False])
        a5 = np.array([False, False, False])
        a6 = np.array(['g', 'd', 'e'])
        tb1 = TypeBlocks.from_blocks((a1, a2, a3, a4, a5, a6))

        f1 = Frame(TypeBlocks.from_blocks((a1, a2, a3, a4, a5, a6)),
                columns = ('a', 'b', 'c', 'd', 'e', 'f'),
                own_data=True)
        self.assertEqual(len(f1._blocks._blocks), 6)

        f2 = Frame(f1.iloc[1:]._blocks.consolidate(),
                columns = ('a', 'b', 'c', 'd', 'e', 'f'),
                own_data=True)
        self.assertEqual(len(f2._blocks._blocks), 3)

        f = Frame.from_concat((f1 ,f2), index=range(5))

        self.assertEqual(
                [str(x) for x in f.dtypes.values.tolist()],
                ['int64', 'int64', 'int64', 'bool', 'bool', '<U1'])

        self.assertEqual(
                [str(x.dtype) for x in f._blocks._blocks],
                ['int64', 'bool', '<U1'])


    def test_frame_from_concat_g(self):
        records = (
                (2, 2, False),
                (30, 34, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 't'),
                index=('x', 'a'))

        records = (
                ('c', False),
                ('d', True),
                )
        f2 = Frame.from_records(records,
                columns=('r', 's',),
                index=('x', 'a'))

        # get combined columns as they are unique
        f = Frame.from_concat((f1, f2), axis=1)
        self.assertEqual(f.to_pairs(0),
                (('p', (('x', 2), ('a', 30))), ('q', (('x', 2), ('a', 34))), ('t', (('x', False), ('a', False))), ('r', (('x', 'c'), ('a', 'd'))), ('s', (('x', False), ('a', True))))
                )


    def test_frame_from_concat_h(self):

        index = list(''.join(x) for x in it.combinations(string.ascii_lowercase, 3))
        columns = list(''.join(x) for x in it.combinations(string.ascii_uppercase, 2))
        data = np.random.rand(len(index), len(columns))
        f1 = Frame(data, index=index, columns=columns)

        f2 = f1[[c for c in f1.columns if c.startswith('D')]]
        f3 = f1[[c for c in f1.columns if c.startswith('G')]]
        post = sf.Frame.from_concat((f2, f3), axis=1)

        # this form of concatenation has no copy
        assert post.mloc.tolist() == [f2.mloc[0], f3.mloc[0]]
        self.assertEqual(post.shape, (2600, 41))


    def test_frame_set_index_a(self):
        records = (
                (2, 2, 'a', False, False),
                (30, 34, 'b', True, False),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=('x', 'y'))

        self.assertEqual(f1.set_index('r').to_pairs(0),
                (('p', (('a', 2), ('b', 30))), ('q', (('a', 2), ('b', 34))), ('r', (('a', 'a'), ('b', 'b'))), ('s', (('a', False), ('b', True))), ('t', (('a', False), ('b', False)))))

        self.assertEqual(f1.set_index('r', drop=True).to_pairs(0),
                (('p', (('a', 2), ('b', 30))), ('q', (('a', 2), ('b', 34))), ('s', (('a', False), ('b', True))), ('t', (('a', False), ('b', False)
                ))))

        f2 = f1.set_index('r', drop=True)

        # in extracting the index, we leave unconnected blocks unchanged.
        self.assertTrue(f1.mloc[[0, 2]].tolist() == f2.mloc.tolist())


    def test_frame_head_tail_a(self):

        # thest of multi threaded apply

        f1 = Frame.from_items(
                zip(range(10), (np.random.rand(1000) for _ in range(10)))
                )
        self.assertEqual(f1.head(3).index.values.tolist(),
                [0, 1, 2])
        self.assertEqual(f1.tail(3).index.values.tolist(),
                [997, 998, 999])


    def test_frame_from_records_date_a(self):

        d = np.datetime64

        records = (
                (d('2018-01-02'), d('2018-01-02'), 'a', False, False),
                (d('2017-01-02'), d('2017-01-02'), 'b', True, False),
                (d('2016-01-02'), d('2016-01-02'), 'c', False, False),
                (d('2015-01-02'), d('2015-01-02'), 'd', True, True),
                )

        f1 = Frame.from_records(records,
                columns=('p', 'q', 'r', 's', 't'),
                index=None)

        dtype = np.dtype

        self.assertEqual(list(f1._blocks._reblock_signature()),
                [(dtype('<M8[D]'), 2), (dtype('<U1'), 1), (dtype('bool'), 2)])


    def test_frame_from_records_a(self):

        NT = namedtuple('Sample', ('a', 'b', 'c'))
        records = [NT(x, x, x) for x in range(4)]
        f1 = Frame.from_records(records)
        self.assertEqual(f1.columns.values.tolist(), ['a', 'b', 'c'])
        self.assertEqual(f1.sum().to_pairs(),
                (('a', 6), ('b', 6), ('c', 6)))

    def test_frame_from_records_b(self):

        records = [{'a':x, 'b':x, 'c':x} for x in range(4)]
        f1 = Frame.from_records(records)
        self.assertEqual(f1.columns.values.tolist(), ['a', 'b', 'c'])
        self.assertEqual(f1.sum().to_pairs(),
                (('a', 6), ('b', 6), ('c', 6)))



    def test_frame_from_json_a(self):

        msg = """[
        {
        "userId": 1,
        "id": 1,
        "title": "delectus aut autem",
        "completed": false
        },
        {
        "userId": 1,
        "id": 2,
        "title": "quis ut nam facilis et officia qui",
        "completed": false
        },
        {
        "userId": 1,
        "id": 3,
        "title": "fugiat veniam minus",
        "completed": false
        },
        {
        "userId": 1,
        "id": 4,
        "title": "et porro tempora",
        "completed": true
        }]"""

        f1 = Frame.from_json(msg)
        self.assertEqual(sorted(f1.columns.values.tolist()),
                sorted(['completed', 'id', 'title', 'userId']))
        self.assertEqual(f1['id'].sum(), 10)

    @unittest.skip('requires network')
    def test_frame_from_json_b(self):
        url = 'https://jsonplaceholder.typicode.com/todos'
        f1 = Frame.from_json_url(url)
        self.assertEqual(f1.columns.values.tolist(),
                ['completed', 'id', 'title', 'userId'])


    def test_frame_reindex_flat_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )

        columns = IndexHierarchy.from_labels(
                (('a', 1), ('a', 2), ('b', 1), ('b', 2), ('b', 3)))
        f1 = Frame.from_records(records,
                columns=columns,
                index=('x', 'y', 'z'))

        f2 = f1.reindex_flat(columns=True)

        self.assertEqual(f2.to_pairs(0),
                ((('a', 1), (('x', 1), ('y', 30), ('z', 54))), (('a', 2), (('x', 2), ('y', 34), ('z', 95))), (('b', 1), (('x', 'a'), ('y', 'b'), ('z', 'c'))), (('b', 2), (('x', False), ('y', True), ('z', False))), (('b', 3), (('x', True), ('y', False), ('z', False)))))


    def test_frame_add_level_a(self):

        records = (
                (1, 2, 'a', False, True),
                (30, 34, 'b', True, False),
                (54, 95, 'c', False, False),
                )


        f1 = Frame.from_records(records,
                columns=('a', 'b', 'c', 'd', 'e'),
                index=('x', 'y', 'z'))

        f2 = f1.reindex_add_level(index='I', columns='II')

        self.assertEqual(f2.to_pairs(0),
                ((('II', 'a'), ((('I', 'x'), 1), (('I', 'y'), 30), (('I', 'z'), 54))), (('II', 'b'), ((('I', 'x'), 2), (('I', 'y'), 34), (('I', 'z'), 95))), (('II', 'c'), ((('I', 'x'), 'a'), (('I', 'y'), 'b'), (('I', 'z'), 'c'))), (('II', 'd'), ((('I', 'x'), False), (('I', 'y'), True), (('I', 'z'), False))), (('II', 'e'), ((('I', 'x'), True), (('I', 'y'), False), (('I', 'z'), False))))
                )


    @unittest.skip('non required dependency')
    def test_from_from_pandas_a(self):
        import pandas as pd

        pdf = pd.DataFrame(
                dict(a=(False, True, False),
                b=(False, False,False),
                c=(1,2,3),
                d=(4,5,6),
                e=(None, None, None)))

        sff = Frame.from_pandas(pdf)
        self.assertTrue((pdf.dtypes.values == sff.dtypes.values).all())




if __name__ == '__main__':
    unittest.main()
