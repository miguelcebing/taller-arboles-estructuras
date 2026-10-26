import unittest

from src.narino_taxonomy import Explorer


def key_of(explorer, name):
    for node in explorer.tree.preorder():
        if node.name == name:
            return node.key
    raise AssertionError(f"missing node {name}")


def key_of_species(explorer, scientific_name):
    for species in explorer.registry.values():
        if species.scientific_name == scientific_name:
            return species.key
    raise AssertionError(f"missing species {scientific_name}")


class ExplorerTest(unittest.TestCase):
    def setUp(self):
        self.explorer = Explorer.with_seed_data()

    def test_seed_has_twenty_species_and_is_consistent(self):
        stats = self.explorer.stats()
        self.assertEqual(stats["taxonomy"]["species"], 20)
        self.assertEqual(stats["taxonomy"]["nodes"], 65)
        self.assertEqual(stats["taxonomy"]["height"], 6)
        self.assertEqual(stats["taxonomy"]["leaves"], 20)
        self.assertEqual(stats["avl"]["size"], 20)
        self.assertEqual(stats["avl"]["height"], 5)
        self.assertTrue(stats["avl"]["balanced"])
        self.assertEqual(stats["trie"]["size"], 20)
        self.assertTrue(stats["consistency"]["ok"])
        self.assertEqual(len(self.explorer.families()), 18)

    def test_tree_view_has_both_kingdoms(self):
        payload = self.explorer.tree_view()
        self.assertEqual([child["name"] for child in payload["children"]], ["Animalia", "Plantae"])
        self.assertEqual(payload["species_count"], 20)
        self.assertEqual(payload["altitude"], [400, 4500])

    def test_navigate_returns_lineage_depth_and_height(self):
        puma = key_of_species(self.explorer, "Puma concolor")
        data = self.explorer.navigate(puma)
        self.assertEqual(data["depth"], 6)
        self.assertEqual(data["height"], 0)
        self.assertEqual(data["subtree_species"], 1)
        self.assertEqual(
            [item["name"] for item in data["path"]],
            ["Biodiversidad de Nariño", "Animalia", "Chordata", "Mammalia", "Carnivora", "Felidae", "Puma concolor"],
        )
        self.assertEqual(data["species"]["common_name"], "Puma")

    def test_navigate_unknown_key_raises(self):
        with self.assertRaises(KeyError):
            self.explorer.navigate("missing")

    def test_lca_between_puma_and_condor_is_chordata(self):
        puma = key_of_species(self.explorer, "Puma concolor")
        condor = key_of_species(self.explorer, "Vultur gryphus")
        data = self.explorer.common_ancestor(puma, condor)
        self.assertEqual(data["ancestor"]["name"], "Chordata")
        self.assertEqual(data["shared_depth"], 2)
        self.assertEqual(data["distance_a"], 4)
        self.assertEqual(data["distance_b"], 4)

    def test_lca_between_plants_and_animals_is_the_root(self):
        frailejon = key_of_species(self.explorer, "Espeletia pycnophylla")
        puma = key_of_species(self.explorer, "Puma concolor")
        data = self.explorer.common_ancestor(frailejon, puma)
        self.assertEqual(data["ancestor"]["name"], "Biodiversidad de Nariño")
        self.assertEqual(data["ancestor"]["rank"], "raíz")

    def test_lca_between_felids_is_the_family(self):
        puma = key_of_species(self.explorer, "Puma concolor")
        tigrillo = key_of_species(self.explorer, "Leopardus tigrinus")
        self.assertEqual(self.explorer.common_ancestor(puma, tigrillo)["ancestor"]["name"], "Felidae")

    def test_traversals_visit_every_node_with_a_purpose(self):
        preorder = self.explorer.traverse("preorder")
        postorder = self.explorer.traverse("postorder")
        bfs = self.explorer.traverse("bfs")
        self.assertEqual(len(preorder["items"]), 65)
        self.assertEqual(preorder["items"][0]["name"], "Biodiversidad de Nariño")
        self.assertEqual(postorder["items"][-1]["name"], "Biodiversidad de Nariño")
        depths = [item["depth"] for item in bfs["items"]]
        self.assertEqual(depths, sorted(depths))
        for result in (preorder, postorder, bfs):
            self.assertTrue(result["purpose"])

    def test_traversal_type_is_validated(self):
        with self.assertRaises(ValueError):
            self.explorer.traverse("inorder")

    def test_range_query_returns_species_that_cross_the_band(self):
        names = {item["scientific_name"] for item in self.explorer.by_altitude(1500, 3000)}
        self.assertEqual(len(names), 19)
        self.assertIn("Puma concolor", names)
        self.assertIn("Polylepis incana", names)
        self.assertNotIn("Bothriechis schlegelii", names)

    def test_range_query_filters_species_below_the_band(self):
        names = {item["scientific_name"] for item in self.explorer.by_altitude(1500, 2500)}
        self.assertEqual(len(names), 17)
        self.assertNotIn("Espeletia pycnophylla", names)
        self.assertNotIn("Polylepis incana", names)
        self.assertNotIn("Bothriechis schlegelii", names)

    def test_range_boundaries_are_inclusive(self):
        self.assertIn(
            "Bothriechis schlegelii",
            [item["scientific_name"] for item in self.explorer.by_altitude(400, 400)],
        )
        self.assertIn(
            "Polylepis incana",
            [item["scientific_name"] for item in self.explorer.by_altitude(3000, 3000)],
        )

    def test_autocomplete_shares_the_pu_prefix(self):
        found = [item["scientific_name"] for item in self.explorer.autocomplete("pu")]
        self.assertEqual(found, ["Puma concolor", "Puya clava-herculis"])
        self.assertEqual(
            [item["scientific_name"] for item in self.explorer.autocomplete("pum")],
            ["Puma concolor"],
        )
        self.assertEqual(self.explorer.autocomplete("zz"), [])
        self.assertEqual(len(self.explorer.autocomplete("", 1)), 1)

    def test_add_species_updates_all_three_structures(self):
        asteraceae = key_of(self.explorer, "Asteraceae")
        created = self.explorer.add_species(
            asteraceae, "Baccharis latifolia", "Chilca", 2200, 3400, "Arbusto de borde de bosque."
        )
        self.assertEqual(len(self.explorer.registry), 21)
        self.assertTrue(self.explorer.check_consistency()["ok"])
        self.assertIn(created["key"], self.explorer.registry)
        self.assertTrue(self.explorer.altitudes.contains(self.explorer.find_species(created["key"])))
        self.assertTrue(self.explorer.names.contains("Baccharis latifolia"))
        self.assertEqual(
            [item["scientific_name"] for item in self.explorer.autocomplete("bac")],
            ["Baccharis latifolia"],
        )

    def test_duplicate_scientific_name_is_rejected(self):
        felidae = key_of(self.explorer, "Felidae")
        with self.assertRaises(ValueError):
            self.explorer.add_species(felidae, "Puma concolor", "Otro puma", 1000, 2000)

    def test_species_can_only_be_added_to_a_family(self):
        carnivora = key_of(self.explorer, "Carnivora")
        with self.assertRaises(ValueError):
            self.explorer.add_species(carnivora, "New species", "Nueva", 1000, 2000)

    def test_invalid_altitude_ranges_are_rejected(self):
        asteraceae = key_of(self.explorer, "Asteraceae")
        with self.assertRaises(ValueError):
            self.explorer.add_species(asteraceae, "Bad range", "Mala", 3000, 2000)
        with self.assertRaises(ValueError):
            self.explorer.add_species(asteraceae, "Negative", "Mala", -1, 2000)
        with self.assertRaises(ValueError):
            self.explorer.add_species(asteraceae, "Too high", "Mala", 1000, 7000)
        with self.assertRaises(ValueError):
            self.explorer.add_species(asteraceae, "Not int", "Mala", 1000.5, 2000)

    def test_remove_family_cleans_avl_and_trie(self):
        felidae = key_of(self.explorer, "Felidae")
        result = self.explorer.remove_branch(felidae)
        self.assertEqual(result["species_count"], 2)
        self.assertEqual(result["nodes"], 3)
        self.assertIsNone(self.explorer.tree.find(felidae))
        self.assertNotIn("puma concolor", self.explorer._name_index)
        self.assertEqual(self.explorer.autocomplete("pum"), [])
        self.assertEqual(len(self.explorer.registry), 18)
        self.assertTrue(self.explorer.check_consistency()["ok"])
        self.assertEqual(self.explorer.stats()["avl"]["size"], 18)

    def test_remove_species_leaf_keeps_the_family(self):
        asteraceae = key_of(self.explorer, "Asteraceae")
        created = self.explorer.add_species(asteraceae, "Baccharis latifolia", "Chilca", 2200, 3400)
        result = self.explorer.remove_branch(created["key"])
        self.assertEqual(result["species_count"], 1)
        self.assertEqual(result["nodes"], 1)
        self.assertIsNotNone(self.explorer.tree.find(asteraceae))
        self.assertEqual(len(self.explorer.registry), 20)
        self.assertTrue(self.explorer.check_consistency()["ok"])

    def test_remove_root_and_missing_branch_are_rejected(self):
        with self.assertRaises(ValueError):
            self.explorer.remove_branch(self.explorer.tree.root.key)
        with self.assertRaises(KeyError):
            self.explorer.remove_branch("missing")

    def test_altitude_bands_are_sorted(self):
        bands = self.explorer.altitude_bands()
        self.assertEqual(len(bands), 20)
        lows = [item["min_altitude"] for item in bands]
        self.assertEqual(lows, sorted(lows))
        self.assertEqual(bands[0]["scientific_name"], "Bothriechis schlegelii")

    def test_species_options_are_sorted_by_scientific_name(self):
        options = self.explorer.species_options()
        names = [item["scientific_name"] for item in options]
        self.assertEqual(names, sorted(names, key=str.casefold))


if __name__ == "__main__":
    unittest.main()
