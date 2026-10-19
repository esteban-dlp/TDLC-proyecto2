# Reporte del proyecto 2

## Proposito

Implementar la simplificacion de una gramatica libre de contexto, su conversion
a la forma normal de Chomsky y el algoritmo CYK para decidir si una frase
pertenece a su lenguaje. Ademas de la respuesta se muestran el tiempo de
validacion y un arbol de analisis para las entradas aceptadas.

Se usa la gramatica de ingles del enunciado y se incluyen los dos archivos
proporcionados para expresiones. Los terminales en ingles se conservan porque
son parte del lenguaje solicitado. Los mensajes y nombres propios del programa
estan en espanol. Solo se usa la biblioteca estandar de Python.

## Diseno de la aplicacion

El flujo es el siguiente:

```text
archivo de gramatica
        |
        v
lector de producciones
        |
        v
simplificacion y conversion a CNF
        |
        v
frase -> separacion de terminales -> CYK -> respuesta y tiempo
                                     |
                                     v
                              tabla y arbol
```

`gramatica.py` representa las reglas con un diccionario. Cada variable tiene
un conjunto de tuplas; cada tupla es el cuerpo de una produccion y la tupla
vacia representa epsilon. Los conjuntos evitan reglas repetidas.
El primer lado izquierdo del archivo es el simbolo inicial.

`convertir.py` permite usar el conversor por separado. `cyk.py` realiza la
programacion dinamica y presenta la tabla y el arbol. `principal.py` une
la lectura, la conversion, la entrada de una frase y la medicion de tiempos.
`pruebas/prueba_proyecto.py` verifica el comportamiento sin paquetes externos.

## Simplificacion y CNF

1. Si el simbolo inicial aparece en un cuerpo, se crea uno nuevo con una regla
   hacia el inicial anterior. Esto evita que el inicial aparezca en otros
   cuerpos y permite conservar epsilon correctamente.
2. Se calculan las variables anulables hasta que el conjunto deje de cambiar.
   Para cada cuerpo se forman las variantes que omiten posiciones anulables.
   Se eliminan las reglas vacias, excepto la del inicial cuando corresponde.
3. Para cada variable se recorren todas las variables accesibles por reglas
   unitarias. Se copian sus producciones no unitarias y se quitan las unitarias.
   Un conjunto de visitados evita ciclos infinitos.
4. Se encuentran las variables que generan alguna cadena de terminales. Se
   eliminan las otras y despues se conservan solamente las alcanzables desde
   el inicial. Si el lenguaje es vacio, el inicial queda sin producciones.
5. Los terminales en cuerpos de longitud dos o mayor se reemplazan por
   variables auxiliares. Cada terminal comparte su variable auxiliar.
6. Cada cuerpo de longitud mayor que dos se divide en reglas binarias.
   Finalmente se comprueba la forma CNF obtenida.

Las reglas finales son `A -> B C` o `A -> terminal`; tambien puede existir
`inicial -> epsilon`. Los nombres auxiliares se revisan contra todos los
simbolos originales para evitar colisiones. Cada paso conserva su propio
estado para mostrar el proceso de conversion.

La conversion no necesita eliminar recursion izquierda: CYK trabaja con
intervalos de terminales y puede usar reglas recursivas en CNF.
La gramatica de ingles ya cumple CNF, por lo que conserva sus producciones.
El archivo `1-cnf.txt` usa reglas binarias y terminales individuales, pero
su inicial `E` tambien aparece en cuerpos. Por eso se agrega un inicial
nuevo para cumplir la convencion estricta usada por el programa.
Los nombres auxiliares y el numero de reglas pueden diferir de los del PDF
sin alterar el lenguaje generado.

## Programacion dinamica y CYK

