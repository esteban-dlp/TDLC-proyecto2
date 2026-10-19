import argparse
from pathlib import Path

from gramatica import convertir_cnf, leer_gramatica, texto_gramatica


def principal():
    analizador = argparse.ArgumentParser(description="Convierte una gramatica a CNF")
    analizador.add_argument("archivo", help="ruta del archivo de gramatica")
    analizador.add_argument("--salida", help="archivo donde guardar la gramatica en CNF")
    args = analizador.parse_args()
    try:
        inicial, reglas = leer_gramatica(args.archivo)
        print("Gramatica original")
        print(texto_gramatica(inicial, reglas))
        inicial, reglas, pasos = convertir_cnf(inicial, reglas)
        for titulo, simbolo, estado in pasos:
            print(f"\n{titulo}")
            print(texto_gramatica(simbolo, estado))
        if args.salida:
            Path(args.salida).write_text(texto_gramatica(inicial, reglas) + "\n", encoding="utf-8")
            print(f"\nGramatica guardada en {args.salida}")
    except (OSError, ValueError) as error:
        analizador.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    principal()
