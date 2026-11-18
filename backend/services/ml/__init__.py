"""
Módulo de Machine Learning para predicción de aprobación académica.
Integra:
1. Modelos estáticos del 1er y 2do Parcial (Regresión Logística, Árbol de Decisión, Random Forest).
2. Modelo dinámico de Serie Temporal Multi-Hito (predicción progresiva en cualquier momento tras el 1er Parcial).
"""
from .predictor import predecir_aprobacion, obtener_modelos_disponibles
from .sequential_tracker import predecir_serie_temporal, entrenar_modelos_serie_temporal
from .lstm_tracker import predecir_probabilidad_lstm, entrenar_modelo_lstm

__all__ = [
    "predecir_aprobacion",
    "obtener_modelos_disponibles",
    "predecir_serie_temporal",
    "entrenar_modelos_serie_temporal",
    "predecir_probabilidad_lstm",
    "entrenar_modelo_lstm",
]


