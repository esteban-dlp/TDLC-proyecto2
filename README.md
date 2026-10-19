# Proyecto 2

Simplificacion de gramaticas y conversion a la forma normal de Chomsky.
Esta es la primera parte del proyecto. La segunda parte agrega el algoritmo
CYK y su documentacion en `INSTRUCCIONES.md` y `REPORTE.md`.

## Requisitos

Python 3.10 o posterior. No se instalan paquetes externos.
Los comandos se ejecutan desde esta carpeta.

## Conversion

```sh
python3 convertir.py gramaticas/1.txt
python3 convertir.py gramaticas/ingles.txt --salida ingles_cnf.txt
```

Se muestran los pasos de eliminacion de producciones vacias y unitarias,
simbolos inutiles, separacion de terminales y division de reglas largas.
Cuando el simbolo inicial aparece en algun cuerpo se agrega uno nuevo.
La cadena vacia se conserva solo en el simbolo inicial cuando corresponde.

## Formato

La primera variable del archivo es el simbolo inicial. Cada produccion usa
`->`, las alternativas usan `|` y los simbolos se separan con espacios.
Una variable es cualquier simbolo definido a la izquierda de una regla.
Los demas simbolos son terminales. Se reservan `e`, `epsilon` y `ε`
para representar la cadena vacia. No se escriben terminales entre comillas.
Se permiten lineas vacias y comentarios en lineas que comienzan con `#`.

```text
S -> A B | e
A -> a
B -> b
```

`gramaticas/ingles.txt` contiene la gramatica del enunciado.
`gramaticas/1.txt` y `gramaticas/1-cnf.txt` son los archivos proporcionados
para el ejemplo de expresiones. Los PDF originales estan en `referencias`.
Los nombres de variables auxiliares pueden ser diferentes a los del ejemplo
sin cambiar el lenguaje generado.
