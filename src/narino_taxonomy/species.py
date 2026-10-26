"""Shared value object for a species record."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Species:
    """Immutable species record shared by the tree, the AVL index and the trie."""

    key: str
    scientific_name: str
    common_name: str
    min_altitude: int
    max_altitude: int
    parent_key: str
    note: str = ""

    def as_dict(self):
        return {
            "key": self.key,
            "scientific_name": self.scientific_name,
            "common_name": self.common_name,
            "min_altitude": self.min_altitude,
            "max_altitude": self.max_altitude,
            "parent_key": self.parent_key,
            "note": self.note,
        }
