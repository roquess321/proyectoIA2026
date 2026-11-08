import datetime
import json
import os
import re
import time
from typing import Any, Dict, List, Optional


class INSWEBScraper:
    """Scraper automatizado para la plataforma INSWEB de la FIUNA (UNA).

    Utiliza Playwright para navegar y extraer:
    1. Inscripciones y horarios actuales.
    2. Historial de notas finales.
    3. Ficha histórica de notas parciales por periodo.
    """

    ANHO_MINIMO = 2019

    def __init__(
        self,
        base_url: str = "https://insweb.ing.una.py/login",
    ):
        self.base_url = base_url
        self.headless = True

    def _asegurar_playwright(self):
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "La librería 'playwright' no está instalada en el entorno virtual. "
                "Para activarla, ejecuta: 'uv add playwright' y luego 'uv run playwright install chromium'."
            )

    def iniciar_sesion(self, page: Any, cedula: str, pin: str) -> bool:
        """Autenticación en el portal INSWEB."""
        print(f"🌐 [Scraper] Conectando a {self.base_url}...")
        page.goto(self.base_url)

        campo_ci = page.locator('input[type="text"]').first
        campo_ci.wait_for(state="visible", timeout=12000)
        campo_ci.fill(cedula)

        campo_pin = page.locator('input[type="password"]').first
        campo_pin.fill(pin)

        print("🚀 [Scraper] Enviando credenciales...")
        campo_pin.press("Enter")

        try:
            page.wait_for_url(lambda url: "login" not in url, timeout=12000)
            print(f"✅ [Scraper] Login exitoso. URL actual: {page.url}")
            return True
        except Exception:
            print("❌ [Scraper] Error de autenticación: Credenciales incorrectas o tiempo de espera excedido.")
            return False

    def extraer_inscripciones(self, page: Any) -> Dict[str, Any]:
        """Extrae las materias e horarios de la página principal."""
        print("🔍 [Scraper] [1/3] Extrayendo Inscripciones...")
        try:
            page.wait_for_selector("tbody > tr", state="visible", timeout=10000)
        except Exception:
            print("⚠️ [Scraper] No se encontraron filas de inscripciones.")
            return {}

        resultado: Dict[str, List[Dict[str, Any]]] = {}
        carrera_actual = "Carrera General"
        filas = page.locator("tbody > tr").all()

        for fila in filas:
            if fila.evaluate("el => el.closest('table.table-horarios') !== null"):
                continue

            if fila.locator("strong").count() > 0:
                carrera_actual = fila.locator("strong").first.inner_text().strip()
                if carrera_actual not in resultado:
                    resultado[carrera_actual] = []
                continue

            celdas = fila.locator("> td").all()
            if len(celdas) >= 4:
                materia_raw = celdas[1].inner_text().strip()
                coincidencia = re.match(r"^(.*?)\s*\((\d+)\)$", materia_raw)

                materia_info = {
                    "semestre": celdas[0].inner_text().strip(),
                    "codigo": coincidencia.group(2) if coincidencia else "N/A",
                    "nombre": coincidencia.group(1).strip() if coincidencia else materia_raw,
                    "estado": celdas[2].inner_text().strip(),
                    "horarios": [
                        td.inner_text().strip()
                        for td in celdas[3].locator("td").all()
                        if td.inner_text().strip()
                    ],
                }

                if carrera_actual not in resultado:
                    resultado[carrera_actual] = []
                resultado[carrera_actual].append(materia_info)

        return resultado

    def extraer_notas(self, page: Any) -> List[Dict[str, Any]]:
        """Extrae el historial de notas finales."""
        print("🔍 [Scraper] [2/3] Extrayendo Notas Finales...")
        try:
            menu_notas = (
                page.locator("a, button, mat-list-item")
                .filter(has_text=re.compile(r"^\s*Notas\s*$", re.IGNORECASE))
                .first
            )
            if menu_notas.count() == 0:
                menu_notas = page.get_by_text("Notas", exact=True)

            menu_notas.wait_for(state="visible", timeout=6000)
            menu_notas.click()

            opcion_notas_finales = page.get_by_text("Notas Finales", exact=True)
            opcion_notas_finales.wait_for(state="visible", timeout=6000)
            opcion_notas_finales.click()

            page.wait_for_selector("tbody > tr", state="visible", timeout=10000)
        except Exception as e:
            print(f"⚠️ [Scraper] No se pudo acceder a la tabla de notas: {e}")
            return []

        historial_notas = []
        filas = page.locator("tbody > tr").all()

        for fila in filas:
            celdas = fila.locator("> td").all()
            if len(celdas) >= 5:
                raw_nota = celdas[1].inner_text().strip()
                match_nota = re.search(r"^(\d+)\s*(?:\((.*?)\))?", raw_nota)

                if match_nota:
                    nota_num = int(match_nota.group(1))
                    nota_txt = match_nota.group(2) if match_nota.group(2) else ""
                else:
                    nota_num = raw_nota
                    nota_txt = ""

                historial_notas.append(
                    {
                        "asignatura": celdas[0].inner_text().strip(),
                        "nota": nota_num,
                        "nota_literal": nota_txt,
                        "fecha": celdas[2].inner_text().strip(),
                        "nro_acta": celdas[3].inner_text().strip(),
                        "tipo": celdas[4].inner_text().strip(),
                        "aprobado": isinstance(nota_num, int) and nota_num >= 2,
                    }
                )

        print(f"✅ [Scraper] {len(historial_notas)} notas finales recuperadas.")
        return historial_notas

    def extraer_notas_parciales(self, page: Any) -> Dict[str, Any]:
        """Extrae el desglose de evaluaciones parciales navegando hacia periodos anteriores."""
        print("🔍 [Scraper] [3/3] Extrayendo Notas Parciales...")
        try:
            menu_notas = (
                page.locator("a, button, mat-list-item")
                .filter(has_text=re.compile(r"^\s*Notas\s*$", re.IGNORECASE))
                .first
            )
            if menu_notas.count() == 0:
                menu_notas = page.get_by_text("Notas", exact=True)

            menu_notas.wait_for(state="visible", timeout=6000)
            menu_notas.click()

            opcion_parciales = page.get_by_text("Notas Parciales", exact=True)
            opcion_parciales.wait_for(state="visible", timeout=6000)
            opcion_parciales.click()

            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception as e:
            print(f"⚠️ [Scraper] No se pudo acceder a notas parciales: {e}")
            return {}

        try:
            input_anho = (
                page.locator("div.form-group")
                .filter(has_text=re.compile(r"^\s*Año\s*$", re.IGNORECASE))
                .locator("input")
                .first
            )
            input_convocatoria = (
                page.locator("div.form-group")
                .filter(has_text=re.compile(r"^\s*Convocatoria\s*$", re.IGNORECASE))
                .locator("input")
                .first
            )
            input_anho.wait_for(state="visible", timeout=5000)
            input_convocatoria.wait_for(state="visible", timeout=5000)
        except Exception:
            return {}

        anho_str, convocatoria_str = "", ""
        for _ in range(5):
            anho_str = input_anho.input_value().strip()
            convocatoria_str = input_convocatoria.input_value().strip()
            if anho_str and convocatoria_str:
                break
            time.sleep(1)

        anho_defecto = int(anho_str) if anho_str.isdigit() else datetime.datetime.now().year
        convocatoria_defecto = int(convocatoria_str) if convocatoria_str.isdigit() else 2

        # Iniciar obligatoriamente un semestre por arriba del que InsWeb muestra por defecto
        if convocatoria_defecto == 1:
            anho_inicio = anho_defecto
            convocatoria_inicio = 2
        else:
            anho_inicio = anho_defecto + 1
            convocatoria_inicio = 1

        print(
            f"🔄 [Scraper] Periodo por defecto en InsWeb: {anho_defecto}_C{convocatoria_defecto}. "
            f"Forzando inicio un ciclo superior: {anho_inicio}_C{convocatoria_inicio}..."
        )

        def cambiar_periodo(a: int, c: int) -> bool:
            try:
                input_anho.click()
                input_anho.fill(str(a))
                input_anho.dispatch_event("input")
                input_anho.dispatch_event("change")

                input_convocatoria.click()
                input_convocatoria.fill(str(c))
                input_convocatoria.dispatch_event("input")
                input_convocatoria.dispatch_event("change")
                input_convocatoria.press("Enter")
                input_convocatoria.press("Tab")

                try:
                    page.wait_for_load_state("networkidle", timeout=3000)
                except Exception:
                    pass
                time.sleep(1.8)
                return True
            except Exception as ex:
                print(f"⚠️ [Scraper] Error al cambiar a periodo {a}_C{c}: {ex}")
                return False

        # Forzar la carga en pantalla del ciclo superior antes de comenzar la extracción
        cambiar_periodo(anho_inicio, convocatoria_inicio)

        anho = anho_inicio
        convocatoria = convocatoria_inicio
        resultados: Dict[str, Any] = {}

        # Bucle descendente por periodos desde el ciclo forzado superior hasta ANHO_MINIMO
        while anho >= self.ANHO_MINIMO:
            clave_periodo = f"{anho}_C{convocatoria}"

            cards = page.locator("div.card").all()
            if cards:
                materias_periodo = []
                for card in cards:
                    if not card.is_visible() or card.locator("h4.title").count() == 0:
                        continue

                    raw_titulo = card.locator("h4.title").inner_text().strip()
                    match_titulo = re.match(r"^(.*?)\s*\((.*?)\)$", raw_titulo)
                    nombre_materia = match_titulo.group(1).strip() if match_titulo else raw_titulo
                    codigo_materia = match_titulo.group(2).strip() if match_titulo else "N/A"

                    evaluaciones = []
                    promedio_ponderado = None
                    promedio_recuperatorio = None
                    derecho = None

                    filas = card.locator("tbody > tr").all()
                    for fila in filas:
                        celdas = fila.locator("> td").all()
                        if len(celdas) == 3 and celdas[0].get_attribute("colspan") is None:
                            tipo_exam = celdas[0].inner_text().strip()
                            puntaje_raw = celdas[1].inner_text().strip()
                            preliminar_raw = celdas[2].inner_text().strip()

                            try:
                                puntaje = float(puntaje_raw.replace(",", ".")) if puntaje_raw else None
                            except ValueError:
                                puntaje = None

                            evaluaciones.append(
                                {
                                    "tipo_examen": tipo_exam,
                                    "puntaje": puntaje,
                                    "puntaje_preliminar": preliminar_raw,
                                }
                            )
                        elif len(celdas) >= 1:
                            texto_resumen = celdas[0].inner_text().strip()
                            if "Promedio Ponderado con Recuperatorio" in texto_resumen:
                                val = texto_resumen.split(":")[-1].strip()
                                try:
                                    promedio_recuperatorio = float(val.replace(",", "."))
                                except ValueError:
                                    promedio_recuperatorio = None
                            elif "Promedio Ponderado" in texto_resumen:
                                val = texto_resumen.split(":")[-1].strip()
                                try:
                                    promedio_ponderado = float(val.replace(",", "."))
                                except ValueError:
                                    promedio_ponderado = None
                            elif "Derecho" in texto_resumen:
                                val = texto_resumen.split(":")[-1].strip()
                                derecho = val.lower() in ["sí", "si", "true"]

                    materias_periodo.append(
                        {
                            "asignatura": nombre_materia,
                            "codigo": codigo_materia,
                            "evaluaciones": evaluaciones,
                            "promedio_ponderado": promedio_ponderado,
                            "promedio_recuperatorio": promedio_recuperatorio,
                            "derecho": derecho,
                        }
                    )

                if materias_periodo:
                    print(f"   ↳ [Scraper] Periodo {clave_periodo}: {len(materias_periodo)} materias recuperadas.")
                    resultados[clave_periodo] = materias_periodo

            # Decrementar periodo para la siguiente iteración
            if convocatoria == 2:
                convocatoria = 1
            else:
                convocatoria = 2
                anho -= 1

            if anho >= self.ANHO_MINIMO:
                ok = cambiar_periodo(anho, convocatoria)
                if not ok:
                    break

        print(f"✅ [Scraper] {len(resultados)} periodos recuperados con evaluaciones.")
        return resultados

    def ejecutar_flujo_completo(self, cedula: str, pin: str) -> Dict[str, Any]:
        """Coordina la sesión de Playwright, extrae todas las secciones y devuelve los datos crudos."""
        self._asegurar_playwright()
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()

            try:
                if not self.iniciar_sesion(page, cedula, pin):
                    browser.close()
                    raise ValueError("Credenciales inválidas o falla de conexión en INSWEB.")

                datos = {
                    "inscripciones": self.extraer_inscripciones(page),
                    "notas": self.extraer_notas(page),
                    "ficha": self.extraer_notas_parciales(page),
                }

                # Resguardar snapshot crudo en directorio data/
                os.makedirs("data", exist_ok=True)
                snapshot_file = os.path.join("data", f"insweb_raw_{cedula}.json")
                with open(snapshot_file, "w", encoding="utf-8") as f:
                    json.dump(datos, f, indent=2, ensure_ascii=False)

                return datos
            finally:
                browser.close()
