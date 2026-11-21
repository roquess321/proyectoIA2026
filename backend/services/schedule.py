import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_DIR.parent
OFFICIAL_SCHEDULES_DIR = _PROJECT_ROOT / "data" / "horarios_oficiales"
DEFAULT_SCHEDULE_FILE = OFFICIAL_SCHEDULES_DIR / "calendario_examenes.json"

_MESES_ES = [
    "ENE",
    "FEB",
    "MAR",
    "ABR",
    "MAY",
    "JUN",
    "JUL",
    "AGO",
    "SEP",
    "OCT",
    "NOV",
    "DIC",
]


def _normalizar(texto: str) -> str:
    res = texto.strip().upper()
    for acc, raw in [("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"), ("Ñ", "N")]:
        res = res.replace(acc, raw)
    # Normalizar romanos finales comunes (I, II, III -> 1, 2, 3) para mejor matching
    tokens = res.split()
    roman_map = {"I": "1", "II": "2", "III": "3", "IV": "4"}
    if tokens and tokens[-1] in roman_map:
        tokens[-1] = roman_map[tokens[-1]]
    return " ".join(tokens)


def _resolver_archivo_horario() -> Optional[Path]:
    """Devuelve calendario_examenes.json si existe, o el archivo .json más reciente de la carpeta."""
    if DEFAULT_SCHEDULE_FILE.exists():
        return DEFAULT_SCHEDULE_FILE
    if not OFFICIAL_SCHEDULES_DIR.exists():
        return None
    candidatos = sorted(
        OFFICIAL_SCHEDULES_DIR.glob("*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidatos[0] if candidatos else None


def _parsear_fecha(fecha_str: str) -> Optional[date]:
    limpio = fecha_str.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(limpio, fmt).date()
        except ValueError:
            continue
    return None


def _carrera_compatible(examen_carrera: str, carreras_alumno_norm: List[str]) -> bool:
    if not carreras_alumno_norm or not examen_carrera:
        return True
    ex_car = _normalizar(examen_carrera)
    if ex_car in {"CURSOS BASICOS", "ASIGNATURAS COMPLEMENTARIAS", "GENERAL", "TODAS"}:
        return True
    for car in carreras_alumno_norm:
        # Comparar por palabra clave de la carrera (CIVIL, MECATRONICA, ELECTRONICA, etc.)
        if ex_car in car or car in ex_car:
            return True
        ex_words = [w for w in ex_car.split() if len(w) >= 5 and w != "INGENIERIA"]
        if any(w in car for w in ex_words):
            return True
    return False


def _coincide_materia(examen_asig: str, inscripciones_norm: List[str]) -> bool:
    ex_norm = _normalizar(examen_asig)
    if ex_norm in {"GENERAL", "TODOS", "FIUNA"}:
        return True
    for ins in inscripciones_norm:
        if ex_norm == ins or ex_norm in ins or ins in ex_norm:
            return True
        # Manejo singular/plural común (ej. LENGUAJE vs LENGUAJES)
        if ex_norm.replace("LENGUAJES", "LENGUAJE") == ins.replace("LENGUAJES", "LENGUAJE"):
            return True
    return False


def cargar_calendario_oficial(
    inscripciones: Optional[List[str]] = None,
    carreras_alumno: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Lee el calendario oficial desde data/horarios_oficiales/ y lo formatea para el Dashboard.
    Si se pasan `inscripciones` y `carreras_alumno`, filtra priorizando los exámenes
    exactos de la carrera y asignaturas matriculadas del estudiante.
    """
    archivo = _resolver_archivo_horario()
    if archivo is None:
        return {
            "source": "no_disponible",
            "periodo": None,
            "fuente": "Sin archivo oficial en data/horarios_oficiales/",
            "actualizado_en": None,
            "archivo": "data/horarios_oficiales/calendario_examenes.json",
            "examenes": [],
        }

    try:
        raw = json.loads(archivo.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "source": "error_lectura",
            "periodo": None,
            "fuente": f"Error al leer {archivo.name}: {exc}",
            "actualizado_en": None,
            "archivo": f"data/horarios_oficiales/{archivo.name}",
            "examenes": [],
        }

    items_raw = raw.get("examenes", [])
    if not isinstance(items_raw, list):
        items_raw = []

    inscripciones_norm = [_normalizar(a) for a in (inscripciones or []) if a and a.strip()]
    carreras_norm = [_normalizar(c) for c in (carreras_alumno or []) if c and c.strip()]
    hoy = date.today()

    eventos_carrera_y_materia: List[Dict[str, Any]] = []
    eventos_solo_materia: List[Dict[str, Any]] = []
    eventos_todos: List[Dict[str, Any]] = []

    for idx, item in enumerate(items_raw):
        if not isinstance(item, dict):
            continue
        asignatura = str(item.get("asignatura", "")).strip()
        instancia = str(item.get("instancia", "Examen")).strip()
        fecha_raw = str(item.get("fecha", "")).strip()
        hora = str(item.get("hora", "A confirmar")).strip()
        aula = str(item.get("aula", "FIUNA San Lorenzo")).strip()
        carrera_item = str(item.get("carrera", "")).strip()

        fecha_dt = _parsear_fecha(fecha_raw)
        if fecha_dt:
            month = _MESES_ES[fecha_dt.month - 1]
            day = f"{fecha_dt.day:02d}"
            days_remaining = (fecha_dt - hoy).days
            sort_key = fecha_dt.toordinal()
        else:
            month = "---"
            day = "--"
            days_remaining = 0
            sort_key = 9999999

        es_final = "final" in instancia.lower()
        if es_final:
            urgency = "final"
        elif 0 <= days_remaining <= 7:
            urgency = "critical"
        else:
            urgency = "normal"

        titulo = (
            instancia
            if _normalizar(asignatura) in {"GENERAL", "TODOS", "FIUNA"}
            else f"{asignatura} - {instancia}"
        )

        evento = {
            "id": f"official-{idx + 1}",
            "asignatura": asignatura,
            "instancia": instancia,
            "fecha": fecha_raw,
            "month": month,
            "day": day,
            "title": titulo,
            "subtitle": aula,
            "days_remaining": max(0, days_remaining),
            "time": hora,
            "urgency": urgency,
            "_sort_key": sort_key,
            "_is_past": days_remaining < 0,
            "_dedup_key": f"{_normalizar(asignatura)}|{instancia}|{fecha_raw}|{hora}",
        }
        eventos_todos.append(evento)

        if inscripciones_norm and _coincide_materia(asignatura, inscripciones_norm):
            eventos_solo_materia.append(evento)
            if _carrera_compatible(carrera_item, carreras_norm):
                eventos_carrera_y_materia.append(evento)

    if eventos_carrera_y_materia:
        seleccionados = eventos_carrera_y_materia
    elif eventos_solo_materia:
        seleccionados = eventos_solo_materia
    else:
        seleccionados = eventos_todos

    # Mostrar primero próximos exámenes (>= hoy) ordenados por fecha ascendente
    futuros = [e for e in seleccionados if not e["_is_past"]]
    final_list = futuros if futuros else seleccionados
    final_list.sort(key=lambda e: (e["_sort_key"], e["time"]))

    # Evitar duplicados exactos (ej. secciones idénticas)
    vistos = set()
    examenes_limpios: List[Dict[str, Any]] = []
    for e in final_list:
        dk = e["_dedup_key"]
        if dk in vistos:
            continue
        vistos.add(dk)
        examenes_limpios.append({k: v for k, v in e.items() if not k.startswith("_")})
        if len(examenes_limpios) >= 12:
            break

    return {
        "source": "archivo_oficial",
        "periodo": raw.get("periodo"),
        "fuente": raw.get("fuente") or f"Archivo oficial ({archivo.name})",
        "actualizado_en": raw.get("actualizado_en"),
        "archivo": f"data/horarios_oficiales/{archivo.name}",
        "examenes": examenes_limpios,
    }
