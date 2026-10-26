"""Seed taxonomy and species records for the Nariño explorer.

Altitudes are approximate on purpose: the workshop evaluates the structures,
not the biological precision of every range. Each record carries its full
lineage so a missing branch is created once and shared by every species below
it.
"""

from .nary import slug

ROOT_NAME = "Biodiversidad de Nariño"

SPECIES = [
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Mammalia", "clase"),
            ("Carnivora", "orden"),
            ("Ursidae", "familia"),
        ],
        "scientific": "Tremarctos ornatus",
        "common": "Oso de anteojos",
        "min": 1800,
        "max": 3800,
        "note": "El único úrsido de Suramérica; usa los bosques andinos y el páramo.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Mammalia", "clase"),
            ("Carnivora", "orden"),
            ("Felidae", "familia"),
        ],
        "scientific": "Puma concolor",
        "common": "Puma",
        "min": 1200,
        "max": 3200,
        "note": "Amplio rango altitudinal; se le registra desde el piedemonte hasta el páramo.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Mammalia", "clase"),
            ("Carnivora", "orden"),
            ("Felidae", "familia"),
        ],
        "scientific": "Leopardus tigrinus",
        "common": "Tigrillo",
        "min": 1500,
        "max": 2800,
        "note": "Felino pequeño de bosques montanos y bordes de páramo.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Mammalia", "clase"),
            ("Perissodactyla", "orden"),
            ("Tapiridae", "familia"),
        ],
        "scientific": "Tapirus pinchaque",
        "common": "Danta de montaña",
        "min": 2000,
        "max": 4000,
        "note": "Mamífero grande del bosque altoandino y el páramo.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Mammalia", "clase"),
            ("Artiodactyla", "orden"),
            ("Cervidae", "familia"),
        ],
        "scientific": "Mazama rufina",
        "common": "Venado de páramo",
        "min": 2200,
        "max": 3500,
        "note": "Venado pequeño asociado a matorrales y páramos.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Mammalia", "clase"),
            ("Rodentia", "orden"),
            ("Dinomyidae", "familia"),
        ],
        "scientific": "Dinomys branickii",
        "common": "Guagua loba",
        "min": 800,
        "max": 3200,
        "note": "Roedor grande y poco frecuente de bosques húmedos.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Mammalia", "clase"),
            ("Chiroptera", "orden"),
            ("Phyllostomidae", "familia"),
        ],
        "scientific": "Anoura geoffroyi",
        "common": "Murciélago de cola libre",
        "min": 1000,
        "max": 3500,
        "note": "Nectarívoro que visita flores de bosque andino.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Aves", "clase"),
            ("Cathartiformes", "orden"),
            ("Cathartidae", "familia"),
        ],
        "scientific": "Vultur gryphus",
        "common": "Cóndor andino",
        "min": 1800,
        "max": 4500,
        "note": "Ave carroñera de grandes altitudes; símbolo de los Andes.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Aves", "clase"),
            ("Apodiformes", "orden"),
            ("Trochilidae", "familia"),
        ],
        "scientific": "Ensifera ensifera",
        "common": "Pico de espada",
        "min": 2000,
        "max": 3300,
        "note": "Colibrí de pico extraordinariamente largo.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Aves", "clase"),
            ("Apodiformes", "orden"),
            ("Trochilidae", "familia"),
        ],
        "scientific": "Metallura tyrianthina",
        "common": "Colibrí paramuno",
        "min": 1500,
        "max": 3600,
        "note": "Colibrí común en bordes de bosque y páramo.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Aves", "clase"),
            ("Strigiformes", "orden"),
            ("Strigidae", "familia"),
        ],
        "scientific": "Asio stygius",
        "common": "Búho orejudo",
        "min": 1800,
        "max": 3000,
        "note": "Búho nocturno de bosques montanos.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Amphibia", "clase"),
            ("Anura", "orden"),
            ("Bufonidae", "familia"),
        ],
        "scientific": "Atelopus sp.",
        "common": "Cutín de Nariño",
        "min": 1800,
        "max": 3000,
        "note": "Rana endémica de altura, sensible a cambios del hábitat.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Amphibia", "clase"),
            ("Anura", "orden"),
            ("Centrolenidae", "familia"),
        ],
        "scientific": "Centrolene buckleyi",
        "common": "Ranita de cristal",
        "min": 1200,
        "max": 2600,
        "note": "Rana de cristal ligada a quebradas de bosque nublado.",
    },
    {
        "lineage": [
            ("Animalia", "reino"),
            ("Chordata", "filo"),
            ("Reptilia", "clase"),
            ("Squamata", "orden"),
            ("Viperidae", "familia"),
        ],
        "scientific": "Bothriechis schlegelii",
        "common": "Víbora de pestañas",
        "min": 400,
        "max": 1400,
        "note": "Serpiente arborícola de zonas bajas y medias.",
    },
    {
        "lineage": [
            ("Plantae", "reino"),
            ("Magnoliophyta", "filo"),
            ("Magnoliopsida", "clase"),
            ("Asterales", "orden"),
            ("Asteraceae", "familia"),
        ],
        "scientific": "Espeletia pycnophylla",
        "common": "Frailejón",
        "min": 2600,
        "max": 3800,
        "note": "Planta emblemática del páramo; almacena agua en sus hojas.",
    },
    {
        "lineage": [
            ("Plantae", "reino"),
            ("Magnoliophyta", "filo"),
            ("Magnoliopsida", "clase"),
            ("Rosales", "orden"),
            ("Rosaceae", "familia"),
        ],
        "scientific": "Polylepis incana",
        "common": "Árbol de papel",
        "min": 3000,
        "max": 4200,
        "note": "Árbol altoandino de corteza laminada.",
    },
    {
        "lineage": [
            ("Plantae", "reino"),
            ("Magnoliophyta", "filo"),
            ("Magnoliopsida", "clase"),
            ("Ericales", "orden"),
            ("Ericaceae", "familia"),
        ],
        "scientific": "Vaccinium floribundum",
        "common": "Mortiño",
        "min": 2400,
        "max": 3800,
        "note": "Arbusto de frutos comestibles en bordes de páramo.",
    },
    {
        "lineage": [
            ("Plantae", "reino"),
            ("Magnoliophyta", "filo"),
            ("Magnoliopsida", "clase"),
            ("Gentianales", "orden"),
            ("Rubiaceae", "familia"),
        ],
        "scientific": "Cinchona pubescens",
        "common": "Quina",
        "min": 1200,
        "max": 3000,
        "note": "Árbol de cuya corteza se extrae la quinina.",
    },
    {
        "lineage": [
            ("Plantae", "reino"),
            ("Magnoliophyta", "filo"),
            ("Liliopsida", "clase"),
            ("Poales", "orden"),
            ("Bromeliaceae", "familia"),
        ],
        "scientific": "Puya clava-herculis",
        "common": "Achupalla",
        "min": 2500,
        "max": 3800,
        "note": "Bromelia de roseta grande en páramos abiertos.",
    },
    {
        "lineage": [
            ("Plantae", "reino"),
            ("Magnoliophyta", "filo"),
            ("Liliopsida", "clase"),
            ("Asparagales", "orden"),
            ("Orchidaceae", "familia"),
        ],
        "scientific": "Odontoglossum gloriosum",
        "common": "Orquídea",
        "min": 1800,
        "max": 3200,
        "note": "Orquídea epífita de bosque húmedo montano.",
    },
]


def build_seed(explorer):
    """Fill an empty explorer with the seed taxonomy and species."""
    root = explorer.tree.add_root(ROOT_NAME, "raíz")
    for record in SPECIES:
        parent_key = root.key
        for name, rank in record["lineage"]:
            key = f"{parent_key}/{slug(name)}"
            node = explorer.tree.find(key)
            if node is None:
                node = explorer.tree.add_child(parent_key, name, rank)
            parent_key = node.key
        explorer.add_species(
            parent_key,
            record["scientific"],
            record["common"],
            record["min"],
            record["max"],
            record["note"],
        )
