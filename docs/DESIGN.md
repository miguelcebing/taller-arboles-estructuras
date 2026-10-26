# Diseño del explorador taxonómico

## Mapa de clases

```
Explorer (fachada)
├── TaxonomyTree          árbol n-ario de la jerarquía
│   └── TaxonomyNode      key, name, rank, parent, children, species
├── AVLTree               índice por (altitud mínima, nombre científico)
│   └── AVLNode           key, species, left, right, height
├── Trie                  índice de prefijos de nombres científicos
│   └── TrieNode          children, term
└── registry: dict[str, Species]
```

`Species` es un registro inmutable con `key`, `scientific_name`,
`common_name`, `min_altitude`, `max_altitude` y `parent_key`. Los nodos guardan
datos y enlaces; la lógica de cada estructura vive en su clase.

## Responsabilidades

| Clase | Guarda | Sabe hacer | No sabe |
| --- | --- | --- | --- |
| `TaxonomyNode` | nombre, rango, padre, hijos, especie si es hoja | nada de lógica | nada del AVL ni del trie |
| `TaxonomyTree` | índice `key → nodo`, raíz | insertar hijo, buscar, camino a la raíz, LCA, recorridos, altura, ancho, borrar rama | altitudes y prefijos |
| `AVLTree` | raíz, contador de rotaciones | insertar, borrar, buscar, consultar por rango, verificar balance | jerarquía y prefijos |
| `Trie` | raíz, número de palabras | insertar, borrar podando, sugerir por prefijo | jerarquía y altitudes |
| `Explorer` | las tres estructuras y el registro | coordinar altas y bajas, responder a la API, verificar consistencia | HTTP y HTML |

## Flujo de una inserción

1. `Explorer.add_species` valida padre existente, nombre único y rango válido.
2. Crea el `Species` y su nodo hoja en `TaxonomyTree`.
3. Inserta el registro en `AVLTree` con clave `(min_altitude, nombre)`.
4. Inserta el nombre normalizado en `Trie`.
5. Guarda el registro en `registry`.

Si el paso 3 o 4 fallara, se revierte el nodo del árbol y el registro para no
dejar datos huérfanos.

## Flujo de un borrado de rama

1. `Explorer.remove_branch` localiza el nodo y rechaza la raíz.
2. Recolecta las especies del subárbol con un recorrido preorden.
3. Por cada especie: la borra del AVL, del trie y del registro.
4. Desconecta el subárbol del padre y elimina todos sus nodos del índice.
5. Devuelve un resumen con especies y nodos eliminados.

La fachada es el único lugar donde se modifican las tres estructuras. Esa es la
invariante que impide datos huérfanos y la que comprueba `check_consistency()`,
expuesta también en `stats()`.

## Invariantes

- **Taxonomía:** cada nodo tiene un `key` único; todo nodo distinto de la raíz
  tiene padre; un nodo de rango `especie` no tiene hijos y sí tiene registro.
- **AVL:** para todo nodo, `|height(left) - height(right)| <= 1`; las claves del
  subárbol izquierdo son menores y las del derecho mayores; no hay claves
  repetidas.
- **Trie:** cada nodo tiene a lo sumo un hijo por letra; un nodo terminal guarda
  un nombre y la clave de su especie; las hojas no terminales se podan.
- **Sincronización:** el conjunto de especies de la taxonomía, del AVL, del trie
  y del registro es el mismo.

## Complejidades

| Operación | Estructura | Costo |
| --- | --- | --- |
| `find` / `add_child` | n-ario con índice | O(1) promedio |
| `lineage` / `lca` | n-ario | O(h) |
| `preorder` / `postorder` / `bfs` | n-ario | O(n) |
| `insert` / `remove` / `search` | AVL | O(log n) |
| `range_query` | AVL | O(log n + k) |
| `insert` / `remove` / `suggest` | trie | O(L + k) |
| `remove_branch` | fachada | O(s · (log n + L)) |

## API JSON

| Método | Ruta | Respuesta |
| --- | --- | --- |
| GET | `/api/tree` | árbol anidado con conteos y rangos |
| GET | `/api/node?key=` | ficha, camino a la raíz, profundidad y altura |
| GET | `/api/lca?a=&b=` | ancestro común y caminos |
| GET | `/api/traversal?type=` | preorden, postorden o BFS con propósito |
| GET | `/api/range?lo=&hi=` | especies que cruzan el rango |
| GET | `/api/autocomplete?prefix=` | sugerencias del trie |
| GET | `/api/altitude` | bandas de altitud para la regla visual |
| GET | `/api/stats` | métricas de las tres estructuras y consistencia |
| POST | `/api/species` | agrega una especie a una familia |
| POST | `/api/remove` | elimina una rama completa |

Los errores viajan como `{"error": "..."}` con estado 400, 404 o 500. Los
mensajes de error del código están en inglés; la interfaz los presenta en
español cuando corresponde.

## Plan de diseño del frontend

- **Paleta:** “páramo nocturno” `#0b1410`, musgo `#16302a`, liquen `#a7c957`,
  frailejón `#e9c46a`, niebla `#dce8e2`, orquídea `#d98cb3`. El verde y el
  dorado salen del páramo; el rosa aparece solo en acentos.
- **Tipografías:** serif de sistema (Iowan Old Style, Palatino, Georgia) para
  títulos y nombres científicos; sans de sistema para controles; monoespaciada
  para altitudes y métricas. Sin CDN, todo funciona sin internet.
- **Distribución:** encabezado con marca y píldoras de estado; bento de dos
  columnas con el árbol colapsable a la izquierda y un panel de pestañas a la
  derecha; en móvil se apila.
- **Elemento memorable:** una **regla de altitud vertical** dibujada como perfil
  de montaña, donde cada especie ocupa su banda real y se resalta al pasar el
  cursor. Es la identidad del caso y no una tarjeta genérica.
- **Movimiento:** transiciones cortas al abrir nodos, cambiar de pestaña y
  resaltar especies; se desactivan con `prefers-reduced-motion`.
- **Inspiración de librerías:** se adopta el lenguaje visual de HeroUI
  (superficies, píldoras, modales), Skiper UI (bloques bento y degradados),
  AnimMasterLib (entradas suaves) y Vengence UI (auroras y brillos), pero se
  implementa con CSS propio porque el taller exige un único HTML sin CDN ni
  compilación. No se inventan componentes de negocio que ya existan en esas
  librerías: se replican sus patrones de interacción con los recursos locales
  permitidos.
