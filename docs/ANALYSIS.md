# Análisis de las estructuras

Este documento explica por qué el explorador taxonómico de Nariño necesita tres
árboles y no una lista. Todas las cifras de la sección de mediciones salen de
`bench/benchmark.py`; el volcado de la última ejecución quedó en
`bench/results.md`.

## 1. Fundamentos con los datos del caso

- **Nodo:** cada taxón o especie. La raíz es el nodo `Biodiversidad de Nariño`,
  de rango `raíz`; una hoja es una especie, por ejemplo *Bothriechis
  schlegelii*.
- **Raíz:** el único nodo sin padre. En este caso es un nodo virtual que reúne
  los reinos `Animalia` y `Plantae`; no representa un taxón biológico, sino el
  punto de partida de la jerarquía.
- **Padre e hijo:** `Felidae` es padre de *Puma concolor* y de *Leopardus
  tigrinus*; ambos son hijos de la misma familia.
- **Grado:** número de hijos directos. `Mammalia` tiene grado 5 (Carnivora,
  Perissodactyla, Artiodactyla, Rodentia y Chiroptera). Una especie tiene grado
  0 porque es hoja.
- **Profundidad:** número de aristas desde la raíz hasta el nodo. La raíz tiene
  profundidad 0; *Puma concolor* tiene profundidad 6.
- **Altura:** número de aristas del camino más largo desde el nodo hasta una
  hoja. La raíz tiene altura 6; una especie tiene altura 0.
- **Nivel:** conjunto de nodos con la misma profundidad. El nivel 4 del caso
  agrupa los 16 órdenes; el nivel 5, las 18 familias.
- **Subárbol:** un nodo y todos sus descendientes. El subárbol de `Felidae`
  contiene dos especies; el de `Plantae`, seis.
- **Árbol n-ario:** cada nodo puede tener cualquier número de hijos. La
  taxonomía es n-aria por naturaleza: `Mammalia` tiene cinco órdenes y
  `Trochilidae` tiene dos especies.
- **Árbol binario:** cada nodo tiene como máximo dos hijos. El AVL del caso es
  binario porque su clave es un par ordenado `(altitud, nombre)`.
- **Árbol balanceado:** la diferencia de altura entre los subárboles izquierdo y
  derecho de cada nodo se mantiene pequeña. En el AVL, el factor de balance debe
  estar en `[-1, 1]`.

### Forma real del árbol taxonómico

El árbol semilla tiene 65 nodos y 20 especies. Su altura es 6 y el ancho por
nivel es:

```
nivel 0:  1   (raíz)
nivel 1:  2   (reinos)
nivel 2:  2   (filos)
nivel 3:  6   (clases)
nivel 4: 16   (órdenes)
nivel 5: 18   (familias)
nivel 6: 20   (especies)
```

Es un árbol **alto y delgado**: muchos niveles con pocos hijos por nodo. Eso
importa porque el costo del camino a la raíz y del ancestro común es O(h), y
aquí `h = 6`, no `log₂(65) ≈ 6` por casualidad: la forma de los datos manda.

## 2. Árbol n-ario de la taxonomía

### Forma y crecimiento

Cada nodo guarda una lista de hijos y un puntero al padre. La altura depende del
grado y de cómo se reparten los nodos. En el peor caso, una cadena de `n` nodos
tiene altura `n - 1`; en el mejor caso, un árbol lleno de grado `b` tiene altura
`⌈log_b(n(b-1)+1)⌉ - 1`. La medición con `n = 10 000` y grado 4 dio altura 7,
igual al mínimo teórico; la cadena dio altura 9 999.

### Invariantes

- Cada nodo tiene una clave única dentro del índice `key → nodo`.
- Todo nodo distinto de la raíz tiene un padre y aparece exactamente una vez en
  la lista de hijos de ese padre.
- Un nodo de rango `especie` no tiene hijos y guarda un registro `Species`.
- El índice y los enlaces no se contradicen: si un nodo está en el índice, es
  alcanzable desde la raíz.

### Operaciones

