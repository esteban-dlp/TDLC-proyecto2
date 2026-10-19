from pathlib import Path


def leer_gramatica(ruta):
    reglas = {}
    inicial = None
    texto = Path(ruta).read_text(encoding="utf-8-sig")
    for num, linea in enumerate(texto.splitlines(), 1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if linea.count("->") != 1:
            raise ValueError(f"Linea {num}: se esperaba una flecha ->")
        izq, der = linea.split("->")
        izq = izq.strip()
        if not izq or len(izq.split()) != 1 or izq in {"e", "epsilon", "ε"}:
            raise ValueError(f"Linea {num}: el lado izquierdo no es valido")
        if inicial is None:
            inicial = izq
        reglas.setdefault(izq, set())
        for opcion in der.split("|"):
            simbolos = tuple(opcion.split())
            if not simbolos:
                raise ValueError(f"Linea {num}: use e para una produccion vacia")
            if simbolos in {("e",), ("epsilon",), ("ε",)}:
                simbolos = ()
            elif any(s in {"e", "epsilon", "ε"} for s in simbolos):
                raise ValueError(f"Linea {num}: epsilon debe aparecer solo")
            reglas[izq].add(simbolos)
    if inicial is None:
        raise ValueError("El archivo no tiene producciones")
    return inicial, reglas


def texto_gramatica(inicial, reglas):
    orden = [inicial] + sorted(s for s in reglas if s != inicial)
    lineas = []
    for izq in orden:
        opciones = [" ".join(der) if der else "e" for der in sorted(reglas[izq])]
        if opciones:
            lineas.append(f"{izq} -> " + " | ".join(opciones))
    return "\n".join(lineas) if lineas else "El lenguaje es vacio"


def es_cnf(inicial, reglas):
    variables = set(reglas)
    for izq, opciones in reglas.items():
        for der in opciones:
            if not der:
                if izq != inicial:
                    return False
            elif len(der) == 1:
                if der[0] in variables:
                    return False
            elif len(der) == 2:
                if any(s not in variables for s in der):
                    return False
            else:
                return False
            if inicial in der:
                return False
    return True


def quitar_vacias(inicial, reglas):
    anulables = set()
    cambio = True
    while cambio:
        cambio = False
        for izq, opciones in reglas.items():
            if izq not in anulables and any(all(s in anulables for s in der) for der in opciones):
                anulables.add(izq)
                cambio = True
    nuevas = {izq: set() for izq in reglas}
    for izq, opciones in reglas.items():
        for der in opciones:
            variantes = {()}
            for s in der:
                siguientes = {v + (s,) for v in variantes}
                if s in anulables:
                    siguientes.update(variantes)
                variantes = siguientes
            nuevas[izq].update(v for v in variantes if v)
    if inicial in anulables:
        nuevas[inicial].add(())
    return nuevas


def quitar_unitarias(reglas):
    nuevas = {izq: set() for izq in reglas}
    for izq in reglas:
        vistos = {izq}
        pendientes = [izq]
        while pendientes:
            actual = pendientes.pop()
            for der in reglas[actual]:
                if len(der) == 1 and der[0] in reglas:
                    if der[0] not in vistos:
                        vistos.add(der[0])
                        pendientes.append(der[0])
                else:
                    nuevas[izq].add(der)
    return nuevas


def quitar_inutiles(inicial, reglas):
    generan = set()
    cambio = True
    while cambio:
        cambio = False
        for izq, opciones in reglas.items():
            if izq not in generan and any(
                all(s not in reglas or s in generan for s in der) for der in opciones
            ):
                generan.add(izq)
                cambio = True
    if inicial not in generan:
        return {inicial: set()}
    utiles = {
        izq: {der for der in opciones if all(s not in reglas or s in generan for s in der)}
        for izq, opciones in reglas.items() if izq in generan
    }
    alcanzados = {inicial}
    pendientes = [inicial]
    while pendientes:
        actual = pendientes.pop()
        for der in utiles[actual]:
            for s in der:
                if s in utiles and s not in alcanzados:
                    alcanzados.add(s)
                    pendientes.append(s)
    return {izq: opciones for izq, opciones in utiles.items() if izq in alcanzados}


def convertir_cnf(inicial, reglas):
    reglas = {izq: set(opciones) for izq, opciones in reglas.items()}
    usados = set(reglas)
    usados.update(s for opciones in reglas.values() for der in opciones for s in der)
    contador = 0

    def nuevo():
        nonlocal contador
        while True:
            contador += 1
            nombre = f"Aux_{contador}"
            if nombre not in usados:
                usados.add(nombre)
                return nombre

    pasos = []
    if any(inicial in der for opciones in reglas.values() for der in opciones):
        anterior = inicial
        inicial = nuevo()
        reglas[inicial] = {(anterior,)}
        pasos.append(("Nuevo simbolo inicial", inicial, reglas))

    reglas = quitar_vacias(inicial, reglas)
    pasos.append(("Sin producciones vacias salvo la inicial", inicial, reglas))
    reglas = quitar_unitarias(reglas)
    pasos.append(("Sin producciones unitarias", inicial, reglas))
    reglas = quitar_inutiles(inicial, reglas)
    pasos.append(("Sin simbolos inutiles", inicial, reglas))

    variables = set(reglas)
    nuevas = {izq: set() for izq in reglas}
    terminales = {}
    for izq, opciones in reglas.items():
        for der in sorted(opciones):
            cuerpo = []
            for s in der:
                if len(der) >= 2 and s not in variables:
                    if s not in terminales:
                        nombre = nuevo()
                        terminales[s] = nombre
                        nuevas[nombre] = {(s,)}
                    s = terminales[s]
                cuerpo.append(s)
            nuevas[izq].add(tuple(cuerpo))
    reglas = nuevas
    pasos.append(("Terminales separados", inicial, reglas))

    nuevas = {izq: set() for izq in reglas}
    for izq, opciones in reglas.items():
        for der in sorted(opciones):
            actual = izq
            resto = der
            while len(resto) > 2:
                nombre = nuevo()
                nuevas[actual].add((resto[0], nombre))
                nuevas[nombre] = set()
                actual = nombre
                resto = resto[1:]
            nuevas[actual].add(resto)
    reglas = nuevas
    pasos.append(("Producciones binarias en CNF", inicial, reglas))
    if not es_cnf(inicial, reglas):
        raise ValueError("No se pudo obtener una gramatica en CNF")
    return inicial, reglas, pasos
