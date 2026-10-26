"""Prefix index for scientific names.

Each edge consumes one folded character. Terminal nodes keep the original
display spelling so the UI never shows a lowercased name.
"""

import unicodedata


def fold(text):
    normalized = unicodedata.normalize("NFKD", text)
    plain = normalized.encode("ascii", "ignore").decode("ascii")
    return plain.casefold().strip()


class TrieNode:
    __slots__ = ("children", "term")

    def __init__(self):
        self.children = {}
        self.term = None


class Trie:
    """Prefix tree with dead-branch pruning on removal."""

    def __init__(self):
        self.root = TrieNode()
        self._size = 0
        self._nodes = 1

    def __len__(self):
        return self._size

    def insert(self, name, species_key):
        if not name or not name.strip():
            raise ValueError("A scientific name cannot be empty")
        node = self.root
        for char in fold(name):
            child = node.children.get(char)
            if child is None:
                child = TrieNode()
                node.children[char] = child
                self._nodes += 1
            node = child
        if node.term is not None:
            raise ValueError(f"The name '{name}' is already in the trie")
        node.term = (name.strip(), species_key)
        self._size += 1

    def remove(self, name):
        folded = fold(name)
        node = self.root
        trail = []
        for char in folded:
            child = node.children.get(char)
            if child is None:
                raise KeyError(f"The name '{name}' is not in the trie")
            trail.append((node, char, child))
            node = child
        if node.term is None:
            raise KeyError(f"The name '{name}' is not a stored word")
        node.term = None
        self._size -= 1
        for parent, char, child in reversed(trail):
            if child.term is None and not child.children:
                del parent.children[char]
                self._nodes -= 1
            else:
                break

    def contains(self, name):
        node = self._walk(fold(name))
        return node is not None and node.term is not None

    def _walk(self, folded):
        node = self.root
        for char in folded:
            node = node.children.get(char)
            if node is None:
                return None
        return node

    def suggest(self, prefix, limit=8):
        """Return (display name, species key) pairs in alphabetical order."""
        if limit <= 0:
            return []
        start = self._walk(fold(prefix))
        if start is None:
            return []
        results = []
        stack = [start]
        while stack and len(results) < limit:
            node = stack.pop()
            if node.term is not None:
                results.append(node.term)
            for char in sorted(node.children, reverse=True):
                stack.append(node.children[char])
        results.sort(key=lambda pair: pair[0].casefold())
        return results[:limit]

    def words(self):
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node.term is not None:
                yield node.term
            for char in sorted(node.children, reverse=True):
                stack.append(node.children[char])

    def node_count(self):
        return self._nodes

    def stats(self):
        return {"size": self._size, "nodes": self._nodes}
