Cómo diseñar y escribir las clases de árbol en Python orientado a objetos, en inglés, con estilo humano y no generado por IA.

Python POO para árboles, escrito como lo haría una persona
1. Diseño antes de código

Escribe en docs/DESIGN.md (puede ser un esquema de texto) las clases, qué guarda cada una y quién llama a quién. Reglas de diseño:

Un concepto, una clase: Node, la estructura (Tree, AVLTree, Trie...) y una fachada.
Los nodos guardan datos y enlaces; la lógica vive en el árbol.
La fachada (por ejemplo Explorer o Manager) es lo único que conoce la capa web. Mantiene sincronizadas las estructuras (si borras algo en una, se borra en todas).
Las invariantes (nombres únicos, balance, índices) se modifican desde un solo lugar.
Errores con ValueError / KeyError y mensajes que digan qué pasó y con qué dato.
2. Estructura de carpetas
main.py
src/<package_name>/   estructuras + fachada
src/server.py         API JSON mínima (http.server)
web/index.html
tests/
docs/                 CASE_STUDY.md, DESIGN.md, ANALYSIS.md
skills/ AGENT.md
3. Estructuras que debes saber implementar bien
Árbol n-ario: hijos en lista, puntero al padre, índice por nombre en un dict, recorridos preorden (iterativo con pila), postorden y BFS (con deque), ancestro común más bajo, profundidad, altura.
BST/AVL: insertar, eliminar (con sucesor en orden), las 4 rotaciones, consulta por rango podando subárboles, verificación de balance.
Trie: insertar, eliminar podando ramas muertas, sugerencias por prefijo.
(Otras según el caso: árbol de intervalos, segment tree, quadtree, Merkle, etc.)
4. Cómo se ve el código humano
Nombres cortos y precisos: climb, heir, lo, hi, trail. Nada de helper_function_1.
Comentarios que explican por qué o avisan de una trampa, nunca lo que ya dice la línea de abajo. Ejemplo bueno: # rotations change the subtree root, so the caller must reattach it.
Docstring solo en métodos públicos, una o dos líneas, sin secciones Args: / Returns:.
Funciones pequeñas, sin sobreingeniería: nada de patrones que el problema no necesita.
Nada de banners decorativos, emojis, # Step 1, ni anotaciones de tipo en cada auxiliar privado.
Variación natural: no todas las funciones tienen la misma longitud ni el mismo formato.
Los tests nombran el comportamiento (test_remove_branch_updates_every_index), no test_1.
5. Pruebas (unittest)

Cubre siempre: árbol vacío, duplicados, eliminar la raíz, eliminar una rama completa y que todas las estructuras queden sincronizadas, entrada ordenada (peor caso del BST) y errores esperados.

6. Lista de verificación antes de cada commit
 ¿Puedo explicar en voz alta la complejidad de cada método?
 ¿Todo identificador, comentario y mensaje está en inglés?
 ¿Los tests pasan y los viste correr?
 ¿El diff se lee como si lo hubiera escrito una persona?