| Operación | Mejor caso | Promedio | Peor caso |
| --- | --- | --- | --- |
| `add_child` | O(1) | O(1) | O(1) con el índice por clave |
| `find` | O(1) | O(1) | O(1) |
| `lineage` / `climb` | O(h) | O(h) | O(n) en una cadena |
| `lca` | O(h) | O(h) | O(n) en una cadena |
| `preorder` / `postorder` / `bfs` | O(n) | O(n) | O(n) |
| `height` / `width_by_level` | O(n) | O(n) | O(n) |
| `remove_branch` | O(s) | O(s) | O(n), con `s` nodos del subárbol |

`height`, `postorder` y `width_by_level` se implementaron con pilas y colas
explícitas. Una cadena de 10 000 nodos se recorre sin agotar la pila de
recursión de Python.

### Por qué no una lista o un diccionario

- Una **lista plana** de especies obliga a buscar el padre de cada una para
  reconstruir el camino. El camino a la raíz pasaría de O(h) a O(n·h) o exigiría
  duplicar los ancestros.
- Un **diccionario** `nombre → especie` responde igualdad en O(1), pero no
  conserva la relación padre-hijo. El ancestro común tendría que reconstruirse
  con una tabla auxiliar.
- El **árbol n-ario** hace que subir por los padres sea O(1) por salto y que los
  recorridos respondan preguntas distintas con una sola estructura.

### Argumento de corrección del LCA

Se guardan las claves de todos los ancestros de `a` en un conjunto y se sube
desde `b` hasta el primer nodo que aparezca en ese conjunto. Ese nodo es el
ancestro común de menor profundidad: cualquier ancestro más bajo de `b` no está
en el camino de `a`, y cualquier ancestro más alto está por encima del primero
que se encuentra. El costo es O(h) en tiempo y O(h) en memoria.

### Casos borde

- Árbol vacío: altura 0, ancho `[]`, recorridos vacíos.
- Eliminar la raíz: se rechaza con `ValueError`; la raíz es el punto de anclaje
  de la taxonomía.
- Clave repetida: `add_child` lanza `ValueError` y no modifica el árbol.
- Padre inexistente: `KeyError` con la clave que falló.
- Rama sin especies: se puede eliminar; no deja nodos en el índice.
- Filtro de la interfaz: no modifica el árbol, solo la vista.

## 3. AVL por altitud

### Forma y crecimiento

Es un árbol binario de búsqueda con clave compuesta
`(altitud_mínima, nombre_científico)`. La altura se mantiene logarítmica por las
rotaciones. Con 20 especies la altura es 5; con 10 000 altitudes ordenadas la
altura es 14, mientras un BST simple se convierte en una cadena de altura
10 000.

### Invariantes

- Para todo nodo, `|height(left) - height(right)| ≤ 1`.
- Todas las claves del subárbol izquierdo son menores que la del nodo y todas
  las del derecho son mayores.
- No hay claves repetidas. La clave compuesta evita el choque entre especies
  que comparten altitud mínima; por ejemplo, cinco especies comienzan en
  1 800 m.
- Cada nodo guarda `end`, el máximo `max_altitude` de su subárbol. Es un
  aumento de intervalo que permite podar ramas que terminan antes del límite
  inferior de la consulta.

### Operaciones

| Operación | Mejor caso | Promedio | Peor caso |
| --- | --- | --- | --- |
| `insert` | O(log n) | O(log n) | O(log n) |
| `remove` | O(log n) | O(log n) | O(log n) |
| `find` | O(1) | O(log n) | O(log n) |
| `range_query` | O(log n + m) | O(log n + m) | O(n) si `m ≈ n` |
| `in_order` | O(n) | O(n) | O(n) |
| `is_balanced` | O(n) | O(n) | O(n) |

`m` es el número de especies que cruzan el rango. La consulta devuelve
intersección de intervalos: una especie entra si
`min_altitude ≤ hi` y `max_altitude ≥ lo`. El recorrido poda con `end < lo` y
con `key[0] > hi`; cuando la respuesta es una fracción grande de `n`, el costo
se acerca a O(n) porque hay que emitir muchas especies.

### Por qué no una lista ordenada, un BST simple o un diccionario

