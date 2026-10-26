# Explorador taxonómico de la biodiversidad de Nariño

Una aplicación de escritorio local que explora la biodiversidad de Nariño como
una taxonomía real: **reino → filo → clase → orden → familia → especie**. No es
una lista de especies: la jerarquía, el índice por altitud y el autocompletado
son tres árboles coordinados por una fachada.

## Qué permite hacer

- Navegar la jerarquía y ver el camino de una especie a la raíz, su profundidad
  y su altura.
- Calcular el ancestro común más cercano de dos especies.
- Recorrer el árbol en preorden, postorden y por niveles (BFS).
- Consultar qué especies cruzan un rango de altitud.
- Autocompletar nombres científicos por prefijo.
- Agregar una especie a una familia y eliminar una rama completa sin dejar
  datos huérfanos.
- Ver estadísticas reales: altura, ancho por nivel, rotaciones del AVL, balance
  y consistencia entre las tres estructuras.

## Estructuras usadas

| Estructura | Archivo | Papel |
| --- | --- | --- |
| Árbol n-ario | `src/narino_taxonomy/nary.py` | Jerarquía, camino a la raíz, LCA, recorridos, ancho por nivel |
| AVL | `src/narino_taxonomy/avl.py` | Índice por `(altitud mínima, nombre científico)` y consulta por rango |
| Trie | `src/narino_taxonomy/trie.py` | Autocompletado de nombres científicos |
| Fachada | `src/narino_taxonomy/explorer.py` | Mantiene sincronizadas las tres estructuras |
| Datos semilla | `src/narino_taxonomy/seed.py` | 20 especies de Nariño con altitudes aproximadas |

## Cómo ejecutar

Requiere Python 3.10 o superior y solo biblioteca estándar.

```bash
python main.py
```

Abre `http://127.0.0.1:8000/` en el navegador. Opciones:

```bash
python main.py --port 8080
python main.py --no-browser
```

`Ctrl+C` detiene el servidor.

## Cómo probar

```bash
python -m unittest discover tests
```

La suite cubre árbol vacío, duplicados, borrado de la raíz, entrada ordenada,
borrado de una rama completa, sincronización de las tres estructuras y casos
borde de cada operación. Son 55 pruebas.

Para reproducir las mediciones del análisis:

```bash
python bench/benchmark.py
```

## Mapa de carpetas

```
main.py                     punto de entrada
src/narino_taxonomy/        estructuras, fachada y datos semilla
src/server.py               API JSON y servidor de archivos (http.server)
web/index.html              interfaz completa: HTML, CSS y JS propios
tests/                      pruebas unittest
bench/benchmark.py          mediciones con time.perf_counter
docs/CASE_STUDY.md          decisión del caso y datos
docs/DESIGN.md              clases, invariantes, API y plan de diseño
docs/ANALYSIS.md            análisis profundo y resultados reales
bench/results.md            salida de la última corrida del benchmark
AGENT.md                    instrucciones del taller
skills/                     las cinco skills de referencia
```

## Documentación

- [Caso de estudio](docs/CASE_STUDY.md)
- [Diseño de clases y API](docs/DESIGN.md)
- [Análisis de estructuras y mediciones](docs/ANALYSIS.md)

## Interfaz

`web/index.html` es un solo archivo sin CDN ni compilación: funciona sin
internet. La identidad visual está inspirada en las librerías de interfaz
HeroUI (superficies, píldoras y modales), Skiper UI (bloques bento y
degradados), AnimMasterLib (entradas suaves) y Vengence UI (auroras y brillos).
El taller exige un único HTML con recursos locales, así que esos patrones se
implementaron con CSS propio en lugar de cargar las librerías por CDN. El
elemento memorable es la regla vertical de altitud: cada especie aparece como
una barra sobre el perfil del páramo.

## Datos

Las 20 especies y sus altitudes son aproximadas. El objetivo del taller es la
estructura de datos, no la precisión biológica de cada rango. Los nombres
comunes están en español y los identificadores, comentarios y mensajes de error
del código en inglés.

## Repositorio

https://github.com/miguelcebing/taller-arboles-estructuras.git
