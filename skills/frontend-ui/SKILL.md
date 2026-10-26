Reglas para construir un frontend HTML funcional y bonito conectado al código Python real, apoyándose en las herramientas de diseño del modelo de IA.

Frontend en HTML
0. Usa las herramientas de interfaz del modelo

Antes de escribir una línea de HTML, carga y aplica las capacidades de diseño que ofrezca tu entorno: la skill frontend-design (si existe), los visualizadores o componentes de interfaz integrados y cualquier guía de diseño disponible. El resultado final siempre se guarda como archivos reales del proyecto (web/index.html), no se queda dentro de una vista previa del chat.

1. Plan de diseño (corto, antes de programar)

Escribe en 5 a 10 líneas: paleta de 4 a 6 colores con nombre, tipografías y su rol, esquema de distribución y qué será el elemento memorable (una sola cosa que haga única a la interfaz). Revísalo contra el tema del caso de estudio: la identidad visual sale del tema, no de una plantilla. Evita los clichés típicos de páginas generadas (fondo crema con serif y terracota, negro con verde ácido, tarjetas idénticas con sombra gris).

2. Requisitos funcionales
Un solo archivo web/index.html con HTML, CSS y JS propios, sin CDN ni compilación, para que funcione sin internet.
Cada control llama a la API real (/api/...) servida por Python. Cero resultados quemados en el HTML.
Visualización del árbol (colapsable o dibujada) que se actualiza al insertar o eliminar.
Al seleccionar un nodo: su camino a la raíz, profundidad, altura y datos propios.
Una pestaña o panel por función del caso de estudio (búsqueda, rango, ancestro, recorridos, edición, estadísticas).
Errores del servidor mostrados con un mensaje que diga qué falló y cómo corregirlo.
Confirmación antes de acciones destructivas (eliminar ramas).
Estado vacío con una invitación a actuar, no una pantalla en blanco.
3. Calidad mínima
Responsive hasta pantallas de celular.
Foco de teclado visible, contraste suficiente, prefers-reduced-motion respetado, modo oscuro opcional.
Movimiento solo donde responda a una acción de la persona.
Textos en español, en minúscula tipo oración; los botones dicen lo que hacen ("Agregar especie", no "Enviar").
4. Verificación

Prueba cada endpoint con peticiones reales y revisa la interfaz en el navegador. Si no puedes abrir un navegador, dilo explícitamente en vez de afirmar que se ve bien.