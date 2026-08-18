import unittest

from jerbud.postprocess import grammar_correct, remove_fillers


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


class GrammarTests(unittest.TestCase):
    def test_restores_contractions(self):
        self.assertEqual(grammar_correct("I cant do it"), "I can't do it.")

    def test_capitalizes_standalone_i(self):
        self.assertEqual(grammar_correct("me and i went"), "Me and I went.")

    def test_capitalizes_sentence_starts(self):
        self.assertEqual(grammar_correct("hi there. i am ready"), "Hi there. I am ready.")

    def test_adds_trailing_period(self):
        self.assertEqual(grammar_correct("This is fine"), "This is fine.")

    def test_preserves_acronyms(self):
        self.assertEqual(grammar_correct("show your ID"), "Show your ID.")

    def test_empty_text(self):
        self.assertEqual(grammar_correct(""), "")


if __name__ == '__main__':
    unittest.main()
