"""Real measurements for docs/ANALYSIS.md.

Run from the project root: python bench/benchmark.py
Every number printed here comes from this run; nothing is hard-coded.
"""

import math
import random
import sys
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.narino_taxonomy.avl import AVLTree
from src.narino_taxonomy.nary import TaxonomyTree
from src.narino_taxonomy.species import Species
from src.narino_taxonomy.trie import Trie


class BSTNode:
    __slots__ = ("key", "left", "right")

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


def bst_insert(root, key):
    if root is None:
        return BSTNode(key)
    node = root
    while True:
        if key < node.key:
            if node.left is None:
                node.left = BSTNode(key)
                return root
            node = node.left
        else:
            if node.right is None:
                node.right = BSTNode(key)
                return root
            node = node.right


def bst_height(root):
    if root is None:
        return 0
    stack = [(root, 1)]
    tallest = 0
    while stack:
        node, depth = stack.pop()
        tallest = max(tallest, depth)
        if node.left is not None:
            stack.append((node.left, depth + 1))
        if node.right is not None:
            stack.append((node.right, depth + 1))
    return tallest


def build_bushy(n, branching=4):
    tree = TaxonomyTree()
    root = tree.add_root("Root", "raíz")
    queue = deque([root])
    count = 1
    while count < n:
        parent = queue.popleft()
        for _ in range(branching):
            if count >= n:
                break
            child = tree.add_child(parent.key, f"Node {count}", "nivel")
            queue.append(child)
            count += 1
    return tree


def build_chain(n):
    tree = TaxonomyTree()
    parent = tree.add_root("Root", "raíz")
    for index in range(1, n):
        parent = tree.add_child(parent.key, f"Node {index}", "nivel")
    return tree


def species(name, minimum, maximum=None):
    maximum = maximum if maximum is not None else minimum + 500
    return Species(f"key/{name}", name, "common", minimum, maximum, "family")


def timed_ms(action):
    start = time.perf_counter()
    result = action()
    return (time.perf_counter() - start) * 1000, result


def nary_table():
    print("## Crecimiento del árbol n-ario\n")
    print("| n | altura bushy (b=4) | altura cadena | altura mínima teórica | ancho máximo bushy | construcción bushy (ms) |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: |")
    for n in (100, 1000, 10000):
        bushy_ms, bushy = timed_ms(lambda: build_bushy(n))
        chain_ms, chain = timed_ms(lambda: build_chain(n))
        theoretical = math.ceil(math.log(n * 3 + 1, 4)) - 1
        width = max(bushy.width_by_level())
        print(
            f"| {n} | {bushy.height()} | {chain.height()} | {theoretical} | {width} | {bushy_ms:.2f} |"
        )
    print(f"\nLa cadena de 10 000 nodos se construyó en {chain_ms:.2f} ms; su altura es lineal, no logarítmica.\n")


def avl_table():
    print("## AVL contra BST simple con altitudes ordenadas\n")
    print("| n | altura BST | altura AVL | rotaciones AVL | BST (ms) | AVL (ms) |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: |")
    for n in (100, 1000, 10000):
        bst_ms, bst_root = timed_ms(lambda: insert_into_bst(n))
        bst_height_value = bst_height(bst_root)

        avl = AVLTree()
        avl_ms, _ = timed_ms(lambda: insert_into_avl(avl, n))
        print(
            f"| {n} | {bst_height_value} | {avl.height()} | {avl.rotations} | {bst_ms:.2f} | {avl_ms:.2f} |"
        )
    print()


def insert_into_bst(n):
    root = None
    for index in range(n):
        root = bst_insert(root, (index, f"species {index:05d}"))
    return root


def insert_into_avl(tree, n):
    for index in range(n):
        tree.insert(species(f"Species {index:05d}", index, index + 500))


def range_table():
    rng = random.Random(2026)
    n = 10000
    queries = 300
    print("## Consulta por rango contra recorrido lineal\n")
    print("Dos regímenes: rangos largos como los de las especies reales y rangos cortos que producen una respuesta selectiva.\n")
    print("| régimen | ancho (m) | n | consultas | AVL promedio (µs) | lineal promedio (µs) | aceleración | resultados promedio |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for label, low_length, high_length, widths in (
        ("rangos largos (100-1500 m)", 100, 1500, (200, 500, 1000)),
        ("rangos cortos (20-80 m)", 20, 80, (100, 200, 500)),
    ):
        avl = AVLTree()
        population = []
        for index in range(n):
            minimum = rng.randrange(0, 5000)
            item = species(
                f"Species {index:05d}",
                minimum,
                minimum + rng.randrange(low_length, high_length),
            )
            avl.insert(item)
            population.append(item)

        for width in widths:
            ranges = []
            for _ in range(queries):
                low = rng.randrange(0, 4500)
                ranges.append((low, low + width))

            def avl_run():
                return [len(avl.range_query(low, high)) for low, high in ranges]

            def linear_run():
                return [
                    sum(1 for item in population if item.min_altitude <= high and item.max_altitude >= low)
                    for low, high in ranges
                ]

            avl_ms, avl_counts = timed_ms(avl_run)
            linear_ms, linear_counts = timed_ms(linear_run)
            assert avl_counts == linear_counts, "the two strategies must agree"
            average_results = sum(avl_counts) / len(avl_counts)
            print(
                f"| {label} | {width} | {n} | {queries} | {avl_ms * 1000 / queries:.1f} | "
                f"{linear_ms * 1000 / queries:.1f} | {linear_ms / avl_ms:.1f}× | {average_results:.1f} |"
            )
    print()


def trie_table():
    rng = random.Random(11)
    names = [f"Genus{rng.randrange(40)} species{index:05d}" for index in range(10000)]
    trie = Trie()
    build_ms, _ = timed_ms(lambda: [trie.insert(name, f"key/{index}") for index, name in enumerate(names)])
    prefixes = [f"genus{rng.randrange(40)}" for _ in range(1000)]

    def trie_run():
        return [len(trie.suggest(prefix, 8)) for prefix in prefixes]

    def list_run():
        return [len([name for name in names if name.casefold().startswith(prefix)][:8]) for prefix in prefixes]

    trie_ms, trie_counts = timed_ms(trie_run)
    list_ms, list_counts = timed_ms(list_run)
    assert trie_counts == list_counts, "trie and list suggestions must agree"
    print("## Autocompletado contra filtro lineal\n")
    print("| nombres | consultas | trie promedio (µs) | lista promedio (µs) | aceleración | construcción (ms) |")
    print("| ---: | ---: | ---: | ---: | ---: | ---: |")
    print(
        f"| {len(names)} | {len(prefixes)} | {trie_ms * 1000 / len(prefixes):.1f} | "
        f"{list_ms * 1000 / len(prefixes):.1f} | {list_ms / trie_ms:.1f}× | {build_ms:.2f} |"
    )
    print()


def main():
    print("# Mediciones reales\n")
    nary_table()
    avl_table()
    range_table()
    trie_table()


if __name__ == "__main__":
    main()