- **Lista ordenada:** la búsqueda binaria del rango es O(log n), pero insertar o
  borrar cuesta O(n) por el desplazamiento. El caso tiene altas y bajas desde la
  interfaz.
- **BST simple:** con altitudes insertadas en orden, la altura es O(n). La
  medición con 10 000 especies dio altura 10 000 y 6 474 ms de inserción; el AVL
  dio altura 14 y 481 ms.
- **Diccionario:** no responde rangos; habría que recorrer todas las claves.

### Cota de altura y corrección

La altura de un AVL con `n` nodos cumple
`h ≤ 1.44 · log₂(n + 2) - 0.33`. Para `n = 10 000`, la cota es
`1.44 · log₂(10 002) ≈ 19.1`; la altura medida fue 14. La inserción y el borrado
restauran el factor de balance con las cuatro rotaciones (LL, RR, LR, RL); cada
rotación cuesta O(1) y se cuentan en `rotations`.

### Casos borde

- Árbol vacío: `size = 0`, altura 0, `is_balanced()` verdadero.
- Clave duplicada: `ValueError` con la altitud y el nombre.
- Borrar una clave inexistente: `KeyError`.
- Borrar la raíz: se reemplaza por el sucesor en orden y se rebalancea.
- Dos especies con la misma altitud mínima: la clave compuesta las mantiene
  separadas y el borrado no es ambiguo.
- Rango invertido: `ValueError`; la interfaz valida antes de llamar.
- Rango sin intersección: lista vacía.

## 4. Trie de nombres científicos

### Forma y crecimiento

Cada arista consume un carácter del nombre normalizado (minúsculas, sin tildes).
Los 20 nombres del caso generan 338 nodos; 10 000 nombres sintéticos se
construyeron en 165.76 ms. La altura del trie es el largo del nombre más largo,
no el número de nombres.

### Invariantes

- Cada nodo tiene como máximo un hijo por carácter.
- Un nodo terminal guarda el nombre con su grafía original y la clave de la
  especie; los nodos intermedios no guardan especies.
- Al borrar, las ramas que quedan sin terminales ni hijos se podan. El número de
  nodos no crece para siempre.
- El trie y el registro de especies apuntan a las mismas claves.

### Operaciones

| Operación | Mejor caso | Promedio | Peor caso |
| --- | --- | --- | --- |
| `insert` | O(L) | O(L) | O(L) |
| `remove` | O(L) | O(L) | O(L) |
| `contains` | O(L) | O(L) | O(L) |
| `suggest` | O(L + k) | O(L + k) | O(L + k) |
| `words` | O(n·L) | O(n·L) | O(n·L) |

`L` es el largo del prefijo o del nombre y `k` el número de sugerencias pedidas.
La búsqueda por prefijo comparte el camino `p-u` entre *Puma concolor* y *Puya
clava-herculis*; un diccionario tendría que comparar el prefijo contra todas las
claves.

### Por qué no un diccionario o una lista

- **Diccionario:** solo responde igualdad. Para un prefijo habría que recorrer
  todas las claves y comparar el inicio.
- **Lista:** el filtro lineal cuesta O(n·L) por consulta. En la medición con
  10 000 nombres y 1 000 prefijos, el trie promedió 192.4 µs y la lista
  3 270.2 µs: 17 veces más rápido.
- **Trie:** comparte prefijos y poda ramas muertas, que es exactamente lo que
  pide el autocompletado.

### Corrección y casos borde

El descenso por los caracteres del prefijo es determinista. Si el camino no
existe, no hay sugerencias. Si existe, un recorrido en profundidad recolecta los
terminales en orden alfabético y se corta al llegar al límite. Se probaron
nombres vacíos, duplicados, prefijos parciales que no son palabras
(`Puma` frente a `Puma concolor`), mayúsculas, tildes y borrado de una de dos
ramas que comparten prefijo.

## 5. Recorridos y su propósito

