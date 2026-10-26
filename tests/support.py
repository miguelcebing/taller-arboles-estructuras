from src.narino_taxonomy.nary import slug
from src.narino_taxonomy.species import Species


def make_species(name, min_altitude, max_altitude, key=None, common="common"):
    return Species(
        key or f"family/{slug(name)}",
        name,
        common,
        min_altitude,
        max_altitude,
        "family",
    )
