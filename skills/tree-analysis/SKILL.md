Método para realizar el análisis profundo de la estructura de árbol: definiciones, invariantes, complejidad, comparaciones y mediciones reales.

Análisis profundo de los árboles del taller

El resultado va en docs/ANALYSIS.md. Debe poder leerse como la parte teórica de una sustentación.

Estructura obligatoria del documento
1. Fundamentos

Define con tus palabras y con ejemplos del caso: nodo, raíz, hoja, padre/hijo, grado, profundidad, altura, nivel, subárbol, árbol n-ario vs. binario, árbol balanceado.

2. Por cada estructura usada

Responde, en este orden:

Forma: cuántos hijos por nodo, cómo crece la altura respecto a n.
Invariantes: qué debe ser siempre cierto (p. ej. factor de balance en [-1, 1], una arista por letra en un trie).
Operaciones: tabla con mejor, promedio y peor caso de insertar, eliminar, buscar, consulta por rango/prefijo y recorridos.
Por qué esta estructura y no otra: compárala con lista, lista ordenada, dict y BST simple para cada función del caso.
Argumento de corrección o cota: por ejemplo, por qué la altura de un AVL es ≤ ~1.44·log₂(n+2), o por qué el ancestro común es O(h).
Casos borde y límites de la implementación.
3. Recorridos

Para cada recorrido (preorden, postorden, inorden, BFS) di qué pregunta del caso responde y por qué ese orden es el adecuado.

4. Mediciones reales

Crea bench/benchmark.py que mida con time.perf_counter:

altura real vs. altura teórica mínima con n creciente (100, 1 000, 10 000),
el peor caso del BST simple (entrada ordenada) contra el AVL,
el costo de la consulta por rango vs. recorrer una lista completa,
número de rotaciones realizadas. Pega los resultados reales en una tabla; nunca cifras inventadas. Expón las métricas estructurales (altura, ancho por nivel, rotaciones) también en el método stats() de la fachada para verlas en la UI.
5. Sincronización entre estructuras

Explica cómo la fachada garantiza que no queden datos huérfanos al insertar o eliminar, y qué test lo protege.

6. Limitaciones y mejoras futuras

Qué cambiarías con más tiempo (cachear alturas, claves compuestas, otra estructura) y qué costo tendría.

Criterio de calidad

Un compañero que no vio el código debe poder entender por qué el árbol era la herramienta correcta.