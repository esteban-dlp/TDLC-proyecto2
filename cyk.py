import re

from gramatica import es_cnf


def separar_frase(frase):
    return re.findall(r"\w+|[^\w\s]", frase, flags=re.UNICODE)


def analizar(palabras, inicial, reglas):
    if not es_cnf(inicial, reglas):
        raise ValueError("CYK necesita una gramatica en CNF")
    n = len(palabras)
    if n == 0:
        arbol = (inicial, "ε") if () in reglas[inicial] else None
        return arbol is not None, [], arbol

    terminales = {}
    parejas = {}
    for izq in sorted(reglas):
        for der in sorted(reglas[izq]):
            if len(der) == 1:
                terminales.setdefault(der[0], []).append(izq)
            elif len(der) == 2:
                parejas.setdefault(der, []).append(izq)

    # cada celda guarda un arbol por variable
    tabla = [[{} for _ in range(n)] for _ in range(n)]
    for i, palabra in enumerate(palabras):
        for izq in terminales.get(palabra, []):
            tabla[i][i][izq] = (izq, palabra)

    # se resuelven primero los intervalos mas cortos
    for largo in range(2, n + 1):
        for i in range(n - largo + 1):
            j = i + largo - 1
            for corte in range(i, j):
                for a, arbol_a in tabla[i][corte].items():
                    for b, arbol_b in tabla[corte + 1][j].items():
                        for izq in parejas.get((a, b), []):
                            if izq not in tabla[i][j]:
                                tabla[i][j][izq] = (izq, arbol_a, arbol_b)
    arbol = tabla[0][n - 1].get(inicial)
    return arbol is not None, tabla, arbol


def texto_tabla(palabras, tabla):
    if not palabras:
        return "La cadena vacia no necesita tabla"
    lineas = []
    for largo in range(1, len(palabras) + 1):
        lineas.append(f"Longitud {largo}")
        for i in range(len(palabras) - largo + 1):
            j = i + largo - 1
            contenido = ", ".join(sorted(tabla[i][j])) or "vacio"
            tramo = " ".join(palabras[i:j + 1])
            lineas.append(f"  [{i + 1}, {j + 1}] {tramo}: {contenido}")
    return "\n".join(lineas)


def texto_arbol(arbol, nivel=0):
    if arbol is None:
        return "No hay arbol porque la frase no pertenece al lenguaje"
    lineas = ["  " * nivel + arbol[0]]
    for hijo in arbol[1:]:
        if isinstance(hijo, tuple):
            lineas.append(texto_arbol(hijo, nivel + 1))
        else:
            lineas.append("  " * (nivel + 1) + hijo)
    return "\n".join(lineas)
