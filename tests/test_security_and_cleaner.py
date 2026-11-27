"""Pruebas unitarias para hashing de contraseñas, sanitización del scraper y utilidades de parseo."""

import unittest

from backend.services.scraper.cleaner import (
    sanitizar_datos_estudiante,
    sanitizar_inscripciones,
    sanitizar_notas,
    sanitizar_parciales,
)
from backend.services.scraper.insweb_scraper import INSWEBScraper
from backend.services.security import hash_password, verify_password


class TestSecurityHashing(unittest.TestCase):
    def test_hash_and_verify_valid_password(self) -> None:
        hashed = hash_password("clave_segura_2026")
        self.assertIn("$", hashed)
        self.assertTrue(verify_password("clave_segura_2026", hashed))
        self.assertFalse(verify_password("clave_incorrecta", hashed))

    def test_hash_uses_random_salt(self) -> None:
        h1 = hash_password("misma_clave")
        h2 = hash_password("misma_clave")
        self.assertNotEqual(h1, h2)
        self.assertTrue(verify_password("misma_clave", h1))
        self.assertTrue(verify_password("misma_clave", h2))

    def test_verify_malformed_hash_returns_false(self) -> None:
        self.assertFalse(verify_password("abc", "sin_separador"))
        self.assertFalse(verify_password("abc", ""))


class TestScraperCleaner(unittest.TestCase):
    def test_sanitizar_parciales_preliminar_fallback_and_official_priority(self) -> None:
        ficha_raw = {
            "2026_C1": [
                {
                    "asignatura": "ELECTRONICA 1",
                    "evaluaciones": [
                        {"tipo_examen": "Primer Parcial", "puntaje": 21.0, "puntaje_preliminar": "99"},
                        {"tipo_examen": "Segundo Parcial", "puntaje": None, "puntaje_preliminar": "32"},
                        {"tipo_examen": "Trabajo Práctico / Taller / Otros", "puntaje": None, "puntaje_preliminar": "A"},
                        {"tipo_examen": "Laboratorio", "puntaje": None, "puntaje_preliminar": "97,5"},
                        {"tipo_examen": "Proyecto", "puntaje": 0.0, "puntaje_preliminar": "80"},
                    ],
                },
                {
                    "asignatura": "SEÑALES Y SISTEMAS",
                    "evaluaciones": [
                        {"tipo_examen": "Primer Parcial", "puntaje": None, "puntaje_preliminar": "58"},
                    ],
                },
            ]
        }

        limpios = sanitizar_parciales(ficha_raw)
        por_clave = {(item["asignatura"], item["tipo_examen"]): item for item in limpios}

        # Oficial tiene prioridad sobre preliminar (incluso cuando oficial es 0.0)
        self.assertEqual(por_clave[("ELECTRONICA 1", "Primer Parcial")]["puntaje"], 21.0)
        self.assertEqual(por_clave[("ELECTRONICA 1", "Proyecto")]["puntaje"], 0.0)

        # Fallback a preliminar numérico cuando oficial es None
        self.assertEqual(por_clave[("ELECTRONICA 1", "Segundo Parcial")]["puntaje"], 32.0)
        self.assertEqual(por_clave[("ELECTRONICA 1", "Laboratorio")]["puntaje"], 97.5)
        self.assertEqual(por_clave[("SEÑALES Y SISTEMAS", "Primer Parcial")]["puntaje"], 58.0)

        # Marcadores no numéricos como Ausente ("A") quedan en None
        self.assertIsNone(por_clave[("ELECTRONICA 1", "Trabajo Práctico / Taller / Otros")]["puntaje"])
        self.assertEqual(por_clave[("SEÑALES Y SISTEMAS", "Primer Parcial")]["periodo"], "2026_C1")

    def test_sanitizar_inscripciones_and_notas(self) -> None:
        raw = {
            "inscripciones": {
                "INGENIERIA MECATRONICA": [
                    {"nombre": "  ESTATICA  ", "semestre": "3", "estado": "NO"},
                ]
            },
            "notas": [
                {"asignatura": "CALCULO 1", "nota": "4", "nota_literal": "Cuatro", "fecha": "10/07/2024"},
                {"asignatura": "FISICA 1", "nota": 1, "nota_literal": "Uno", "fecha": "12/07/2024"},
            ],
            "ficha": {},
        }

        limpio = sanitizar_datos_estudiante(raw)
        self.assertEqual(len(limpio["inscripciones"]), 1)
        self.assertEqual(limpio["inscripciones"][0]["asignatura"], "ESTATICA")
        self.assertEqual(len(limpio["notas"]), 2)
        self.assertTrue(limpio["notas"][0]["aprobado"])
        self.assertFalse(limpio["notas"][1]["aprobado"])

        # Lista directa en sanitizar_inscripciones
        ins_list = sanitizar_inscripciones([{"carrera": "MCT", "asignatura": "DINAMICA", "semestre": "4", "estado": "SI"}])
        self.assertEqual(ins_list[0]["asignatura"], "DINAMICA")
        self.assertEqual(sanitizar_notas([]), [])


class TestInswebScraperHelpers(unittest.TestCase):
    def test_parse_float_or_none(self) -> None:
        self.assertEqual(INSWEBScraper._parse_float_or_none("67,5"), 67.5)
        self.assertEqual(INSWEBScraper._parse_float_or_none(0), 0.0)
        self.assertIsNone(INSWEBScraper._parse_float_or_none("A"))
        self.assertIsNone(INSWEBScraper._parse_float_or_none(""))
        self.assertIsNone(INSWEBScraper._parse_float_or_none(True))

    def test_parse_kv_metric(self) -> None:
        blob = "CUMPLEPROCESO=S,CUMPLEUREQC=1,SUMAPROCESO=67.00,SUMATOTAL=67.00,DERECHO=S,SUMARECU=73.0,"
        self.assertEqual(INSWEBScraper._parse_kv_metric(blob, "SUMATOTAL"), "67.00")
        self.assertEqual(INSWEBScraper._parse_kv_metric(blob, "DERECHO"), "S")
        self.assertEqual(INSWEBScraper._parse_kv_metric(blob, "SUMARECU"), "73.0")
        self.assertIsNone(INSWEBScraper._parse_kv_metric(blob, "INEXISTENTE"))
        self.assertIsNone(INSWEBScraper._parse_kv_metric(None, "DERECHO"))


if __name__ == "__main__":
    unittest.main()
