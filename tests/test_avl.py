import math
import random
import unittest

from src.narino_taxonomy.avl import AVLTree, species_key
from tests.support import make_species


class AVLTreeTest(unittest.TestCase):
    def test_empty_tree(self):
        tree = AVLTree()
        self.assertEqual(len(tree), 0)
        self.assertEqual(tree.height(), 0)
        self.assertTrue(tree.is_balanced())
        self.assertEqual(list(tree.in_order()), [])
        self.assertEqual(tree.range_query(0, 5000), [])

    def test_insert_and_find(self):
        tree = AVLTree()
        species = make_species("Puma concolor", 1200, 3200)
        tree.insert(species)
        self.assertEqual(len(tree), 1)
        self.assertIs(tree.find(species_key(species)), species)
        self.assertTrue(tree.contains(species))
        self.assertIsNone(tree.find((9999, "nope")))

    def test_duplicate_key_is_rejected(self):
        tree = AVLTree()
        species = make_species("Puma concolor", 1200, 3200)
        tree.insert(species)
        with self.assertRaises(ValueError):
            tree.insert(species)

    def test_same_altitude_uses_name_as_tie_breaker(self):
        tree = AVLTree()
        alpha = make_species("Alpha beta", 1800, 3000)
        zeta = make_species("Zeta omega", 1800, 2500)
        tree.insert(zeta)
        tree.insert(alpha)
        self.assertEqual([item.scientific_name for item in tree.in_order()], ["Alpha beta", "Zeta omega"])
        tree.remove_species(alpha)
        self.assertEqual([item.scientific_name for item in tree.in_order()], ["Zeta omega"])

    def test_in_order_is_sorted_by_altitude(self):
        tree = AVLTree()
        for altitude in (3000, 1000, 2500, 1800):
            tree.insert(make_species(f"Species {altitude}", altitude, altitude + 100))
        self.assertEqual([item.min_altitude for item in tree.in_order()], [1000, 1800, 2500, 3000])

    def test_ascending_input_stays_balanced(self):
        tree = AVLTree()
        for altitude in range(1, 201):
            tree.insert(make_species(f"Species {altitude:03d}", altitude, altitude + 50))
        self.assertTrue(tree.is_balanced())
        self.assertEqual(len(tree), 200)
        self.assertLessEqual(tree.height(), math.ceil(1.44 * math.log2(202)))
        self.assertGreater(tree.rotations, 0)

    def test_range_query_returns_overlapping_intervals(self):
        tree = AVLTree()
        low = make_species("Low", 1000, 1500)
        middle = make_species("Middle", 2000, 2500)
        high = make_species("High", 3000, 3500)
        for species in (low, middle, high):
            tree.insert(species)
        found = tree.range_query(1400, 2600)
        self.assertEqual([item.scientific_name for item in found], ["Low", "Middle"])
        self.assertEqual(tree.range_query(1500, 1500), [low])
        self.assertEqual(tree.range_query(1600, 1900), [])
        self.assertEqual(tree.range_query(2500, 3000), [middle, high])

    def test_range_query_rejects_inverted_limits(self):
        tree = AVLTree()
        with self.assertRaises(ValueError):
            tree.range_query(3000, 1000)

    def test_remove_leaf_one_child_and_two_children(self):
        tree = AVLTree()
        values = [2000, 1000, 3000, 500, 1500, 2500, 3500]
        for altitude in values:
            tree.insert(make_species(f"Species {altitude}", altitude, altitude + 10))
        tree.remove((500, "species 500"))
        self.assertEqual(len(tree), 6)
        tree.remove((1000, "species 1000"))
        self.assertEqual(len(tree), 5)
        tree.remove((2000, "species 2000"))
        self.assertEqual(len(tree), 4)
        self.assertTrue(tree.is_balanced())
        self.assertEqual([item.min_altitude for item in tree.in_order()], [1500, 2500, 3000, 3500])

    def test_remove_root_with_two_children(self):
        tree = AVLTree()
        for altitude in (2000, 1000, 3000):
            tree.insert(make_species(f"Species {altitude}", altitude, altitude + 10))
        root_key = tree.root.key
        tree.remove(root_key)
        self.assertEqual(len(tree), 2)
        self.assertTrue(tree.is_balanced())
        self.assertNotIn(root_key, [node.key for node in tree._postorder()])

    def test_remove_missing_key_raises(self):
        tree = AVLTree()
        with self.assertRaises(KeyError):
            tree.remove((1000, "missing"))

    def test_random_operations_keep_the_invariant(self):
        rng = random.Random(7)
        tree = AVLTree()
        inserted = {}
        for step in range(300):
            altitude = rng.randrange(0, 5000, 10)
            name = f"Species {altitude} {step % 3}"
            species = make_species(name, altitude, altitude + rng.randrange(50, 500))
            key = species_key(species)
            if key in inserted:
                continue
            tree.insert(species)
            inserted[key] = species
            if step % 5 == 0 and inserted:
                victim = rng.choice(list(inserted))
                tree.remove(victim)
                del inserted[victim]
            self.assertTrue(tree.is_balanced())
        self.assertEqual(len(tree), len(inserted))
        self.assertEqual(tree.stats()["size"], len(inserted))


if __name__ == "__main__":
    unittest.main()
