# Caso de estudio: explorador taxonómico de la biodiversidad de Nariño

## Decisión

Se construye un explorador de la biodiversidad de Nariño organizado como una
taxonomía real: **reino → filo → clase → orden → familia → especie**. La
aplicación combina tres estructuras de árbol coordinadas por una fachada:

1. **Árbol n-ario** para la jerarquía taxonómica.
2. **Árbol AVL** con clave compuesta `(altitud mínima, nombre científico)` para
   consultar especies por rango de altitud.
3. **Trie** para autocompletar nombres científicos por prefijo.

El caso se eligió antes de escribir código y se mantiene como decisión cerrada.
Las fases 2 a 8 del taller se desarrollan a partir de él.

## Los tres candidatos

| Candidato | Pros | Contras |
| --- | --- | --- |
| Explorador taxonómico de la biodiversidad de Nariño | Jerarquía real y profunda; datos reconocibles de la región; permite combinar árbol n-ario, AVL y trie; se visualiza muy bien | Exige sincronizar tres estructuras al borrar |
| Agenda de reservas con árbol de intervalos | Problema real; el árbol de intervalos es poco común; detectar choques es natural | Menos variedad de estructuras; visualización más pobre; el árbol queda casi oculto tras el calendario |
| Control de versiones con árbol de Merkle | Muy poco común; el análisis de hashes es interesante | Difícil de explicar en una sustentación corta; poca variedad de operaciones visibles para el usuario |

## Por qué se eligió este caso

Se contrasta con los criterios obligatorios de la skill de selección:

- **Árbol esencial.** Si la taxonomía se guardara en una lista plana o en un
  diccionario, el camino a la raíz, el ancestro común más cercano y los
  recorridos exigirían reconstruir la jerarquía en cada consulta. El AVL y el
  trie tampoco tienen sustituto directo: una lista ordenada paga O(n) por
  inserción y un diccionario no resuelve prefijos.
- **Al menos cinco funciones.** El caso ofrece siete funciones distintas, con
  inserción/eliminación que conserva invariantes, consulta estructural,
  consulta por rango, consulta por prefijo, recorridos con propósito y
  estadísticas.
- **Datos reales y reconocibles.** Se usan 20 especies presentes o reportadas
  en Nariño, con altitudes aproximadas. El oso de anteojos, el cóndor andino,
  el frailejón y la danta de montaña permiten hablar del territorio sin trabajo
  adicional.
- **Alcance razonable.** Las tres estructuras son de tamaño de curso y los datos
  caben en un archivo semilla. El proyecto se termina en días.
- **Se ve bien en pantalla.** La jerarquía se muestra como un árbol colapsable
  y las especies se ubican sobre una regla vertical de altitud, lo que hace
  visible la estructura y no solo sus resultados.
- **Combinación de árboles.** La fachada `Explorer` es la única que conoce las
  tres estructuras y garantiza que un borrado no deje especies huérfanas.

## Funciones y estructura responsable

| Función | Estructura | Complejidad esperada |
| --- | --- | --- |
| Navegar la jerarquía y ver el camino de una especie a la raíz | Árbol n-ario con puntero al padre | O(h) |
| Ancestro común más cercano de dos nodos | Árbol n-ario | O(h) con h = altura del árbol |
| Recorridos preorden, postorden y BFS | Árbol n-ario | O(n) |
| Especies cuya altitud se cruza con un rango | AVL con clave `(altitud mínima, nombre)` | O(log n + k) |
| Autocompletado de nombres científicos | Trie | O(L + k), L = largo del prefijo |
| Eliminar una rama completa sin datos huérfanos | Fachada sobre las tres estructuras | O(s · (log n + L)) con s = especies de la rama |
| Estadísticas: altura, ancho por nivel, rotaciones, balance | Las tres estructuras | O(n) |

## Alternativas descartadas por función

- **Camino a la raíz:** una lista de ancestros por especie duplicaría datos y se
  desactualizaría al mover una rama. El puntero al padre es O(1) por salto.
- **Ancestro común:** comparar listas de todos los ancestros guardadas en un
  diccionario ocupa O(n·h) de memoria. Subir por los padres usa solo la altura.
- **Rango de altitud:** una lista ordenada permite búsqueda binaria, pero cada
  inserción o borrado cuesta O(n). Un BST simple degenera con altitudes
  ordenadas; el AVL conserva altura logarítmica.
