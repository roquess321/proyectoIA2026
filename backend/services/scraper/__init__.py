"""Módulo de Scraper e ingesta de datos de INSWEB para FIUNA."""
from .cleaner import sanitizar_datos_estudiante
from .pipeline import ejecutar_pipeline_estudiante

__all__ = ["sanitizar_datos_estudiante", "ejecutar_pipeline_estudiante"]
