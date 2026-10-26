# Mediciones reales

## Crecimiento del ├írbol n-ario

| n | altura bushy (b=4) | altura cadena | altura m├¡nima te├│rica | ancho m├íximo bushy | construcci├│n bushy (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 4 | 99 | 4 | 64 | 0.77 |
| 1000 | 5 | 999 | 5 | 659 | 4.26 |
| 10000 | 7 | 9999 | 7 | 4539 | 81.21 |

La cadena de 10 000 nodos se construy├│ en 992.99 ms; su altura es lineal, no logar├¡tmica.

## AVL contra BST simple con altitudes ordenadas

| n | altura BST | altura AVL | rotaciones AVL | BST (ms) | AVL (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 100 | 100 | 7 | 93 | 0.84 | 2.02 |
| 1000 | 1000 | 10 | 990 | 61.79 | 17.37 |
| 10000 | 10000 | 14 | 9986 | 6474.46 | 481.15 |

## Consulta por rango contra recorrido lineal

Dos reg├¡menes: rangos largos como los de las especies reales y rangos cortos que producen una respuesta selectiva.

| r├®gimen | ancho (m) | n | consultas | AVL promedio (┬Ás) | lineal promedio (┬Ás) | aceleraci├│n | resultados promedio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| rangos largos (100-1500 m) | 200 | 10000 | 300 | 2322.9 | 1902.3 | 0.8├ù | 1849.2 |
| rangos largos (100-1500 m) | 500 | 10000 | 300 | 3144.9 | 1594.5 | 0.5├ù | 2379.6 |
| rangos largos (100-1500 m) | 1000 | 10000 | 300 | 4502.6 | 2191.2 | 0.5├ù | 3324.5 |
| rangos cortos (20-80 m) | 100 | 10000 | 300 | 406.0 | 3125.3 | 7.7├ù | 300.1 |
| rangos cortos (20-80 m) | 200 | 10000 | 300 | 793.5 | 2557.0 | 3.2├ù | 500.1 |
| rangos cortos (20-80 m) | 500 | 10000 | 300 | 1300.2 | 2869.4 | 2.2├ù | 1096.9 |

## Autocompletado contra filtro lineal

| nombres | consultas | trie promedio (┬Ás) | lista promedio (┬Ás) | aceleraci├│n | construcci├│n (ms) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10000 | 1000 | 192.4 | 3270.2 | 17.0├ù | 165.76 |