- **Prefijos:** un diccionario de nombres solo responde igualdad. Recorrer todas
  las claves para filtrar por prefijo cuesta O(n·L); el trie comparte prefijos.
- **Borrado de rama:** borrar solo en el árbol n-ario dejaría especies en el AVL
  y en el trie. La fachada centraliza la operación y permite verificarlo.

## Datos de ejemplo

Las altitudes son aproximadas y sirven para probar la estructura, no como dato
biológico oficial. La columna “rango” es el intervalo en metros sobre el nivel
del mar.

| Reino | Filo | Clase | Orden | Familia | Especie | Nombre común | Rango (m) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Animalia | Chordata | Mammalia | Carnivora | Ursidae | *Tremarctos ornatus* | Oso de anteojos | 1800–3800 |
| Animalia | Chordata | Mammalia | Carnivora | Felidae | *Puma concolor* | Puma | 1200–3200 |
| Animalia | Chordata | Mammalia | Carnivora | Felidae | *Leopardus tigrinus* | Tigrillo | 1500–2800 |
| Animalia | Chordata | Mammalia | Perissodactyla | Tapiridae | *Tapirus pinchaque* | Danta de montaña | 2000–4000 |
| Animalia | Chordata | Mammalia | Artiodactyla | Cervidae | *Mazama rufina* | Venado de páramo | 2200–3500 |
| Animalia | Chordata | Mammalia | Rodentia | Dinomyidae | *Dinomys branickii* | Guagua loba | 800–3200 |
| Animalia | Chordata | Mammalia | Chiroptera | Phyllostomidae | *Anoura geoffroyi* | Murciélago de cola libre | 1000–3500 |
| Animalia | Chordata | Aves | Cathartiformes | Cathartidae | *Vultur gryphus* | Cóndor andino | 1800–4500 |
| Animalia | Chordata | Aves | Apodiformes | Trochilidae | *Ensifera ensifera* | Pico de espada | 2000–3300 |
| Animalia | Chordata | Aves | Apodiformes | Trochilidae | *Metallura tyrianthina* | Colibrí paramuno | 1500–3600 |
| Animalia | Chordata | Aves | Strigiformes | Strigidae | *Asio stygius* | Búho orejudo | 1800–3000 |
| Animalia | Chordata | Amphibia | Anura | Bufonidae | *Atelopus* sp. | Cutín de Nariño | 1800–3000 |
| Animalia | Chordata | Amphibia | Anura | Centrolenidae | *Centrolene buckleyi* | Ranita de cristal | 1200–2600 |
| Animalia | Chordata | Reptilia | Squamata | Viperidae | *Bothriechis schlegelii* | Víbora de pestañas | 400–1400 |
| Plantae | Magnoliophyta | Magnoliopsida | Asterales | Asteraceae | *Espeletia pycnophylla* | Frailejón | 2600–3800 |
| Plantae | Magnoliophyta | Magnoliopsida | Rosales | Rosaceae | *Polylepis incana* | Árbol de papel | 3000–4200 |
| Plantae | Magnoliophyta | Magnoliopsida | Ericales | Ericaceae | *Vaccinium floribundum* | Mortiño | 2400–3800 |
| Plantae | Magnoliophyta | Magnoliopsida | Gentianales | Rubiaceae | *Cinchona pubescens* | Quina | 1200–3000 |
| Plantae | Magnoliophyta | Liliopsida | Poales | Bromeliaceae | *Puya clava-herculis* | Achupalla | 2500–3800 |
| Plantae | Magnoliophyta | Liliopsida | Asparagales | Orchidaceae | *Odontoglossum gloriosum* | Orquídea | 1800–3200 |

## Decisiones de datos que afectan el diseño

- La **clave del AVL es compuesta**: `(altitud mínima, nombre científico)`.
  Cinco especies comparten 1800 m y tres comparten 1200 m; con solo la altitud
  la clave se repetiría y el borrado se volvería ambiguo.
- El AVL indexa por **altitud mínima** y guarda el rango completo en el
  registro. Una consulta `[lo, hi]` poda las claves mayores que `hi` y descarta
  las especies cuyo máximo queda por debajo de `lo`, de modo que responde por
  **intersección de intervalos**, que es lo que un biólogo espera al preguntar
  “¿qué especies viven entre 1500 y 3000 m?”.
- El trie normaliza a minúsculas y sin tildes. El nombre visible conserva la
  grafía científica original.