| Recorrido | Pregunta del caso | Por qué ese orden |
| --- | --- | --- |
| **Preorden** | ¿Cómo se pinta la jerarquía completa desde los reinos hacia las especies? | El padre aparece antes que sus hijos; el árbol se dibuja sin volver atrás. |
| **Postorden** | ¿Cuántas especies y qué rango de altitud tiene cada rama? | Los hijos se resuelven antes que el padre; los conteos y los mínimos/máximos se acumulan en una sola pasada. |
| **BFS** | ¿Cuál es el ancho de cada nivel y cómo se comparan ramas de la misma profundidad? | Visita por niveles; el ancho se obtiene contando cada nivel. |
| **Inorden del AVL** | ¿Cuál es el orden de especies por altitud? | En un árbol binario de búsqueda, inorden devuelve las claves ordenadas. |

El preorden y el postorden se usan además para construir la vista anidada del
árbol (`to_dict`) y para calcular las anotaciones de cada nodo. El BFS alimenta
la tabla de ancho por nivel de la pestaña de estadísticas.

## 6. Mediciones reales

Entorno de la ejecución: Python 3.11.0, Windows, `bench/benchmark.py` con
`time.perf_counter`. Los tiempos varían con la carga de la máquina; por eso se
reporta la corrida guardada en `bench/results.md`, no un valor idealizado.

### Crecimiento del árbol n-ario

