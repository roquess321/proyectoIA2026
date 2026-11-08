from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

try:
    from ...models import Estudiante, Inscripcion, Parcial, NotaFinal
    from .cleaner import sanitizar_datos_estudiante
    from .insweb_scraper import INSWEBScraper
except ImportError:
    from backend.models import Estudiante, Inscripcion, Parcial, NotaFinal
    from backend.services.scraper.cleaner import sanitizar_datos_estudiante
    from backend.services.scraper.insweb_scraper import INSWEBScraper


def persistir_datos_estudiante(cedula: str, datos_limpios: Dict[str, Any], db: Session) -> Dict[str, int]:
    """Guarda en la base de datos SQLite relacional los datos académicos sanitizados."""
    # 1. Crear o actualizar estudiante
    estudiante = db.query(Estudiante).filter(Estudiante.cedula == cedula).first()
    ahora = datetime.now(timezone.utc)
    if not estudiante:
        estudiante = Estudiante(cedula=cedula, fecha_actualizacion=ahora)
        db.add(estudiante)
    else:
        estudiante.fecha_actualizacion = ahora

    db.flush()

    # 2. Reemplazar registros anteriores del estudiante
    db.query(Inscripcion).filter(Inscripcion.cedula == cedula).delete()
    db.query(Parcial).filter(Parcial.cedula == cedula).delete()
    db.query(NotaFinal).filter(NotaFinal.cedula == cedula).delete()

    # 3. Insertar inscripciones
    inscripciones_objs = [
        Inscripcion(
            cedula=cedula,
            carrera=item.get("carrera"),
            asignatura=item["asignatura"],
            semestre=item.get("semestre"),
            estado=item.get("estado"),
        )
        for item in datos_limpios.get("inscripciones", [])
        if item.get("asignatura")
    ]
    db.bulk_save_objects(inscripciones_objs)

    # 4. Insertar evaluaciones parciales
    parciales_objs = [
        Parcial(
            cedula=cedula,
            asignatura=item["asignatura"],
            tipo_examen=item["tipo_examen"],
            puntaje=item.get("puntaje"),
            periodo=item.get("periodo"),
        )
        for item in datos_limpios.get("parciales", [])
        if item.get("asignatura")
    ]
    db.bulk_save_objects(parciales_objs)

    # 5. Insertar notas finales
    notas_objs = [
        NotaFinal(
            cedula=cedula,
            asignatura=item["asignatura"],
            nota=item.get("nota"),
            nota_literal=item.get("nota_literal"),
            fecha=item.get("fecha"),
            nro_acta=item.get("nro_acta"),
            tipo=item.get("tipo"),
            aprobado=item.get("aprobado", False),
        )
        for item in datos_limpios.get("notas", [])
        if item.get("asignatura")
    ]
    db.bulk_save_objects(notas_objs)

    db.commit()

    return {
        "inscripciones": len(inscripciones_objs),
        "parciales": len(parciales_objs),
        "notas": len(notas_objs),
    }


def ejecutar_pipeline_estudiante(
    cedula: str,
    pin: str,
    db: Session,
) -> Dict[str, Any]:
    """Orquesta la extracción (Playwright), sanitización y persistencia (SQLAlchemy) de un estudiante."""
    bot = INSWEBScraper()
    datos_crudos = bot.ejecutar_flujo_completo(cedula=cedula, pin=pin)

    if not datos_crudos:
        raise ValueError("No se pudieron extraer datos de INSWEB. Verifica las credenciales.")

    datos_limpios = sanitizar_datos_estudiante(datos_crudos)
    conteos = persistir_datos_estudiante(cedula=cedula, datos_limpios=datos_limpios, db=db)

    return {
        "ok": True,
        "cedula": cedula,
        "conteo": conteos,
        "datos": datos_limpios,
    }
