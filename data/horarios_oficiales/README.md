# Horarios Oficiales de Exámenes — FIUNA

Coloca o actualiza el archivo **`calendario_examenes.json`** en esta carpeta (`data/horarios_oficiales/`).
El backend FastAPI (`GET /api/horarios/examenes`) lee esta carpeta automáticamente en cada consulta (sin reiniciar el servidor) y filtra las materias que coincidan con las inscripciones vigentes del alumno en SQLite.

## Formato esperado (`calendario_examenes.json`)

```json
{
  "periodo": "2026-2",
  "fuente": "Cronograma Oficial FIUNA",
  "actualizado_en": "2026-11-20",
  "examenes": [
    {
      "asignatura": "PROBABILIDAD Y ESTADISTICA",
      "instancia": "2do Parcial",
      "fecha": "2026-11-26",
      "hora": "14:00 hs",
      "aula": "Aula E-12"
    }
  ]
}
```

- **`asignatura`**: nombre de la materia (se compara sin tildes ni mayúsculas/minúsculas). Usa `"GENERAL"` para hitos institucionales visibles para todos los estudiantes (por ejemplo, inicio de finales).
- **`fecha`**: formato ISO `YYYY-MM-DD`. Los días restantes y la urgencia se calculan automáticamente respecto a la fecha actual.
- **Automatización futura**: cualquier scraper o tarea programada solo necesita sobreescribir `data/horarios_oficiales/calendario_examenes.json` (o guardar un `.json` más reciente en esta misma carpeta) para que toda la plataforma muestre el calendario actualizado al instante.