| n | Altura bushy (grado 4) | Altura cadena | Altura mínima teórica | Ancho máximo bushy | Construcción bushy (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 4 | 99 | 4 | 64 | 0.77 |
| 1 000 | 5 | 999 | 5 | 659 | 4.26 |
| 10 000 | 7 | 9 999 | 7 | 4 539 | 81.21 |

La cadena de 10 000 nodos se construyó en 992.99 ms y su altura fue 9 999. La
forma de los datos cambia por completo el costo de subir a la raíz: en el árbol
bushy la altura es 7; en la cadena es 9 999.

### AVL contra BST simple con altitudes ordenadas

| n | Altura BST | Altura AVL | Rotaciones AVL | BST (ms) | AVL (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 100 | 7 | 93 | 0.84 | 2.02 |
| 1 000 | 1 000 | 10 | 990 | 61.79 | 17.37 |
| 10 000 | 10 000 | 14 | 9 986 | 6 474.46 | 481.15 |

El BST simple degenera en una lista: su altura es `n`. El AVL mantiene altura
logarítmica y paga rotaciones (9 986 para 10 000 inserciones ordenadas). El
costo de inserción del AVL es menor incluso con ese trabajo extra.

### Consulta por rango contra recorrido lineal

Se probaron dos regímenes con 10 000 especies y 300 consultas por fila. En los
rangos largos, la respuesta promedio es una fracción grande de `n`; en los
rangos cortos, es selectiva.

| Régimen | Ancho (m) | AVL promedio (µs) | Lineal promedio (µs) | Aceleración | Resultados promedio |
| --- | ---: | ---: | ---: | ---: | ---: |
| Rangos largos (100-1500 m) | 200 | 2 322.9 | 1 902.3 | 0.8× | 1 849.2 |
| Rangos largos (100-1500 m) | 500 | 3 144.9 | 1 594.5 | 0.5× | 2 379.6 |
| Rangos largos (100-1500 m) | 1 000 | 4 502.6 | 2 191.2 | 0.5× | 3 324.5 |
| Rangos cortos (20-80 m) | 100 | 406.0 | 3 125.3 | 7.7× | 300.1 |
| Rangos cortos (20-80 m) | 200 | 793.5 | 2 557.0 | 3.2× | 500.1 |
| Rangos cortos (20-80 m) | 500 | 1 300.2 | 2 869.4 | 2.2× | 1 096.9 |

La lectura honesta: el AVL gana cuando la consulta es selectiva; cuando el
resultado es casi todo el conjunto, el recorrido lineal es competitivo porque
el costo dominante es emitir las respuestas. El AVL no es magia: su ventaja es
O(log n + m), y si `m` es grande, `m` manda. Para el caso real, con 20 especies,
la diferencia es despreciable; la estructura se justifica por las altas y bajas
y por el crecimiento.

### Autocompletado contra filtro lineal

| Nombres | Consultas | Trie promedio (µs) | Lista promedio (µs) | Aceleración | Construcción (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 000 | 1 000 | 192.4 | 3 270.2 | 17.0× | 165.76 |

### Métricas del árbol semilla

| Estructura | Métrica | Valor |
| --- | --- | ---: |
| Taxonomía | Nodos | 65 |
| Taxonomía | Especies | 20 |
| Taxonomía | Altura | 6 |
| Taxonomía | Hojas | 20 |
| Taxonomía | Ancho máximo | 20 (nivel 6) |
| AVL | Altura | 5 |
| AVL | Rotaciones | 19 |
| AVL | Balanceado | sí |
| Trie | Nombres | 20 |
| Trie | Nodos | 338 |
| Consistencia | Árbol = AVL = trie | sí |

Para reproducir:

```
python bench/benchmark.py
```

## 7. Sincronización entre estructuras

La fachada `Explorer` es el único lugar que modifica las tres estructuras. El
flujo de alta es:

1. Validar el padre, el nombre único y el rango de altitud.
2. Crear el nodo hoja en el árbol n-ario.
3. Insertar la especie en el AVL con clave `(min_altitude, nombre)`.
4. Insertar el nombre en el trie.
5. Guardar el registro en `registry` y en `_name_index`.

Si el paso 3 o el 4 falla, el bloque `try/except` deshace la inserción anterior
y elimina el nodo recién creado. El flujo de baja primero verifica que todas las
especies del subárbol existan en el registro, el AVL y el trie; solo entonces
desconecta la rama y borra cada especie de los índices. Esa verificación previa
evita dejar la mitad de una rama en una estructura y la otra mitad en otra.

`check_consistency()` compara cuatro conjuntos: especies del árbol, claves del
registro, claves del AVL y claves del trie. Devuelve las diferencias en ambas
direcciones (faltantes y sobrantes). La pestaña de estadísticas muestra el
resultado como “sin huérfanos” o “revisar”.

Los tests que protegen esta propiedad son:

- `test_add_species_updates_all_three_structures`
- `test_remove_family_cleans_avl_and_trie`
- `test_remove_species_leaf_keeps_the_family`
- `test_duplicate_scientific_name_is_rejected`
- `test_seed_has_twenty_species_and_is_consistent`

## 8. Limitaciones y mejoras futuras

- **Persistencia:** todo vive en memoria. Al reiniciar, se vuelve a la semilla.
  Una mejora sería cargar y guardar un JSON o una base SQLite.
- **Consulta por rango:** el AVL indexa por altitud mínima y responde por
  intersección. Si se necesitaran consultas por “altitud típica” o por
  contención estricta, convendría un árbol de intervalos o una segunda clave.
  La peor caso de la consulta actual es O(n) cuando casi todas las especies
  cruzan el rango.
- **Serialización del árbol:** `to_dict` es recursiva y depende de la altura.
  Con la taxonomía real (altura 6) no hay problema; para una cadena de 10 000
  nodos habría que hacerla iterativa o subir el límite de recursión.
- **Borrado de especies individuales:** si se borra la última especie de una
  familia, la familia queda vacía. Es válido para la taxonomía, pero podría
  podarse automáticamente para no dejar ramas sin especies.
- **Búsqueda por nombre común:** el trie solo indexa nombres científicos. Un
  segundo trie o un índice adicional resolvería el autocompletado por nombre
  común.
- **Concurrencia:** el servidor usa un `RLock` para serializar las peticiones.
  Es suficiente para un taller local; un despliegue real necesitaría otra
  estrategia.
- **Benchmark:** los tiempos varían con la máquina. Una mejora sería repetir
  cada medición varias veces, descartar el calentamiento y reportar mediana y
  desviación, en lugar de una sola corrida.

## 9. Conclusión

La taxonomía es una jerarquía real: el árbol n-ario es la única estructura que
guarda el padre y los hijos sin duplicar datos, y por eso el camino a la raíz y
el ancestro común salen en O(h). El AVL agrega el orden por altitud que el árbol
taxonómico no tiene y lo mantiene logarítmico ante inserciones ordenadas. El
trie explota los prefijos compartidos de los nombres científicos. La fachada
convierte tres estructuras independientes en una sola operación consistente:
agregar o eliminar una especie actualiza la jerarquía, el índice de altitud y
el autocompletado, y `check_consistency()` demuestra que no quedaron huérfanos.
