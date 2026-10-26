import unittest

from src.narino_taxonomy.trie import Trie


class TrieTest(unittest.TestCase):
    def setUp(self):
        self.trie = Trie()
        self.trie.insert("Puma concolor", "puma")
        self.trie.insert("Puya clava-herculis", "puya")
        self.trie.insert("Polylepis incana", "polylepis")
        self.trie.insert("Vultur gryphus", "vultur")

    def test_prefix_returns_alphabetical_suggestions(self):
        found = [name for name, _ in self.trie.suggest("pu")]
        self.assertEqual(found, ["Puma concolor", "Puya clava-herculis"])

    def test_prefix_is_case_and_accent_insensitive(self):
        self.assertEqual(self.trie.suggest("PÚM")[0][1], "puma")

    def test_suggestions_respect_the_limit(self):
        self.assertEqual(len(self.trie.suggest("", 2)), 2)
        self.assertEqual(self.trie.suggest("zzz"), [])

    def test_contains_uses_the_folded_name(self):
        self.assertTrue(self.trie.contains("puma concolor"))
        self.assertFalse(self.trie.contains("puma"))

    def test_remove_prunes_dead_branches(self):
        before = self.trie.node_count()
        self.trie.remove("Puma concolor")
        self.assertFalse(self.trie.contains("Puma concolor"))
        self.assertTrue(self.trie.contains("Puya clava-herculis"))
        self.assertLess(self.trie.node_count(), before)
        self.assertEqual(len(self.trie), 3)

    def test_remove_missing_or_partial_name_raises(self):
        with self.assertRaises(KeyError):
            self.trie.remove("Puma")
        with self.assertRaises(KeyError):
            self.trie.remove("Missing name")

    def test_duplicate_and_empty_names_are_rejected(self):
        with self.assertRaises(ValueError):
            self.trie.insert("Puma concolor", "other")
        with self.assertRaises(ValueError):
            self.trie.insert("   ", "blank")

    def test_words_returns_every_terminal(self):
        self.assertEqual(
            sorted(name for name, _ in self.trie.words()),
            ["Polylepis incana", "Puma concolor", "Puya clava-herculis", "Vultur gryphus"],
        )

    def test_removing_one_shared_prefix_keeps_the_other(self):
        self.trie.remove("Puma concolor")
        self.assertEqual([name for name, _ in self.trie.suggest("pu")], ["Puya clava-herculis"])


if __name__ == "__main__":
    unittest.main()
