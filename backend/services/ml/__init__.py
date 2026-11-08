"""
Módulo de Machine Learning para predicción de aprobación académica.
Integra los modelos desarrollados en el Primer Parcial (y extensible al Segundo Parcial).
"""
from .predictor import predecir_aprobacion, obtener_modelos_disponibles

__all__ = ["predecir_aprobacion", "obtener_modelos_disponibles"]

