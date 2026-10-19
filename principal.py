import argparse
from pathlib import Path
from time import perf_counter

from cyk import analizar, separar_frase, texto_arbol, texto_tabla
from gramatica import convertir_cnf, leer_gramatica, texto_gramatica


def principal():
    carpeta = Path(__file__).resolve().parent
    ingles = carpeta / "gramaticas" / "ingles.txt"
    analizador = argparse.ArgumentParser(description="Conversion a CNF y validacion con CYK")
    analizador.add_argument("frase", nargs="?", help="frase entre comillas o vacia para preguntar")
    analizador.add_argument("--gramatica", default=str(ingles), help="archivo de gramatica")
    analizador.add_argument("--pasos", action="store_true", help="muestra toda la conversion")
    analizador.add_argument("--tabla", action="store_true", help="muestra la tabla de CYK")
    analizador.add_argument("--minusculas", action="store_true", help="convierte la entrada a minusculas")
    args = analizador.parse_args()
    try:
        inicial, reglas = leer_gramatica(args.gramatica)
        inicio = perf_counter()
        inicial, reglas, pasos = convertir_cnf(inicial, reglas)
        tiempo_cnf = perf_counter() - inicio
        frase = args.frase if args.frase is not None else input("Ingrese la frase o expresion: ")
        if args.minusculas or Path(args.gramatica).resolve() == ingles:
            frase = frase.lower()
        palabras = separar_frase(frase)

        print("Gramatica en CNF")
        print(texto_gramatica(inicial, reglas))
        if args.pasos:
            for titulo, simbolo, estado in pasos:
                print(f"\n{titulo}")
                print(texto_gramatica(simbolo, estado))

        inicio = perf_counter()
        pertenece, tabla, arbol = analizar(palabras, inicial, reglas)
        tiempo_cyk = perf_counter() - inicio
        print("\nResultado:", "SÍ" if pertenece else "NO")
        print(f"Tiempo de conversion a CNF: {tiempo_cnf:.9f} segundos")
        print(f"Tiempo de validacion CYK: {tiempo_cyk:.9f} segundos")
        if args.tabla:
            print("\nTabla de CYK")
            print(texto_tabla(palabras, tabla))
        print("\nArbol de analisis de la gramatica en CNF")
        print(texto_arbol(arbol))
    except (OSError, ValueError, EOFError, KeyboardInterrupt) as error:
        analizador.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    principal()
