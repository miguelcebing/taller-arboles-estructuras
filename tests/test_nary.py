import unittest

from src.narino_taxonomy.nary import TaxonomyTree
from tests.support import make_species


def build_tree():
    tree = TaxonomyTree()
    root = tree.add_root("Life", "raíz")
    a = tree.add_child(root.key, "A", "reino")
    a1 = tree.add_child(a.key, "A1", "filo")
    a1a = tree.add_child(a1.key, "A1a", "clase", make_species("Alpha beta", 1000, 2000))
    tree.add_child(a.key, "A2", "filo")
    b = tree.add_child(root.key, "B", "reino")
    tree.add_child(b.key, "B1", "filo")
    return tree


class TaxonomyTreeTest(unittest.TestCase):
    def test_empty_tree_has_no_height_or_width(self):
        tree = TaxonomyTree()
        self.assertEqual(tree.height(), 0)
        self.assertEqual(tree.width_by_level(), [])
        self.assertEqual(list(tree.preorder()), [])
        self.assertEqual(tree.count(), 0)

    def test_root_and_child_keys_are_unique(self):
        tree = TaxonomyTree()
        root = tree.add_root("Life", "raíz")
        tree.add_child(root.key, "Alpha", "reino")
        with self.assertRaises(ValueError):
            tree.add_child(root.key, "Alpha", "reino")
        with self.assertRaises(ValueError):
            tree.add_root("Other", "raíz")

    def test_child_of_missing_parent_raises(self):
        tree = TaxonomyTree()
        with self.assertRaises(KeyError):
            tree.add_child("nope", "A", "reino")

    def test_lineage_goes_from_root_to_node(self):
        tree = build_tree()
        key = "life/a/a1/a1a"
        self.assertEqual([node.name for node in tree.lineage(key)], ["Life", "A", "A1", "A1a"])
        self.assertEqual(tree.depth(key), 3)

    def test_lca_handles_siblings_cousins_and_self(self):
        tree = build_tree()
        self.assertEqual(tree.lca("life/a/a1/a1a", "life/a/a2").name, "A")
        self.assertEqual(tree.lca("life/a/a1/a1a", "life/b/b1").name, "Life")
        self.assertEqual(tree.lca("life/a/a2", "life/a/a2").name, "A2")

    def test_lca_with_unknown_key_raises(self):
        tree = build_tree()
        with self.assertRaises(KeyError):
            tree.lca("life/a", "missing")

    def test_traversals_use_their_own_order(self):
        tree = build_tree()
        self.assertEqual(
            [node.name for node in tree.preorder()],
            ["Life", "A", "A1", "A1a", "A2", "B", "B1"],
        )
        self.assertEqual(
            [node.name for node in tree.postorder()],
            ["A1a", "A1", "A2", "A", "B1", "B", "Life"],
        )
        self.assertEqual(
            [node.name for node in tree.bfs()],
            ["Life", "A", "B", "A1", "A2", "B1", "A1a"],
        )

    def test_height_width_and_leaves(self):
        tree = build_tree()
        self.assertEqual(tree.height(), 3)
        self.assertEqual(tree.height("life/a"), 2)
        self.assertEqual(tree.width_by_level(), [1, 2, 3, 1])
        self.assertEqual(tree.leaf_count(), 3)
        self.assertEqual(tree.count(), 7)

    def test_remove_branch_detaches_nodes_and_reports_species(self):
        tree = build_tree()
        removed = tree.remove_branch("life/a")
        self.assertEqual(sorted(item.scientific_name for item in removed["species"]), ["Alpha beta"])
        self.assertEqual(len(removed["nodes"]), 4)
        self.assertIsNone(tree.find("life/a"))
        self.assertIsNone(tree.find("life/a/a1/a1a"))
        self.assertEqual(tree.count(), 3)
        self.assertEqual([node.name for node in tree.root.children], ["B"])

    def test_remove_root_is_rejected(self):
        tree = build_tree()
        with self.assertRaises(ValueError):
            tree.remove_branch("life")

    def test_to_dict_annotates_counts_and_altitudes(self):
        tree = build_tree()
        payload = tree.to_dict()
        self.assertEqual(payload["species_count"], 1)
        self.assertEqual(payload["altitude"], [1000, 2000])
        self.assertEqual(payload["height"], 3)
        self.assertEqual(payload["children"][0]["species_count"], 1)
        self.assertEqual(payload["children"][1]["species_count"], 0)

    def test_empty_branch_keeps_annotations_consistent(self):
        tree = build_tree()
        tree.remove_branch("life/a/a1/a1a")
        payload = tree.to_dict()
        self.assertEqual(payload["species_count"], 0)
        self.assertIsNone(payload["altitude"][0])


if __name__ == "__main__":
    unittest.main()