La idea de llenar la tabla por longitudes crecientes y usar reglas binarias
se contrasto con las [notas de CYK de Yale](https://zoo.cs.yale.edu/classes/cs470/2014--15-fall/14f-lecnotes/lec31.html).
La reutilizacion de subproblemas se consulto en el [material de OpenDSA de Virginia Tech](https://opendsa.cs.vt.edu/ODSA/Books/vt/0000/spring-2020/TR_1000/html/CYKParsing.html).

La programacion dinamica resuelve subproblemas y guarda sus resultados para
usarlos en problemas mas grandes. Aqui el subproblema es determinar que
variables generan el intervalo de palabras que va desde `i` hasta `j`.

La tabla tiene una celda por intervalo. Cada celda guarda un diccionario
con las variables que generan ese fragmento y un arbol por variable.
Para los intervalos de una palabra se buscan reglas `A -> palabra`.
Despues se consideran longitudes de dos hasta la longitud completa.

Para cada intervalo se prueban todos sus cortes. Si una parte izquierda
es generada por `B`, una derecha por `C` y existe `A -> B C`, se agrega
`A` a la celda. Se guarda tambien el nodo con ambos hijos. Al terminar,
la frase pertenece al lenguaje si el simbolo inicial esta en la celda
que cubre la frase completa. La cadena vacia se revisa por separado.

El arbol impreso corresponde a la gramatica convertida a CNF. Puede incluir
variables auxiliares; no se reconstruyen pasos eliminados de la gramatica
original. Las hojas, leidas de izquierda a derecha, forman la entrada.
Cuando hay ambiguedad se muestra un solo arbol por variable e intervalo.
Esto basta para decidir pertenencia, pero no enumera todas las derivaciones.
Las hojas se verifican tambien en las pruebas.

Para `n` palabras y una gramatica fija, el tiempo de CYK es O(n^3) y la
memoria es O(n^2). Si tambien se cuenta el tamano de la gramatica, esta
implementacion recorre parejas de variables en cada corte y busca sus padres
en un indice; una cota es O(n^3 (v^2 + p)), con `v` variables y `p` reglas.
La tabla guarda como maximo O(n^2 v) nodos con referencias a sus hijos.
La conversion no forma parte de esa cota: eliminar epsilon puede crear
hasta 2^k variantes para un cuerpo con `k` posiciones anulables.

## Ejemplos ejecutados

Los tiempos siguientes se midieron en segundos durante una ejecucion local.
Cambian segun el equipo y la carga. Incluyen la preparacion de indices y la
construccion de la tabla y del arbol de CYK; excluyen entrada, conversion e
impresion. El programa mide la conversion por separado.

| Gramatica | Entrada | Resultado | Tiempo CYK en segundos |
| --- | --- | --- | --- |
| ingles.txt | She eats a cake with a fork | SÍ | 0.000031875 |
| ingles.txt | The cat drinks the beer | SÍ | 0.000017459 |
| ingles.txt | he cooks | SÍ | 0.000009875 |
| ingles.txt | the cake drinks a cat | SÍ | 0.000014208 |
| ingles.txt | she a cake eats | NO | 0.000011792 |
| ingles.txt | he eats cake | NO | 0.000010125 |
| ingles.txt | they eat a cake | NO | 0.000010208 |
| ingles.txt | cadena vacia | NO | 0.000003792 |
| 1.txt | (id*id)+id | SÍ | 0.000036542 |
| 1-cnf.txt | (id*id)+id | SÍ | 0.000029084 |
| 1.txt | id+ | NO | 0.000013250 |

`the cake drinks a cat` es aceptada porque la estructura cumple las reglas,
aunque su significado resulte extrano. El programa comprueba sintaxis.
`he eats cake` se rechaza porque el objeto requiere `Det N`.

Para `She eats a cake with a fork`, la gramatica produce este arbol:

```text
S
  NP
    she
  VP
    VP
      V
        eats
      NP
        Det
          a
        N
          cake
    PP
      P
        with
      NP
        Det
          a
        N
          fork
```

## Pruebas automatizadas

Se ejecutaron los siete metodos de prueba sin fallos. Se revisan catorce
entradas de ingles y diez expresiones con cada uno de los dos archivos.
Para nueve gramaticas adicionales se comparan todas las 121 cadenas del
alfabeto `{a, b, c}` de longitud cero a cuatro contra un calculo independiente
del lenguaje por punto fijo. En total son 1089 comparaciones de pertenencia
para verificar la conversion, ademas de los casos de ingles y expresiones.

Esas nueve gramaticas incluyen epsilon inicial, variables anulables repetidas,
ciclos unitarios, recursion del inicial, simbolos no generadores, variables
inalcanzables, reglas de cuatro variables y nombres auxiliares preexistentes.
Tambien se prueban archivos invalidos, la validacion previa de CNF y que la
conversion no modifique las reglas originales ni los estados anteriores.
La comparacion acotada aporta evidencia de correccion para esos casos;
no constituye una prueba formal para todas las gramaticas posibles.

## Discusion y recomendaciones

Una dificultad de la conversion es eliminar epsilon cuando el inicial tambien
aparece dentro de una produccion. Se resolvio agregando un inicial nuevo antes
de eliminar reglas. Otra es quitar reglas unitarias con ciclos; recorrerlas
con visitados permite copiar sus producciones sin quedar en un ciclo.

En las expresiones, `id` debe tratarse como un terminal completo y los
operadores deben separarse incluso sin espacios. Se usa un separador de
palabras y signos. En ingles se aceptan mayusculas mediante normalizacion,
pero no se quita puntuacion que no forme parte de la gramatica.

La gramatica usa espacios entre simbolos y define variables por sus lados
izquierdos. Conviene revisar nombres mal escritos porque un simbolo sin
produccion propia se considera terminal. El formato no permite que un mismo
nombre represente un terminal y una variable ni usar `e` como terminal literal.
Tampoco se implementa un analizador lexico configurable para terminales de
varias palabras o signos compuestos.

La tabla y los arboles se imprimen en texto para mantener pocas dependencias.
Con entradas largas la salida puede ser grande; la tabla y los pasos son
opcionales. Para gramaticas grandes, la eliminacion de epsilon y la cantidad
de nodos pueden consumir mucha memoria. Como mejora futura podria guardarse
la procedencia de cada regla para reconstruir el arbol de la gramatica original
y ofrecer todas las derivaciones cuando haya ambiguedad.

## Material consultado

- `referencias/Proyecto No 2.pdf`: requisitos, gramatica de ingles y criterios.
- `referencias/Ejemplo Proyecto 2.pdf`: simplificacion y conversion del ejemplo.
- `gramaticas/1.txt` y `gramaticas/1-cnf.txt`: gramaticas entregadas con el ejemplo.
