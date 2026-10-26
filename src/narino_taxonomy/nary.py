"""N-ary tree for the taxonomic hierarchy.

Children live in a list and every node keeps a pointer to its parent. That
pointer is what makes "climb to the root" cheap: no lookup and no rebuilding of
the lineage.
"""

import unicodedata
from collections import deque


def slug(text):
    """Turn a display name into a stable, URL-safe key fragment."""
    normalized = unicodedata.normalize("NFKD", text)
    plain = normalized.encode("ascii", "ignore").decode("ascii")
    pieces = []
    previous_dash = False
    for char in plain.lower():
        if char.isalnum():
            pieces.append(char)
            previous_dash = False
        elif not previous_dash:
            pieces.append("-")
            previous_dash = True
    return "".join(pieces).strip("-")


class TaxonomyNode:
    """A taxon: its name, rank, parent link, children and optional species."""

    __slots__ = ("key", "name", "rank", "parent", "children", "species")

    def __init__(self, key, name, rank, parent=None, species=None):
        self.key = key
        self.name = name
        self.rank = rank
        self.parent = parent
        self.children = []
        self.species = species


class TaxonomyTree:
    """Hierarchy of taxa indexed by key, with parent pointers for climbing."""

    def __init__(self):
        self.root = None
        self._index = {}

    def add_root(self, name, rank):
        if self.root is not None:
            raise ValueError("The taxonomy already has a root")
        node = TaxonomyNode(slug(name), name, rank)
        self.root = node
        self._index[node.key] = node
        return node

    def add_child(self, parent_key, name, rank, species=None):
        parent = self.require(parent_key)
        if parent.species is not None:
            raise ValueError(f"Cannot add a child under species '{parent.name}'")
        key = f"{parent.key}/{slug(name)}"
        if key in self._index:
            raise ValueError(f"A taxon with key '{key}' already exists")
        node = TaxonomyNode(key, name, rank, parent, species)
        parent.children.append(node)
        self._index[key] = node
        return node

    def find(self, key):
        return self._index.get(key)

    def require(self, key):
        node = self._index.get(key)
        if node is None:
            raise KeyError(f"No taxon with key '{key}'")
        return node

    def __len__(self):
        return len(self._index)

    def lineage(self, key):
        """Return the path from the root down to the node."""
        node = self.require(key)
        path = []
        while node is not None:
            path.append(node)
            node = node.parent
        path.reverse()
        return path

    def climb(self, key):
        """Yield the node and its ancestors, starting at the node itself."""
        node = self.require(key)
        while node is not None:
            yield node
            node = node.parent

    def depth(self, key):
        return len(self.lineage(key)) - 1

    def lca(self, key_a, key_b):
        """Lowest common ancestor of two nodes, found by walking both parents."""
        ancestors = {node.key for node in self.climb(key_a)}
        for node in self.climb(key_b):
            if node.key in ancestors:
                return node
        raise ValueError("The two nodes do not share a root")

    def preorder(self, key=None):
        """Root first, then each child subtree from left to right."""
        start = self.root if key is None else self.require(key)
        if start is None:
            return
        stack = [start]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))

    def _postorder_from(self, start):
        if start is None:
            return
        stack = [start]
        visited = []
        while stack:
            node = stack.pop()
            visited.append(node)
            stack.extend(node.children)
        for node in reversed(visited):
            yield node

    def postorder(self, key=None):
        """Children before their parent, so counts and heights settle in one pass."""
        start = self.root if key is None else self.require(key)
        yield from self._postorder_from(start)

    def bfs(self, key=None):
        """Level by level, which is what the width-by-level statistic needs."""
        start = self.root if key is None else self.require(key)
        if start is None:
            return
        queue = deque([start])
        while queue:
            node = queue.popleft()
            yield node
            queue.extend(node.children)

    def height(self, key=None):
        start = self.root if key is None else self.require(key)
        if start is None:
            return 0
        heights = {}
        for node in self._postorder_from(start):
            if node.children:
                heights[node.key] = 1 + max(heights[child.key] for child in node.children)
            else:
                heights[node.key] = 0
        return heights[start.key]

    def width_by_level(self, key=None):
        start = self.root if key is None else self.require(key)
        if start is None:
            return []
        widths = []
        level = [start]
        while level:
            widths.append(len(level))
            level = [child for node in level for child in node.children]
        return widths

    def count(self, key=None):
        return sum(1 for _ in self.preorder(key))

    def leaf_count(self, key=None):
        return sum(1 for node in self.preorder(key) if not node.children)

    def subtree_species(self, key):
        return [node.species for node in self.preorder(key) if node.species is not None]

    def remove_branch(self, key):
        """Detach a subtree and drop every one of its nodes from the index."""
        node = self.require(key)
        if node.parent is None:
            raise ValueError("The root of the taxonomy cannot be removed")
        species = self.subtree_species(key)
        nodes = [item.key for item in self.preorder(key)]
        node.parent.children.remove(node)
        for node_key in nodes:
            del self._index[node_key]
        return {"nodes": nodes, "species": species}

    def _annotations(self):
        heights, counts, lows, highs = {}, {}, {}, {}
        for node in self._postorder_from(self.root):
            if node.children:
                heights[node.key] = 1 + max(heights[child.key] for child in node.children)
                counts[node.key] = sum(counts[child.key] for child in node.children)
                child_lows = [lows[child.key] for child in node.children if lows[child.key] is not None]
                child_highs = [highs[child.key] for child in node.children if highs[child.key] is not None]
                lows[node.key] = min(child_lows) if child_lows else None
                highs[node.key] = max(child_highs) if child_highs else None
            else:
                heights[node.key] = 0
                if node.species is not None:
                    counts[node.key] = 1
                    lows[node.key] = node.species.min_altitude
                    highs[node.key] = node.species.max_altitude
                else:
                    counts[node.key] = 0
                    lows[node.key] = None
                    highs[node.key] = None
        return heights, counts, lows, highs

    def to_dict(self):
        """Nested payload for the web UI, annotated in a single bottom-up pass."""
        if self.root is None:
            return None
        heights, counts, lows, highs = self._annotations()

        def pack(node, depth):
            payload = {
                "key": node.key,
                "name": node.name,
                "rank": node.rank,
                "depth": depth,
                "height": heights[node.key],
                "species_count": counts[node.key],
                "altitude": [lows[node.key], highs[node.key]],
                "species": node.species.as_dict() if node.species else None,
                "children": [pack(child, depth + 1) for child in node.children],
            }
            return payload

        return pack(self.root, 0)
