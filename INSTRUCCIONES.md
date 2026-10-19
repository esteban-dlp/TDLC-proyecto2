# Uso del proyecto completo

Se necesita Python 3.10 o posterior. No hay dependencias externas.
Abra una terminal dentro de Proyecto 2.

## Frases en ingles

```sh
python3 principal.py
python3 principal.py "She eats a cake with a fork" --tabla --pasos
python3 principal.py "The cat drinks the beer"
python3 principal.py "she a cake eats"
```

El primer comando pregunta la frase. Los otros reciben la frase como argumento.
La gramatica de ingles es la predeterminada y se busca junto al programa,
aunque este se ejecute desde otra carpeta. Para esta gramatica se pasa la
entrada a minusculas. No se elimina la puntuacion: un punto final se rechaza
porque no esta definido en la gramatica del enunciado.

La salida contiene la gramatica en CNF, SÍ o NO, el tiempo de conversion,
el tiempo de CYK y un arbol si la frase es aceptada. `--tabla` muestra los
intervalos de la tabla y `--pasos` muestra las etapas de conversion.
Los tiempos usan segundos y se miden sin incluir impresiones ni entrada
por teclado. La medicion de CYK incluye revisar CNF, preparar indices,
construir la tabla y guardar el arbol; la conversion se mide aparte.

## Expresiones del ejemplo

```sh
python3 principal.py "(id*id)+id" --gramatica gramaticas/1.txt --pasos --tabla
python3 principal.py "(id*id)+id" --gramatica gramaticas/1-cnf.txt --tabla
python3 principal.py "id+" --gramatica gramaticas/1.txt
```

Ambos archivos pasan por el conversor antes de ejecutar CYK.
`id` es un solo terminal; los operadores y parentesis se separan aunque
no tengan espacios. Las palabras se mantienen completas: `sheeats`
no se separa artificialmente en `she eats`.

Con otras gramaticas se respetan mayusculas y minusculas. Puede usar
`--minusculas` si quiere normalizar la entrada. Cada terminal debe ser
una palabra completa o un signo individual compatible con el separador
`\w+|[^\w\s]`. No se admiten terminales de varias palabras ni signos
compuestos como un unico terminal. Las rutas relativas de `--gramatica`
se interpretan desde la carpeta actual de la terminal.

## Cadena vacia

```sh
python3 principal.py "" --gramatica gramaticas/1.txt
```

La frase vacia se escribe con comillas vacias, no con `e`. Se acepta
solamente si el simbolo inicial de la gramatica puede generar epsilon.
En el archivo de gramatica se escribe `e`, `epsilon` o `ε` para epsilon.

## Pruebas

```sh
python3 -m unittest discover -s pruebas -p 'prueba_*.py' -v
```

Son siete pruebas automatizadas con varios casos cada una. Incluyen ingles,
expresiones, formato invalido, validacion de CNF, copia independiente de pasos
y comparacion del lenguaje original con el convertido para cadenas cortas.
El reporte explica los resultados y las limitaciones.

## Division de la entrega

La carpeta ya contiene las dos partes terminadas. El primer comando de
entrega debe agregar solamente estos archivos:

- `.gitignore`
- `README.md`
- `gramatica.py`
- `convertir.py`
- `gramaticas/`
- `referencias/`

Ese conjunto permite leer y convertir las gramaticas de forma independiente.
La segunda tanda agrega estos archivos:

- `cyk.py`
- `principal.py`
- `pruebas/`
- `INSTRUCCIONES.md`
- `REPORTE.md`

Asi se obtienen dos avances funcionales de tamano parecido sin tener que
reemplazar versiones de un archivo. Antes del primer commit no use
`git add .`, porque eso incluiria tambien la segunda parte.
Los comandos de entrega estan en el chat. No se ejecuto Git para preparar
este proyecto y no se creo un repositorio ni se vinculo un remoto.
