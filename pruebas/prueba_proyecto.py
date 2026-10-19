import itertools
from pathlib import Path
import tempfile
import unittest

from cyk import analizar, separar_frase
from gramatica import convertir_cnf, es_cnf, leer_gramatica


CARPETA = Path(__file__).resolve().parents[1]


def desde_texto(texto):
    with tempfile.TemporaryDirectory() as carpeta:
        ruta = Path(carpeta) / "gramatica.txt"
        ruta.write_text(texto, encoding="utf-8")
        return leer_gramatica(ruta)


def acepta(frase, inicial, reglas):
    return analizar(separar_frase(frase), inicial, reglas)[0]


def hojas(arbol):
    if len(arbol) == 2:
        return [] if arbol[1] == "ε" else [arbol[1]]
    return hojas(arbol[1]) + hojas(arbol[2])


def lenguaje_acotado(inicial, reglas, limite):
    # calcula palabras por punto fijo sin usar cnf ni cyk
    palabras = {s: set() for s in reglas}
    cambio = True
    while cambio:
        cambio = False
        for izq, opciones in reglas.items():
            for der in opciones:
                partes = [palabras[s] if s in reglas else {(s,)} for s in der]
                nuevas = set()
                for combinacion in itertools.product(*partes):
                    palabra = tuple(s for parte in combinacion for s in parte)
                    if len(palabra) <= limite:
                        nuevas.add(palabra)
                if not nuevas <= palabras[izq]:
                    palabras[izq].update(nuevas)
                    cambio = True
    return palabras[inicial]


class PruebasProyecto(unittest.TestCase):
    def test_ingles(self):
        inicial, reglas = leer_gramatica(CARPETA / "gramaticas/ingles.txt")
        inicial, reglas, _ = convertir_cnf(inicial, reglas)
        casos = {
            "she eats a cake with a fork": True,
            "the cat drinks the beer": True,
            "he cooks": True,
            "she cuts the meat with a knife": True,
            "the cake drinks a cat": True,
            "she eats a cake with a fork in the oven": True,
            "she eats a cake with a": False,
            "she a cake eats": False,
            "the dog": False,
            "he eats cake": False,
            "they eat a cake": False,
            "sheeats": False,
            "she eats a cake.": False,
            "": False,
        }
        for frase, esperado in casos.items():
            with self.subTest(frase=frase):
                ok, _, arbol = analizar(separar_frase(frase), inicial, reglas)
                self.assertEqual(ok, esperado)
                if ok:
                    self.assertEqual(hojas(arbol), separar_frase(frase))

    def test_expresiones(self):
        for archivo in ["1.txt", "1-cnf.txt"]:
            inicial, reglas = leer_gramatica(CARPETA / "gramaticas" / archivo)
            inicial, reglas, _ = convertir_cnf(inicial, reglas)
            for frase in ["id", "(id*id)+id", "id+id*id", "((id))"]:
                with self.subTest(archivo=archivo, frase=frase):
                    self.assertTrue(acepta(frase, inicial, reglas))
            for frase in ["", "id+", "*id", "(id", "id id", "()"]:
                with self.subTest(archivo=archivo, frase=frase):
                    self.assertFalse(acepta(frase, inicial, reglas))

    def test_equivalencia_general(self):
        textos = [
            "S -> A A B | e\nA -> a | e\nB -> b",
            "S -> A\nA -> B | a\nB -> A | b",
            "S -> a S b | e",
            "S -> A B | a\nA -> A\nB -> b\nC -> c",
            "S -> A\nA -> A",
            "S -> a S | a",
            "S -> A B C D\nA -> a\nB -> b\nC -> a\nD -> b",
            "S -> A A\nA -> e | a",
            "S -> a S | Aux_1\nAux_1 -> b",
        ]
        for texto in textos:
            with self.subTest(texto=texto):
                inicial, reglas = desde_texto(texto)
                esperado = lenguaje_acotado(inicial, reglas, 4)
                nuevo, cnf, _ = convertir_cnf(inicial, reglas)
                self.assertTrue(es_cnf(nuevo, cnf))
                for largo in range(5):
                    for palabra in itertools.product(["a", "b", "c"], repeat=largo):
                        ok, _, arbol = analizar(list(palabra), nuevo, cnf)
                        self.assertEqual(ok, palabra in esperado, palabra)
                        if ok:
                            self.assertEqual(hojas(arbol), list(palabra))

    def test_archivo_cnf(self):
        inicial, reglas = leer_gramatica(CARPETA / "gramaticas/1-cnf.txt")
        self.assertTrue(all(
            (len(der) == 1 and der[0] not in reglas)
            or (len(der) == 2 and all(s in reglas for s in der))
            for opciones in reglas.values() for der in opciones
        ))
        nuevo, cnf, _ = convertir_cnf(inicial, reglas)
        self.assertTrue(es_cnf(nuevo, cnf))
        self.assertTrue(acepta("(id*id)+id", nuevo, cnf))

    def test_rechaza_gramatica_sin_convertir(self):
        inicial, reglas = desde_texto("S -> A\nA -> a")
        with self.assertRaises(ValueError):
            analizar(["a"], inicial, reglas)

    def test_formato_invalido(self):
        for texto in ["", "S A", "S ->", "S -> a |", "S T -> a", "S -> e a", "e -> a"]:
            with self.subTest(texto=texto):
                with self.assertRaises(ValueError):
                    desde_texto(texto)

    def test_pasos_independientes(self):
        inicial, reglas = desde_texto("S -> a S b | e")
        original = {s: set(opciones) for s, opciones in reglas.items()}
        nuevo, cnf, pasos = convertir_cnf(inicial, reglas)
        self.assertEqual(reglas, original)
        self.assertIn(("a", "S", "b"), pasos[0][2]["S"])
        self.assertTrue(es_cnf(nuevo, cnf))


if __name__ == "__main__":
    unittest.main()
