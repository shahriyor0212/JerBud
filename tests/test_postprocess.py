import unittest

from jerbud.postprocess import remove_fillers


class PostprocessTests(unittest.TestCase):
    def test_remove_simple_uh(self):
        src = "Uh, I want to go to the store."
        self.assertEqual(remove_fillers(src), "I want to go to the store.")

    def test_remove_multiple_fillers(self):
        src = "Um, umm, I was like, you know, thinking about it."
        self.assertEqual(remove_fillers(src), "I was thinking about it.")

    def test_preserve_normal_text(self):
        src = "This sentence is fine."
        self.assertEqual(remove_fillers(src), "This sentence is fine.")

    def test_trims_spaces_before_punctuation(self):
        src = "I think, um , that's it ."
        self.assertEqual(remove_fillers(src), "I think, that's it.")


if __name__ == '__main__':
    unittest.main()
