Cómo elegir y justificar un caso de estudio poco común donde los árboles sean esenciales y permitan varias funciones distintas.

Elegir el caso de estudio
Objetivo

Escoger un problema real y poco visto donde el árbol sea la estructura que hace posible las funciones, no un adorno. Tú (el agente) eliges; el estudiante confirma.

Casos demasiado comunes: evita

Sistema de archivos y carpetas, árbol genealógico simple, organigrama, calculadora de expresiones, BST de números sueltos, "adivina el animal", autocompletado como única función, compresión de Huffman sola.

Criterios obligatorios
Árbol esencial: si lo reemplazas por una lista o un diccionario, al menos dos funciones se vuelven más lentas o más torpes. Debes poder explicar por qué.
Mínimo 5 funciones distintas apoyadas en el árbol, con al menos:
una de inserción/eliminación que mantenga invariantes,
una consulta estructural (ancestro común, camino, profundidad, altura, subárbol),
una consulta por rango o prefijo,
recorridos con propósito real (no solo imprimir),
una estadística de la estructura (altura, balance, ancho por nivel).
Datos reales o verosímiles que el estudiante pueda reconocer y explicar (mejor si son de su región, Pasto/Nariño).
Alcance razonable: se termina en días, no semanas.
Se ve bien en pantalla: el árbol o sus resultados deben poder mostrarse visualmente en HTML.
Combinar árboles es válido (y suma al análisis)

Un buen caso puede usar varios: por ejemplo un árbol n-ario para una jerarquía, un AVL o árbol de intervalos para consultas ordenadas y un trie para búsqueda. Si combinas, define quién mantiene todo sincronizado (una clase fachada).

Semillas de ideas (inspiración; no estás obligado a usarlas)
Taxonomía de biodiversidad con índice por altitud y búsqueda por prefijo.
Agenda de reservas con árbol de intervalos para detectar choques de horario.
Control de versiones de documentos con árbol de Merkle para detectar qué cambió.
Editor de texto con rope (árbol de cadenas) para insertar y borrar en textos largos.
Mapa de zonas con quadtree para buscar puntos de interés cercanos.
Inventario de bodega con segment tree para consultas de sumas y mínimos por rango.
Entregable de esta fase: docs/CASE_STUDY.md

Debe contener:

Tres candidatos con una línea cada uno y sus pros y contras.
El elegido y por qué (cumple cada criterio de arriba, uno por uno).
Lista de funciones con la estructura exacta que usa cada una y su complejidad esperada.
Qué estructura alternativa se descartó para cada función y por qué.
Datos de ejemplo que se usarán.

Después de escribirlo, detente y pide confirmación.