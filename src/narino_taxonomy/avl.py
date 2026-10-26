"""AVL index of species keyed by (minimum altitude, scientific name).

The composite key matters: several species share the same lower altitude, so an
altitude-only key would collide and make removal ambiguous.
"""


def species_key(species):
    return (species.min_altitude, species.scientific_name.casefold())


class AVLNode:
    __slots__ = ("key", "species", "left", "right", "height", "end")

    def __init__(self, species):
        self.key = species_key(species)
        self.species = species
        self.left = None
        self.right = None
        self.height = 1
        self.end = species.max_altitude


class AVLTree:
    """Height-balanced binary search tree with a counter for rotations."""

    def __init__(self):
        self.root = None
        self.rotations = 0
        self._size = 0

    def __len__(self):
        return self._size

    def _height(self, node):
        return node.height if node is not None else 0

    def _refresh(self, node):
        node.height = 1 + max(self._height(node.left), self._height(node.right))
        # The subtree's highest end lets range_query discard branches that finish
        # before the lower bound, instead of walking every small altitude.
        node.end = node.species.max_altitude
        if node.left is not None:
            node.end = max(node.end, node.left.end)
        if node.right is not None:
            node.end = max(node.end, node.right.end)

    def _rotate_left(self, node):
        pivot = node.right
        node.right = pivot.left
        pivot.left = node
        self._refresh(node)
        self._refresh(pivot)
        self.rotations += 1
        return pivot

    def _rotate_right(self, node):
        pivot = node.left
        node.left = pivot.right
        pivot.right = node
        self._refresh(node)
        self._refresh(pivot)
        self.rotations += 1
        return pivot

    def _rebalance(self, node):
        self._refresh(node)
        balance = self._height(node.left) - self._height(node.right)
        if balance > 1:
            if self._height(node.left.left) < self._height(node.left.right):
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1:
            if self._height(node.right.right) < self._height(node.right.left):
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def insert(self, species):
        key = species_key(species)
        self.root = self._insert(self.root, species, key)
        self._size += 1

    def _insert(self, node, species, key):
        if node is None:
            return AVLNode(species)
        if key < node.key:
            node.left = self._insert(node.left, species, key)
        elif key > node.key:
            node.right = self._insert(node.right, species, key)
        else:
            raise ValueError(
                f"Species '{species.scientific_name}' is already indexed at {key[0]} m"
            )
        return self._rebalance(node)

    def find(self, key):
        node = self.root
        while node is not None:
            if key == node.key:
                return node.species
            node = node.left if key < node.key else node.right
        return None

    def contains(self, species):
        return self.find(species_key(species)) is not None

    def remove(self, key):
        if self.find(key) is None:
            raise KeyError(f"No species indexed with key {key}")
        self.root = self._remove(self.root, key)
        self._size -= 1

    def remove_species(self, species):
        self.remove(species_key(species))

    def _remove(self, node, key):
        if key < node.key:
            node.left = self._remove(node.left, key)
        elif key > node.key:
            node.right = self._remove(node.right, key)
        else:
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            heir = node.right
            while heir.left is not None:
                heir = heir.left
            node.key = heir.key
            node.species = heir.species
            node.right = self._remove(node.right, heir.key)
        return self._rebalance(node)

    def in_order(self):
        """Species sorted by altitude, then by scientific name."""
        stack = []
        node = self.root
        while stack or node is not None:
            while node is not None:
                stack.append(node)
                node = node.left
            node = stack.pop()
            yield node.species
            node = node.right

    def range_query(self, lo, hi):
        """Species whose altitude interval overlaps [lo, hi].

        Keys are lower bounds, so any key above hi can be pruned. A candidate
        still has to pass the max-altitude check because it may end below lo.
        The subtree's highest end prunes branches that finish before lo.
        """
        if lo > hi:
            raise ValueError(f"Range start {lo} is greater than range end {hi}")
        found = []
        self._collect(self.root, lo, hi, found)
        return found

    def _collect(self, node, lo, hi, found):
        if node is None or node.end < lo:
            return
        if node.key[0] > hi:
            self._collect(node.left, lo, hi, found)
            return
        self._collect(node.left, lo, hi, found)
        if node.species.max_altitude >= lo:
            found.append(node.species)
        self._collect(node.right, lo, hi, found)

    def height(self):
        return self._height(self.root)

    def is_balanced(self):
        heights = {}
        for node in self._postorder():
            left = heights.get(node.left.key, 0) if node.left else 0
            right = heights.get(node.right.key, 0) if node.right else 0
            if abs(left - right) > 1:
                return False
            heights[node.key] = 1 + max(left, right)
        return True

    def _postorder(self):
        if self.root is None:
            return
        stack = [self.root]
        visited = []
        while stack:
            node = stack.pop()
            visited.append(node)
            if node.left is not None:
                stack.append(node.left)
            if node.right is not None:
                stack.append(node.right)
        for node in reversed(visited):
            yield node

    def stats(self):
        return {
            "size": self._size,
            "height": self.height(),
            "rotations": self.rotations,
            "balanced": self.is_balanced(),
        }
