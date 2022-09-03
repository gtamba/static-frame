
from collections import Counter


from static_frame.test.test_case import TestCase
from doc.build_example import to_string_io
from doc.build_example import get_examples_fp
from doc.build_example import TAG_START
from doc.build_example import TAG_END

# clipboard does not work on some platforms / GitHub CI
SKIP = frozenset((
    'from_clipboard()',
    'to_clipboard()',
    'from_arrow()',
    'to_arrow()',
    'mloc'
    ))

class TestUnit(TestCase):


    def test_example_gen(self) -> None:
        # NOTE: comparing the direct output is problematic as different platforms might have subtle differences in float representations; thus, we just copmare exaples size and exercise example generation

        current = to_string_io()
        fp = get_examples_fp()
        skip = False

        def count(lines, counter):
            current = ''
            for line in lines:
                if line.startswith(TAG_START):
                    current = line.rstrip()
                    if current.split('-', maxsplit=1)[1] in SKIP:
                        current = ''
                    continue
                if current:
                    counter[current] += 1
                    continue
                if line.startswith(TAG_END):
                    current = ''

        counts_current = Counter()
        counts_past = Counter()

        with open(fp) as past:
            count(past, counts_past)
        count(current.readlines(), counts_current)

        for key in (counts_current.keys() | counts_past.keys()):
            with self.subTest(key):
                self.assertEqual(counts_current[key], counts_past[key], key)

        # import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    import unittest
    unittest.main()
