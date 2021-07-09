
import unittest

import numpy as np

from static_frame.test.test_case import TestCase
from static_frame.core.rank import rank_1d
from static_frame.core.rank import RankMethod

class TestUnit(TestCase):

    def test_rank_ordinal_a(self) -> None:
        self.assertEqual(
                rank_1d(np.array([3, 2, 6, 20]), RankMethod.ORDINAL).tolist(),
                [1, 0, 2, 3]
                )

        self.assertEqual(
                rank_1d(np.array([3, 2, 6, 20]), RankMethod.ORDINAL, start=1).tolist(),
                [2, 1, 3, 4]
                )


        a2 = rank_1d(np.array([3, 2, 6, 20]), RankMethod.ORDINAL, ascending=False)
        self.assertEqual(a2.tolist(),
                [2, 3, 1, 0]
                )

    def test_rank_ordinal_b(self) -> None:

        a1 = rank_1d(np.array([0, 2, 3, 2]), 'ordinal', start=1)
        self.assertEqual(a1.tolist(),
                [1, 2, 4, 3]
                )

        a2 = rank_1d(np.array([0, 2, 3, 2]), 'ordinal', start=0)
        self.assertEqual(a2.tolist(),
                [0, 1, 3, 2]
                )

        a3 = rank_1d(np.array([0, 2, 3, 2]), 'ordinal', ascending=False)
        self.assertEqual(a3.tolist(),
                [3, 2, 0, 1]
                )


    def test_rank_average_a(self) -> None:

        a1 = rank_1d(np.array([0, 2, 3, 2]), 'average', ascending=True)
        self.assertEqual(a1.tolist(),
                [0.0, 1.5, 3.0, 1.5]
                )

        a2 = rank_1d(np.array([0, 2, 3, 2]), 'average', start=1)
        self.assertEqual(a2.tolist(),
                [1.0, 2.5, 4.0, 2.5]
                )

        a3 = rank_1d(np.array([0, 2, 3, 2]), 'average', start=1, ascending=False)
        self.assertEqual(a3.tolist(),
                [4.0, 2.5, 1.0, 2.5]
                )


    def test_rank_average_b(self) -> None:

        a1 = rank_1d(np.array([0, 2, 5, 2, 2, 2]), 'average', ascending=True)
        self.assertEqual(a1.tolist(),
                [0.0, 2.5, 2.5, 2.5, 5.0, 2.5]
                )

        # import ipdb; ipdb.set_trace()
        a2 = rank_1d(np.array([0, 2, 3, 2]), 'average', start=1)
        self.assertEqual(a2.tolist(),
                [1.0, 2.5, 4.0, 2.5]
                )

        a3 = rank_1d(np.array([0, 2, 3, 2]), 'average', start=1, ascending=False)
        self.assertEqual(a3.tolist(),
                [4.0, 2.5, 1.0, 2.5]
                )

    def test_rank_min_a(self) -> None:

        a1 = rank_1d(np.array([0, 2, 3, 2]), 'min', start=1)
        self.assertEqual(a1.tolist(),
                [1, 2, 4, 2]
                )
        a2 = rank_1d(np.array([0, 2, 3, 2]), 'min', start=0)
        self.assertEqual(a2.tolist(),
                [0, 1, 3, 1]
                )

        a3 = rank_1d(np.array([0, 2, 3, 2]), 'min', ascending=False)
        self.assertEqual(a3.tolist(),
                [3, 1, 0, 1]
                )


    def test_rank_max_a(self) -> None:

        a1 = rank_1d(np.array([0, 2, 3, 2]), 'max', start=1)
        # import ipdb; ipdb.set_trace()

        self.assertEqual(a1.tolist(),
                [1, 3, 4, 3]
                )
        a2 = rank_1d(np.array([0, 2, 3, 2]), 'max', start=0)
        self.assertEqual(a2.tolist(),
                [0, 2, 3, 2]
                )

        a2 = rank_1d(np.array([0, 2, 3, 2]), 'max', ascending=False)
        self.assertEqual(a2.tolist(),
                [3, 2, 0, 2]
                )



    def test_rank_dense_a(self) -> None:

        a1 = rank_1d(np.array([0, 2, 3, 2]), 'dense', start=1)
        self.assertEqual(a1.tolist(),
                [1, 2, 3, 2]
                )

        a2 = rank_1d(np.array([0, 2, 3, 2]), 'dense', start=0)
        self.assertEqual(a2.tolist(),
                [0, 1, 2, 1]
                )

        a3 = rank_1d(np.array([0, 2, 3, 2]), 'dense', ascending=False)
        self.assertEqual(a3.tolist(),
                [2, 1, 0, 1]
                )



if __name__ == '__main__':
    unittest.main()

