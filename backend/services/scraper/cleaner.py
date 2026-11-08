import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _limpiar_texto(valor: Any) -> str:
    """Convierte cualquier valor a string limpio sin espacios extras."""
    if valor is None:
        return ""
    return str(valor).strip()


def _limpiar_puntaje(valor: Any) -> Optional[float]:
    """Convierte de forma segura puntajes (incluyendo None o textos) a float."""
    if valor is None or valor == "":
        return None
    val_str = str(valor).strip().replace(",", ".")
    try:
        return float(val_str)
    except (ValueError, TypeError):
        return None


def sanitizar_inscripciones(inscripciones_raw: Any) -> List[Dict[str, str]]:
    """Normaliza las materias inscritas por el estudiante."""
    inscripciones_limpias: List[Dict[str, str]] = []

    if isinstance(inscripciones_raw, dict):
        for carrera_nombre, lista_materias in inscripciones_raw.items():
            if isinstance(lista_materias, list):
                for item in lista_materias:
                    if isinstance(item, dict):
                        inscripciones_limpias.append(
                            {
                                "carrera": _limpiar_texto(carrera_nombre),
                                "asignatura": _limpiar_texto(item.get("nombre") or item.get("asignatura")),
                                "semestre": _limpiar_texto(item.get("semestre")),
                                "estado": _limpiar_texto(item.get("estado")),
                            }
                        )
    elif isinstance(inscripciones_raw, list):
        for item in inscripciones_raw:
            if isinstance(item, dict):
                inscripciones_limpias.append(
                    {
                        "carrera": _limpiar_texto(item.get("carrera")),
                        "asignatura": _limpiar_texto(item.get("asignatura") or item.get("nombre")),
                        "semestre": _limpiar_texto(item.get("semestre")),
                        "estado": _limpiar_texto(item.get("estado")),
                    }
                )

    return inscripciones_limpias


def sanitizar_parciales(ficha_raw: Any) -> List[Dict[str, Any]]:
    """Extrae y normaliza las evaluaciones parciales desde la ficha histórica de periodos."""
    parciales_limpios: List[Dict[str, Any]] = []

    if isinstance(ficha_raw, dict):
        for periodo, lista_materias in ficha_raw.items():
            if isinstance(lista_materias, list):
                for materia in lista_materias:
                    if isinstance(materia, dict):
                        nombre_asig = _limpiar_texto(materia.get("asignatura"))
                        evaluaciones = materia.get("evaluaciones", [])

                        if isinstance(evaluaciones, list):
                            for ev in evaluaciones:
                                if isinstance(ev, dict):
                                    parciales_limpios.append(
                                        {
                                            "asignatura": nombre_asig,
                                            "tipo_examen": _limpiar_texto(
                                                ev.get("tipo_examen", "Parcial")
                                            ),
                                            "puntaje": _limpiar_puntaje(ev.get("puntaje")),
                                            "periodo": _limpiar_texto(periodo),
                                        }
                                    )

    return parciales_limpios


def sanitizar_notas(notas_raw: Any) -> List[Dict[str, Any]]:
    """Normaliza el historial de notas finales del estudiante."""
    notas_limpias: List[Dict[str, Any]] = []

    if isinstance(notas_raw, list):
        for item in notas_raw:
            if isinstance(item, dict):
                raw_nota = item.get("nota")
                nota_int = None
                if isinstance(raw_nota, int):
                    nota_int = raw_nota
                elif isinstance(raw_nota, str) and raw_nota.strip().isdigit():
                    nota_int = int(raw_nota.strip())

                aprobado = item.get("aprobado")
                if aprobado is None and nota_int is not None:
                    aprobado = nota_int >= 2

                notas_limpias.append(
                    {
                        "asignatura": _limpiar_texto(item.get("asignatura")),
                        "nota": nota_int,
                        "nota_literal": _limpiar_texto(item.get("nota_literal")),
                        "fecha": _limpiar_texto(item.get("fecha")),
                        "nro_acta": _limpiar_texto(item.get("nro_acta")),
                        "tipo": _limpiar_texto(item.get("tipo")),
                        "aprobado": bool(aprobado),
                    }
                )

    return notas_limpias


def sanitizar_datos_estudiante(datos_crudos: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Toma el diccionario crudo del scraper y lo transforma a un esquema estructurado y limpio."""
    if not datos_crudos:
        return {"inscripciones": [], "parciales": [], "notas": []}

    return {
        "inscripciones": sanitizar_inscripciones(datos_crudos.get("inscripciones", {})),
        "parciales": sanitizar_parciales(datos_crudos.get("ficha", {})),
        "notas": sanitizar_notas(datos_crudos.get("notas", [])),
    }
