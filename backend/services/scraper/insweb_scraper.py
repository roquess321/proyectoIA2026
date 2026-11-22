import datetime
import json
import os
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

ProgressCallback = Optional[Callable[[Dict[str, Any]], None]]


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

    def _emit(
        self,
        on_progress: ProgressCallback,
        *,
        step: str,
        step_status: str,
        progress: int,
        message: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra telemetría en consola y notifica de forma segura al callback de progreso."""
        print(message, flush=True)
        if on_progress is None:
            return
        try:
            on_progress(
                {
                    "type": "progress",
                    "step": step,
                    "step_status": step_status,
                    "progress": progress,
                    "message": message,
                    "meta": meta or {},
                }
            )
        except Exception:
            pass

    def _asegurar_playwright(self) -> None:
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
        except ImportError:
            raise RuntimeError(
                "La librería 'playwright' no está instalada en el entorno virtual. "
                "Para activarla, ejecuta: 'uv add playwright' y luego 'uv run playwright install chromium'."
            )

    def iniciar_sesion(
        self,
        page: Any,
        cedula: str,
        pin: str,
        on_progress: ProgressCallback = None,
    ) -> bool:
        """Autenticación en el portal INSWEB."""
        self._emit(
            on_progress,
            step="handshake",
            step_status="running",
            progress=8,
            message=f"🌐 [Scraper] Conectando a {self.base_url}...",
        )

        last_err: Optional[Exception] = None
        for intento in range(2):
            try:
                page.goto(self.base_url, wait_until="domcontentloaded", timeout=25000)
                last_err = None
                break
            except Exception as exc:
                last_err = exc
                if intento == 0:
                    self._emit(
                        on_progress,
                        step="handshake",
                        step_status="running",
                        progress=10,
                        message="⚠️ [Scraper] Tiempo de espera inicial en InsWeb; reintentando conexión...",
                    )
                    time.sleep(1.0)

        if last_err is not None:
            err_msg = f"No se pudo conectar a InsWeb ({last_err})"
            self._emit(
                on_progress,
                step="handshake",
                step_status="error",
                progress=8,
                message=f"❌ [Scraper] {err_msg}",
            )
            raise RuntimeError(err_msg) from last_err

        try:
            campo_ci = page.locator('input[type="text"]').first
            campo_ci.wait_for(state="visible", timeout=20000)
            campo_ci.fill(cedula)

            campo_pin = page.locator('input[type="password"]').first
            campo_pin.wait_for(state="visible", timeout=10000)
            campo_pin.fill(pin)

            self._emit(
                on_progress,
                step="handshake",
                step_status="running",
                progress=15,
                message="🚀 [Scraper] Enviando credenciales a InsWeb...",
            )
            campo_pin.press("Enter")

            page.wait_for_url(lambda url: "login" not in url.lower(), timeout=20000)
            self._emit(
                on_progress,
                step="handshake",
                step_status="done",
                progress=22,
                message=f"✅ [Scraper] Sesión autenticada en InsWeb ({page.url})",
            )
            return True
        except Exception:
            self._emit(
                on_progress,
                step="handshake",
                step_status="error",
                progress=15,
                message="❌ [Scraper] Credenciales inválidas o tiempo de espera excedido en InsWeb.",
            )
            return False

    def extraer_inscripciones(
        self,
        page: Any,
        on_progress: ProgressCallback = None,
    ) -> Dict[str, Any]:
        """Extrae las materias e horarios de la página principal de forma atómica."""
        self._emit(
            on_progress,
            step="inscripciones",
            step_status="running",
            progress=26,
            message="🔍 [Scraper] [1/3] Extrayendo inscripciones vigentes...",
        )
        try:
            page.wait_for_selector("tbody > tr", state="visible", timeout=12000)
        except Exception:
            self._emit(
                on_progress,
                step="inscripciones",
                step_status="done",
                progress=36,
                message="⚠️ [Scraper] 0 inscripciones vigentes recuperadas.",
                meta={"inscripciones": 0},
            )
            return {}

        resultado: Dict[str, List[Dict[str, Any]]] = page.evaluate(
            """() => {
                const out = {};
                let carreraActual = "Carrera General";
                const filas = document.querySelectorAll("tbody > tr");
                for (const fila of filas) {
                    if (fila.closest("table.table-horarios")) continue;
                    const strongEl = fila.querySelector("strong");
                    if (strongEl) {
                        const txt = (strongEl.innerText || strongEl.textContent || "").trim();
                        if (txt) {
                            carreraActual = txt;
                            if (!out[carreraActual]) out[carreraActual] = [];
                        }
                        continue;
                    }
                    const celdas = Array.from(fila.children).filter(el => el.tagName === "TD");
                    if (celdas.length >= 4) {
                        const semestre = (celdas[0].innerText || "").trim();
                        const materiaRaw = (celdas[1].innerText || "").trim();
                        const estado = (celdas[2].innerText || "").trim();
                        const horarios = Array.from(celdas[3].querySelectorAll("td"))
                            .map(td => (td.innerText || "").trim())
                            .filter(Boolean);
                        const match = materiaRaw.match(/^(.*?)\\s*\\((\\d+)\\)$/);
                        const info = {
                            semestre,
                            codigo: match ? match[2] : "N/A",
                            nombre: match ? match[1].trim() : materiaRaw,
                            estado,
                            horarios,
                        };
                        if (!out[carreraActual]) out[carreraActual] = [];
                        out[carreraActual].push(info);
                    }
                }
                return out;
            }"""
        )

        total_ins = sum(len(v) for v in resultado.values())
        self._emit(
            on_progress,
            step="inscripciones",
            step_status="done",
            progress=36,
            message=f"✅ [Scraper] {total_ins} inscripciones vigentes recuperadas.",
            meta={"inscripciones": total_ins},
        )
        return resultado

    def extraer_notas(
        self,
        page: Any,
        on_progress: ProgressCallback = None,
    ) -> List[Dict[str, Any]]:
        """Extrae el historial de notas finales."""
        self._emit(
            on_progress,
            step="calificaciones",
            step_status="running",
            progress=40,
            message="🔍 [Scraper] [2/3] Extrayendo historial de notas finales...",
        )
        try:
            menu_notas = (
                page.locator("a, button, mat-list-item")
                .filter(has_text=re.compile(r"^\s*Notas\s*$", re.IGNORECASE))
                .first
            )
            if menu_notas.count() == 0:
                menu_notas = page.get_by_text("Notas", exact=True).first

            menu_notas.wait_for(state="visible", timeout=8000)
            menu_notas.click()

            opcion_notas_finales = page.get_by_text("Notas Finales", exact=True).first
            opcion_notas_finales.wait_for(state="visible", timeout=8000)
            opcion_notas_finales.click()

            page.wait_for_selector("tbody > tr", state="visible", timeout=12000)
        except Exception as e:
            self._emit(
                on_progress,
                step="calificaciones",
                step_status="running",
                progress=48,
                message=f"⚠️ [Scraper] No se pudo acceder a la tabla de notas finales: {e}",
            )
            return []

        filas_raw: List[List[str]] = page.evaluate(
            """() => {
                const rows = [];
                const trs = document.querySelectorAll("tbody > tr");
                for (const fila of trs) {
                    const celdas = Array.from(fila.children).filter(el => el.tagName === "TD");
                    if (celdas.length >= 5) {
                        rows.push([
                            (celdas[0].innerText || "").trim(),
                            (celdas[1].innerText || "").trim(),
                            (celdas[2].innerText || "").trim(),
                            (celdas[3].innerText || "").trim(),
                            (celdas[4].innerText || "").trim(),
                        ]);
                    }
                }
                return rows;
            }"""
        )

        historial_notas: List[Dict[str, Any]] = []
        for cols in filas_raw:
            raw_nota = cols[1]
            match_nota = re.search(r"^(\d+)\s*(?:\((.*?)\))?", raw_nota)
            if match_nota:
                nota_num: Any = int(match_nota.group(1))
                nota_txt = match_nota.group(2) if match_nota.group(2) else ""
            else:
                nota_num = raw_nota
                nota_txt = ""

            historial_notas.append(
                {
                    "asignatura": cols[0],
                    "nota": nota_num,
                    "nota_literal": nota_txt,
                    "fecha": cols[2],
                    "nro_acta": cols[3],
                    "tipo": cols[4],
                    "aprobado": isinstance(nota_num, int) and nota_num >= 2,
                }
            )

        self._emit(
            on_progress,
            step="calificaciones",
            step_status="running",
            progress=52,
            message=f"✅ [Scraper] {len(historial_notas)} notas finales recuperadas.",
            meta={"notas": len(historial_notas)},
        )
        return historial_notas

    def _leer_cards_periodo(self, page: Any) -> Tuple[str, List[Dict[str, Any]]]:
        """Lee atómicamente las tarjetas visibles de evaluaciones parciales en el DOM."""
        raw_cards: List[Dict[str, Any]] = page.evaluate(
            """() => {
                const result = [];
                const cards = document.querySelectorAll("div.card");
                for (const card of cards) {
                    const st = window.getComputedStyle(card);
                    if (st.display === "none" || st.visibility === "hidden" || card.getClientRects().length === 0) {
                        continue;
                    }
                    const tituloEl = card.querySelector("h4.title");
                    if (!tituloEl) continue;
                    const rawTitulo = (tituloEl.innerText || tituloEl.textContent || "").trim();
                    if (!rawTitulo) continue;

                    const evaluacionesRaw = [];
                    const resumenes = [];
                    const trs = card.querySelectorAll("tbody > tr");
                    for (const fila of trs) {
                        const celdas = Array.from(fila.children).filter(el => el.tagName === "TD");
                        if (celdas.length === 3 && !celdas[0].hasAttribute("colspan")) {
                            evaluacionesRaw.push({
                                tipo_examen: (celdas[0].innerText || "").trim(),
                                puntaje_raw: (celdas[1].innerText || "").trim(),
                                preliminar_raw: (celdas[2].innerText || "").trim(),
                            });
                        } else if (celdas.length >= 1) {
                            const texto = (celdas[0].innerText || "").trim();
                            if (texto) resumenes.push(texto);
                        }
                    }

                    result.push({
                        raw_titulo: rawTitulo,
                        evaluaciones: evaluacionesRaw,
                        resumenes,
                    });
                }
                return result;
            }"""
        )

        materias_periodo: List[Dict[str, Any]] = []
        sig_parts: List[str] = []

        for item in raw_cards:
            raw_titulo = str(item.get("raw_titulo", "")).strip()
            match_titulo = re.match(r"^(.*?)\s*\((.*?)\)$", raw_titulo)
            nombre_materia = match_titulo.group(1).strip() if match_titulo else raw_titulo
            codigo_materia = match_titulo.group(2).strip() if match_titulo else "N/A"

            evaluaciones: List[Dict[str, Any]] = []
            ev_sigs: List[str] = []
            for ev in item.get("evaluaciones", []):
                tipo_exam = str(ev.get("tipo_examen", "")).strip()
                puntaje_raw = str(ev.get("puntaje_raw", "")).strip()
                preliminar_raw = str(ev.get("preliminar_raw", "")).strip()
                try:
                    puntaje: Optional[float] = float(puntaje_raw.replace(",", ".")) if puntaje_raw else None
                except ValueError:
                    puntaje = None

                evaluaciones.append(
                    {
                        "tipo_examen": tipo_exam,
                        "puntaje": puntaje,
                        "puntaje_preliminar": preliminar_raw,
                    }
                )
                ev_sigs.append(f"{tipo_exam}={puntaje_raw}")

            promedio_ponderado: Optional[float] = None
            promedio_recuperatorio: Optional[float] = None
            derecho: Optional[bool] = None

            for texto_resumen in item.get("resumenes", []):
                texto_str = str(texto_resumen).strip()
                if "Promedio Ponderado con Recuperatorio" in texto_str:
                    val = texto_str.split(":")[-1].strip()
                    try:
                        promedio_recuperatorio = float(val.replace(",", "."))
                    except ValueError:
                        promedio_recuperatorio = None
                elif "Promedio Ponderado" in texto_str:
                    val = texto_str.split(":")[-1].strip()
                    try:
                        promedio_ponderado = float(val.replace(",", "."))
                    except ValueError:
                        promedio_ponderado = None
                elif "Derecho" in texto_str:
                    val = texto_str.split(":")[-1].strip()
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
            sig_parts.append(f"{raw_titulo}:{'|'.join(ev_sigs)}:{derecho}")

        return "||".join(sig_parts), materias_periodo

    _EVAL_API_FIELDS: Tuple[Tuple[str, str], ...] = (
        ("pp", "Primer Parcial"),
        ("sp", "Segundo Parcial"),
        ("tp", "Tercer Parcial"),
        ("cp", "Cuarto Parcial"),
        ("aot", "Trabajo Práctico / Taller / Otros"),
        ("prf", "Primer Recuperatorio"),
        ("srf", "Segundo Recuperatorio"),
        ("trf", "Tercer Recuperatorio"),
        ("lab", "Laboratorio"),
        ("proy", "Proyecto"),
        ("prfc", "Primer Recuperatorio Final"),
        ("srfc", "Segundo Recuperatorio Final"),
        ("trfc", "Tercer Recuperatorio Final"),
    )

    @staticmethod
    def _parse_float_or_none(val: Any) -> Optional[float]:
        if val is None or isinstance(val, bool):
            return None
        txt = str(val).strip().replace(",", ".")
        if not txt:
            return None
        try:
            return float(txt)
        except ValueError:
            return None

    @staticmethod
    def _parse_kv_metric(blob: Optional[str], key: str) -> Optional[str]:
        if not blob:
            return None
        match = re.search(rf"(?:^|,)\s*{re.escape(key)}=([^,]+)", str(blob))
        return match.group(1).strip() if match else None

    def _extraer_parciales_via_api(
        self,
        page: Any,
        on_progress: ProgressCallback = None,
    ) -> Optional[Dict[str, Any]]:
        """Consulta directamente los endpoints JSON autenticados de INSWEB por año y convocatoria."""
        req = getattr(page.context, "request", None)
        if req is None:
            return None

        api_base = "https://insweb.ing.una.py/insweb-backend"
        cfg_anho = datetime.datetime.now().year
        cfg_sem = 2
        anho_min = self.ANHO_MINIMO

        try:
            r_cfg = req.get(f"{api_base}/exafinalconfig/1", timeout=8000)
            if r_cfg.ok:
                cfg_data = r_cfg.json()
                if isinstance(cfg_data, dict):
                    if str(cfg_data.get("anho", "")).isdigit():
                        cfg_anho = int(cfg_data["anho"])
                    if str(cfg_data.get("semestre", "")).isdigit():
                        cfg_sem = int(cfg_data["semestre"])
        except Exception:
            pass

        try:
            r_perf = req.get(f"{api_base}/ver_perfil", timeout=8000)
            if r_perf.ok:
                perf_data = r_perf.json()
                if isinstance(perf_data, dict) and str(perf_data.get("anhoingreso", "")).isdigit():
                    ingreso = int(perf_data["anhoingreso"])
                    anho_min = max(2015, min(self.ANHO_MINIMO, ingreso))
        except Exception:
            pass

        anho_inicio = max(cfg_anho, datetime.datetime.now().year)
        convocatoria_inicio = 2

        self._emit(
            on_progress,
            step="calificaciones",
            step_status="running",
            progress=56,
            message=(
                f"🔄 [Scraper] Config INSWEB: {cfg_anho}_C{cfg_sem}. "
                f"Consultando historial de parciales desde {anho_inicio}_C{convocatoria_inicio} hasta {anho_min}_C1..."
            ),
        )

        periodos: List[Tuple[int, int]] = []
        a, c = anho_inicio, convocatoria_inicio
        while a >= anho_min:
            periodos.append((a, c))
            if c == 2:
                c = 1
            else:
                c = 2
                a -= 1

        resultados: Dict[str, Any] = {}
        total_periodos = max(1, len(periodos))

        for iter_idx, (anho, conv) in enumerate(periodos):
            clave_periodo = f"{anho}_C{conv}"
            prog = min(88, 56 + int((iter_idx / total_periodos) * 32))

            try:
                r_par = req.get(
                    f"{api_base}/notas_parciales/?anho={anho}&convocatoria={conv}",
                    timeout=10000,
                )
                r_pre = req.get(
                    f"{api_base}/notas_preliminares/?anho={anho}&convocatoria={conv}",
                    timeout=10000,
                )
                if r_par.status != 200 or r_pre.status != 200:
                    if iter_idx == 0:
                        return None
                    self._emit(
                        on_progress,
                        step="calificaciones",
                        step_status="running",
                        progress=prog,
                        message=(
                            f"⚠️ [Scraper] Periodo {clave_periodo} respondió HTTP "
                            f"{r_par.status}/{r_pre.status}; omitido."
                        ),
                    )
                    continue

                par_json = r_par.json()
                pre_json = r_pre.json()
                if not isinstance(par_json, list) or not isinstance(pre_json, list):
                    if iter_idx == 0:
                        return None
                    continue
            except Exception as exc_api:
                if iter_idx == 0:
                    self._emit(
                        on_progress,
                        step="calificaciones",
                        step_status="running",
                        progress=57,
                        message=f"⚠️ [Scraper] API directa no disponible ({exc_api}); usando modo DOM...",
                    )
                    return None
                self._emit(
                    on_progress,
                    step="calificaciones",
                    step_status="running",
                    progress=prog,
                    message=f"⚠️ [Scraper] Error consultando {clave_periodo}: {exc_api}",
                )
                continue

            combined: Dict[str, Dict[str, Any]] = {}
            ordered_keys: List[str] = []

            def _ensure_entry(raw_row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
                cod = str(raw_row.get("codasign") or "").strip()
                desc = str(raw_row.get("descrip") or "").strip()
                key = cod if cod else desc.upper()
                if not key:
                    return None
                if key not in combined:
                    combined[key] = {
                        "asignatura": desc or cod,
                        "codigo": cod or "N/A",
                        "parcial": None,
                        "prelim": None,
                    }
                    ordered_keys.append(key)
                else:
                    if desc and combined[key]["asignatura"] == combined[key]["codigo"]:
                        combined[key]["asignatura"] = desc
                return combined[key]

            for row in par_json:
                if isinstance(row, dict):
                    entry = _ensure_entry(row)
                    if entry is not None:
                        entry["parcial"] = row

            for row in pre_json:
                if isinstance(row, dict):
                    entry = _ensure_entry(row)
                    if entry is not None:
                        entry["prelim"] = row

            materias_periodo: List[Dict[str, Any]] = []
            for key in ordered_keys:
                entry = combined[key]
                par_row = entry["parcial"] or {}
                pre_row = entry["prelim"] or {}

                evaluaciones: List[Dict[str, Any]] = []
                for field_key, tipo_label in self._EVAL_API_FIELDS:
                    par_val = par_row.get(field_key)
                    pre_val = pre_row.get(field_key)
                    pre_str = str(pre_val).strip() if pre_val is not None else ""
                    if par_val is None and not pre_str:
                        continue

                    evaluaciones.append(
                        {
                            "tipo_examen": tipo_label,
                            "puntaje": self._parse_float_or_none(par_val),
                            "puntaje_preliminar": pre_str,
                        }
                    )

                prom_blob = pre_row.get("promedio")
                recu_blob = pre_row.get("promedio_conrecu")
                promedio_ponderado = self._parse_float_or_none(
                    self._parse_kv_metric(prom_blob, "SUMATOTAL")
                )
                derecho_raw = self._parse_kv_metric(prom_blob, "DERECHO")
                derecho: Optional[bool] = (
                    derecho_raw.upper() == "S" if derecho_raw in ("S", "N", "s", "n") else None
                )

                recu_val = self._parse_float_or_none(
                    self._parse_kv_metric(recu_blob, "SUMARECU")
                )
                has_recu_ev = any(
                    (
                        par_row.get(rk) is not None
                        or (pre_row.get(rk) is not None and str(pre_row.get(rk)).strip() != "")
                    )
                    for rk in ("prf", "srf", "trf", "prfc", "srfc", "trfc")
                )
                promedio_recuperatorio: Optional[float] = (
                    recu_val
                    if recu_val is not None
                    and recu_val > 0
                    and (bool(pre_row.get("tienederechorecu")) or has_recu_ev)
                    else None
                )

                materias_periodo.append(
                    {
                        "asignatura": entry["asignatura"],
                        "codigo": entry["codigo"],
                        "evaluaciones": evaluaciones,
                        "promedio_ponderado": promedio_ponderado,
                        "promedio_recuperatorio": promedio_recuperatorio,
                        "derecho": derecho,
                    }
                )

            if materias_periodo:
                resultados[clave_periodo] = materias_periodo
                msg_periodo = f"   ↳ [Scraper] Periodo {clave_periodo}: {len(materias_periodo)} materias recuperadas."
            else:
                msg_periodo = f"   ↳ [Scraper] Periodo {clave_periodo}: sin evaluaciones registradas."

            self._emit(
                on_progress,
                step="calificaciones",
                step_status="running",
                progress=prog,
                message=msg_periodo,
                meta={"periodo": clave_periodo, "materias": len(materias_periodo)},
            )

        self._emit(
            on_progress,
            step="calificaciones",
            step_status="done",
            progress=90,
            message=f"✅ [Scraper] Extracción histórica completada ({len(resultados)} periodos con parciales).",
            meta={"periodos": len(resultados)},
        )
        return resultados

    def extraer_notas_parciales(
        self,
        page: Any,
        on_progress: ProgressCallback = None,
    ) -> Dict[str, Any]:
        """Extrae el desglose de evaluaciones parciales (API directa con fallback a DOM)."""
        self._emit(
            on_progress,
            step="calificaciones",
            step_status="running",
            progress=55,
            message="🔍 [Scraper] [3/3] Extrayendo notas parciales por periodo...",
        )

        # Vía rápida y atómica contra la API autenticada de INSWEB
        api_resultados = self._extraer_parciales_via_api(page, on_progress=on_progress)
        if api_resultados is not None:
            return api_resultados

        # Fallback DOM en caso de cambio o indisponibilidad del endpoint directo
        try:
            menu_notas = (
                page.locator("a, button, mat-list-item")
                .filter(has_text=re.compile(r"^\s*Notas\s*$", re.IGNORECASE))
                .first
            )
            if menu_notas.count() == 0:
                menu_notas = page.get_by_text("Notas", exact=True).first

            menu_notas.wait_for(state="visible", timeout=8000)
            menu_notas.click()

            opcion_parciales = page.get_by_text("Notas Parciales", exact=True).first
            opcion_parciales.wait_for(state="visible", timeout=8000)
            opcion_parciales.click()

            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception as e:
            self._emit(
                on_progress,
                step="calificaciones",
                step_status="done",
                progress=90,
                message=f"⚠️ [Scraper] No se pudo acceder a notas parciales: {e}",
            )
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
            input_anho.wait_for(state="visible", timeout=8000)
            input_convocatoria.wait_for(state="visible", timeout=8000)
        except Exception:
            self._emit(
                on_progress,
                step="calificaciones",
                step_status="done",
                progress=90,
                message="⚠️ [Scraper] Formulario de filtros por periodo no disponible en InsWeb.",
            )
            return {}

        anho_str, convocatoria_str = "", ""
        for _ in range(5):
            anho_str = input_anho.input_value().strip()
            convocatoria_str = input_convocatoria.input_value().strip()
            if anho_str and convocatoria_str:
                break
            time.sleep(0.8)

        anho_defecto = int(anho_str) if anho_str.isdigit() else datetime.datetime.now().year
        convocatoria_defecto = int(convocatoria_str) if convocatoria_str.isdigit() else 2

        # Iniciar obligatoriamente un semestre por arriba del que InsWeb muestra por defecto
        if convocatoria_defecto == 1:
            anho_inicio = anho_defecto
            convocatoria_inicio = 2
        else:
            anho_inicio = anho_defecto + 1
            convocatoria_inicio = 1

        self._emit(
            on_progress,
            step="calificaciones",
            step_status="running",
            progress=56,
            message=(
                f"🔄 [Scraper] Periodo por defecto en InsWeb: {anho_defecto}_C{convocatoria_defecto}. "
                f"Iniciando barrido DOM desde {anho_inicio}_C{convocatoria_inicio}..."
            ),
        )

        def cambiar_periodo(a: int, c: int, prev_signature: str) -> bool:
            if "login" in page.url.lower():
                self._emit(
                    on_progress,
                    step="calificaciones",
                    step_status="running",
                    progress=85,
                    message="⚠️ [Scraper] Sesión expirada en InsWeb; deteniendo consulta de periodos restantes.",
                )
                return False

            try:
                cur_a = input_anho.input_value().strip()
                anho_cambiado = cur_a != str(a)

                # Rellenar inputs y emitir cambio único con blur para evitar XHR solapados
                if anho_cambiado:
                    input_anho.fill(str(a))
                    input_anho.dispatch_event("change")

                input_convocatoria.fill(str(c))
                input_convocatoria.dispatch_event("change")
                input_convocatoria.evaluate("el => el.blur()")

                try:
                    page.wait_for_load_state("networkidle", timeout=4000)
                except Exception:
                    pass

                # No abortar por DOM vacío transitorio mientras Angular carga las tarjetas
                last_sig: Optional[str] = None
                stable_count = 0
                changed = False
                for step_idx in range(10):
                    time.sleep(0.3)
                    try:
                        sig_now, _ = self._leer_cards_periodo(page)
                    except Exception:
                        sig_now = ""
                    if sig_now != prev_signature:
                        changed = True
                    if sig_now == last_sig:
                        stable_count += 1
                    else:
                        stable_count = 0
                        last_sig = sig_now
                    if changed and stable_count >= 1 and (sig_now != "" or step_idx >= 4):
                        break
                    if not changed and step_idx >= 4 and stable_count >= 2:
                        break

                return True
            except Exception as ex:
                self._emit(
                    on_progress,
                    step="calificaciones",
                    step_status="running",
                    progress=70,
                    message=f"⚠️ [Scraper] Error al cambiar a periodo {a}_C{c}: {ex}",
                )
                return False

        try:
            prev_signature, _ = self._leer_cards_periodo(page)
        except Exception:
            prev_signature = ""

        # Forzar la carga en pantalla del ciclo superior antes de comenzar la extracción
        cambiar_periodo(anho_inicio, convocatoria_inicio, prev_signature)

        anho = anho_inicio
        convocatoria = convocatoria_inicio
        resultados: Dict[str, Any] = {}
        total_periodos = max(1, (anho_inicio - self.ANHO_MINIMO) * 2 + convocatoria_inicio)
        iter_idx = 0

        # Bucle descendente por periodos desde el ciclo forzado superior hasta ANHO_MINIMO
        while anho >= self.ANHO_MINIMO:
            clave_periodo = f"{anho}_C{convocatoria}"
            prog = min(88, 56 + int((iter_idx / total_periodos) * 32))

            materias_periodo: List[Dict[str, Any]] = []
            lectura_ok = False
            for intento_lectura in range(2):
                try:
                    sig_actual, materias_periodo = self._leer_cards_periodo(page)
                    prev_signature = sig_actual
                    lectura_ok = True
                    break
                except Exception as exc_card:
                    if intento_lectura == 0:
                        time.sleep(0.8)
                    else:
                        self._emit(
                            on_progress,
                            step="calificaciones",
                            step_status="running",
                            progress=prog,
                            message=f"⚠️ [Scraper] Periodo {clave_periodo} omitido por actualización DOM: {exc_card}",
                        )

            if lectura_ok:
                if materias_periodo:
                    resultados[clave_periodo] = materias_periodo
                    msg_periodo = f"   ↳ [Scraper] Periodo {clave_periodo}: {len(materias_periodo)} materias recuperadas."
                else:
                    msg_periodo = f"   ↳ [Scraper] Periodo {clave_periodo}: sin evaluaciones registradas."
                self._emit(
                    on_progress,
                    step="calificaciones",
                    step_status="running",
                    progress=prog,
                    message=msg_periodo,
                    meta={"periodo": clave_periodo, "materias": len(materias_periodo)},
                )

            iter_idx += 1

            # Decrementar periodo para la siguiente iteración
            if convocatoria == 2:
                convocatoria = 1
            else:
                convocatoria = 2
                anho -= 1

            if anho >= self.ANHO_MINIMO:
                ok = cambiar_periodo(anho, convocatoria, prev_signature)
                if not ok:
                    break

        self._emit(
            on_progress,
            step="calificaciones",
            step_status="done",
            progress=90,
            message=f"✅ [Scraper] Extracción histórica completada ({len(resultados)} periodos con parciales).",
            meta={"periodos": len(resultados)},
        )
        return resultados

    def ejecutar_flujo_completo(
        self,
        cedula: str,
        pin: str,
        on_progress: ProgressCallback = None,
    ) -> Dict[str, Any]:
        """Coordina la sesión de Playwright, extrae todas las secciones y devuelve los datos crudos."""
        self._asegurar_playwright()
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context()
            page = context.new_page()

            try:
                if not self.iniciar_sesion(page, cedula, pin, on_progress=on_progress):
                    raise ValueError("Credenciales inválidas o falla de conexión en INSWEB.")

                datos = {
                    "inscripciones": self.extraer_inscripciones(page, on_progress=on_progress),
                    "notas": self.extraer_notas(page, on_progress=on_progress),
                    "ficha": self.extraer_notas_parciales(page, on_progress=on_progress),
                }

                # Resguardar snapshot crudo en directorio data/ (best-effort para entornos cloud/efímeros)
                try:
                    data_dir = os.path.join(
                        os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "data"
                    )
                    os.makedirs(data_dir, exist_ok=True)
                    snapshot_file = os.path.join(data_dir, f"insweb_raw_{cedula}.json")
                    with open(snapshot_file, "w", encoding="utf-8") as f:
                        json.dump(datos, f, indent=2, ensure_ascii=False)
                except Exception as snapshot_err:
                    print(f"⚠️ No se pudo guardar snapshot crudo en disco: {snapshot_err}")

                return datos
            finally:
                try:
                    browser.close()
                except Exception:
                    pass
