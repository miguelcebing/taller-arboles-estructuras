"""Facade that keeps the taxonomy, the AVL index and the trie in sync.

Only this class mutates the three structures. If a species disappears from the
tree it also disappears from the altitude index, the prefix index and the
registry, which is what prevents orphan records.
"""

from .avl import AVLTree
from .nary import TaxonomyTree, slug
from .species import Species
from .trie import Trie, fold

RANKS = ("raíz", "reino", "filo", "clase", "orden", "familia", "especie")

TRAVERSALS = {
    "preorder": "Muestra la jerarquía desde el reino hacia las especies; sirve para pintar el árbol y numerar ramas.",
    "postorder": "Resuelve los hijos antes que el padre; sirve para contar especies y alturas de cada rama.",
    "bfs": "Recorre por niveles; sirve para medir el ancho de la taxonomía y comparar ramas de la misma profundidad.",
}


class Explorer:
    """Single entry point for queries and mutations over the three trees."""

    def __init__(self):
        self.tree = TaxonomyTree()
        self.altitudes = AVLTree()
        self.names = Trie()
        self.registry = {}
        self._name_index = {}

    @classmethod
    def with_seed_data(cls):
        from .seed import build_seed

        explorer = cls()
        build_seed(explorer)
        return explorer

    def add_species(self, parent_key, scientific_name, common_name, min_altitude, max_altitude, note=""):
        parent = self.tree.require(parent_key)
        if parent.rank != "familia":
            raise ValueError(
                f"Species must be attached to a family; '{parent.name}' is a {parent.rank}"
            )
        name = scientific_name.strip()
        common = common_name.strip()
        if not name:
            raise ValueError("The scientific name cannot be empty")
        if not common:
            raise ValueError("The common name cannot be empty")
        if not isinstance(min_altitude, int) or not isinstance(max_altitude, int):
            raise ValueError("Altitudes must be whole meters")
        if min_altitude < 0 or max_altitude < min_altitude:
            raise ValueError(
                f"Invalid altitude range {min_altitude}-{max_altitude} m for '{name}'"
            )
        if max_altitude > 6000:
            raise ValueError(f"Altitude {max_altitude} m is outside the supported range")
        folded = fold(name)
        if folded in self._name_index:
            raise ValueError(f"The species '{name}' is already in the taxonomy")

        key = f"{parent.key}/{slug(name)}"
        if self.tree.find(key) is not None:
            raise ValueError(f"A taxon with key '{key}' already exists")
        species = Species(key, name, common, min_altitude, max_altitude, parent.key, note)

        self.tree.add_child(parent.key, name, "especie", species)
        try:
            self.altitudes.insert(species)
            self.names.insert(name, key)
        except Exception:
            if self.altitudes.contains(species):
                self.altitudes.remove_species(species)
            self.tree.remove_branch(key)
            raise

        self.registry[key] = species
        self._name_index[folded] = key
        return species.as_dict()

    def remove_branch(self, key):
        node = self.tree.require(key)
        if node.parent is None:
            raise ValueError("The root of the taxonomy cannot be removed")
        species = self.tree.subtree_species(key)
        for item in species:
            if item.key not in self.registry:
                raise RuntimeError(f"Species '{item.scientific_name}' is missing from the registry")
            if not self.altitudes.contains(item):
                raise RuntimeError(f"Species '{item.scientific_name}' is missing from the AVL index")
            if not self.names.contains(item.scientific_name):
                raise RuntimeError(f"Species '{item.scientific_name}' is missing from the trie")

        removed = self.tree.remove_branch(key)
        for item in species:
            self.altitudes.remove_species(item)
            self.names.remove(item.scientific_name)
            self.registry.pop(item.key, None)
            self._name_index.pop(fold(item.scientific_name), None)

        return {
            "removed_key": key,
            "removed_name": node.name,
            "nodes": len(removed["nodes"]),
            "species_count": len(species),
            "species": [item.as_dict() for item in species],
        }

    def navigate(self, key):
        node = self.tree.require(key)
        path = [
            {"key": item.key, "name": item.name, "rank": item.rank}
            for item in self.tree.lineage(key)
        ]
        return {
            "key": node.key,
            "name": node.name,
            "rank": node.rank,
            "depth": self.tree.depth(key),
            "height": self.tree.height(key),
            "path": path,
            "children": [
                {"key": child.key, "name": child.name, "rank": child.rank}
                for child in node.children
            ],
            "subtree_species": len(self.tree.subtree_species(key)),
            "species": node.species.as_dict() if node.species else None,
        }

    def common_ancestor(self, key_a, key_b):
        ancestor = self.tree.lca(key_a, key_b)
        node_a = self.tree.require(key_a)
        node_b = self.tree.require(key_b)
        return {
            "ancestor": {
                "key": ancestor.key,
                "name": ancestor.name,
                "rank": ancestor.rank,
            },
            "path_a": [
                {"key": item.key, "name": item.name, "rank": item.rank}
                for item in self.tree.lineage(key_a)
            ],
            "path_b": [
                {"key": item.key, "name": item.name, "rank": item.rank}
                for item in self.tree.lineage(key_b)
            ],
            "shared_depth": self.tree.depth(ancestor.key),
            "distance_a": self.tree.depth(key_a) - self.tree.depth(ancestor.key),
            "distance_b": self.tree.depth(key_b) - self.tree.depth(ancestor.key),
            "species_a": node_a.species.as_dict() if node_a.species else None,
            "species_b": node_b.species.as_dict() if node_b.species else None,
        }

    def traverse(self, kind):
        if kind not in TRAVERSALS:
            raise ValueError(f"Unknown traversal '{kind}'")
        walkers = {
            "preorder": self.tree.preorder,
            "postorder": self.tree.postorder,
            "bfs": self.tree.bfs,
        }
        items = []
        for node in walkers[kind]():
            items.append(
                {
                    "key": node.key,
                    "name": node.name,
                    "rank": node.rank,
                    "depth": self.tree.depth(node.key),
                    "species": node.species.common_name if node.species else None,
                }
            )
        return {"type": kind, "purpose": TRAVERSALS[kind], "items": items}

    def by_altitude(self, lo, hi):
        if not isinstance(lo, int) or not isinstance(hi, int):
            raise ValueError("Altitude limits must be whole meters")
        return [item.as_dict() for item in self.altitudes.range_query(lo, hi)]

    def autocomplete(self, prefix, limit=8):
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError("The suggestion limit must be a positive integer")
        results = []
        for display, key in self.names.suggest(prefix, limit):
            species = self.registry.get(key)
            if species is None:
                raise RuntimeError(f"The trie points to missing species '{key}'")
            results.append(species.as_dict())
        return results

    def altitude_bands(self):
        ordered = sorted(
            self.registry.values(),
            key=lambda item: (item.min_altitude, item.scientific_name.casefold()),
        )
        return [item.as_dict() for item in ordered]

    def species_options(self):
        ordered = sorted(self.registry.values(), key=lambda item: item.scientific_name.casefold())
        return [
            {
                "key": item.key,
                "scientific_name": item.scientific_name,
                "common_name": item.common_name,
            }
            for item in ordered
        ]

    def families(self):
        return [
            {"key": node.key, "name": node.name}
            for node in self.tree.preorder()
            if node.rank == "familia"
        ]

    def find_species(self, key):
        species = self.registry.get(key)
        if species is None:
            raise KeyError(f"No species with key '{key}'")
        return species

    def tree_view(self):
        return self.tree.to_dict()

    def check_consistency(self):
        tree_keys = {node.species.key for node in self.tree.preorder() if node.species}
        registry_keys = set(self.registry)
        avl_keys = {item.key for item in self.altitudes.in_order()}
        trie_keys = {key for _, key in self.names.words()}
        missing_in_tree = sorted(registry_keys - tree_keys)
        missing_in_avl = sorted(registry_keys - avl_keys)
        missing_in_trie = sorted(registry_keys - trie_keys)
        extra_in_tree = sorted(tree_keys - registry_keys)
        extra_in_avl = sorted(avl_keys - registry_keys)
        extra_in_trie = sorted(trie_keys - registry_keys)
        return {
            "ok": not any(
                (
                    missing_in_tree,
                    missing_in_avl,
                    missing_in_trie,
                    extra_in_tree,
                    extra_in_avl,
                    extra_in_trie,
                )
            ),
            "missing_in_tree": missing_in_tree,
            "missing_in_avl": missing_in_avl,
            "missing_in_trie": missing_in_trie,
            "extra_in_tree": extra_in_tree,
            "extra_in_avl": extra_in_avl,
            "extra_in_trie": extra_in_trie,
        }

    def stats(self):
        widths = self.tree.width_by_level()
        ranks = {}
        for node in self.tree.preorder():
            ranks[node.rank] = ranks.get(node.rank, 0) + 1
        return {
            "taxonomy": {
                "nodes": len(self.tree),
                "species": len(self.registry),
                "height": self.tree.height(),
                "leaves": self.tree.leaf_count(),
                "width_by_level": widths,
                "max_width": max(widths) if widths else 0,
                "ranks": ranks,
            },
            "avl": self.altitudes.stats(),
            "trie": self.names.stats(),
            "consistency": self.check_consistency(),
        }
