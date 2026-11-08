import os
import json
import joblib
import pandas as pd
from typing import Dict, Any, List, Optional

# Rutas
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PROJECT_ROOT = os.path.dirname(BASE_DIR) if os.path.basename(BASE_DIR) == "backend" else BASE_DIR

MODELS_DIR_PACKAGE = os.path.join(CURRENT_DIR, "saved_models")
MODELS_DIR_PARCIAL_1 = os.path.join(PROJECT_ROOT, "ejemplos_modelos_ingorar_github", "modelos_primer_parcial")
MODELS_DIR_PARCIAL_2 = os.path.join(PROJECT_ROOT, "ejemplos_modelos_ingorar_github", "modelos_segundo_parcial")

_CACHE_MODELOS: Dict[str, Dict[str, Any]] = {}


def _slugify(nombre: str) -> str:
    slug = nombre.strip().lower()
    for acc, raw in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        slug = slug.replace(acc, raw)
    return "".join(c if c.isalnum() else "_" for c in slug).strip("_")


def obtener_modelos_disponibles() -> Dict[str, Any]:
    """
    Lista los modelos serializados disponibles tanto del Primer Parcial
    como del Segundo Parcial (preparado para futuras extensiones).
    """
    modelos_p1 = []
    # Revisar tanto el directorio empaquetado como el directorio de ejemplos
    directorios_p1 = [MODELS_DIR_PACKAGE, MODELS_DIR_PARCIAL_1]
    vistos = set()

    for base_p1 in directorios_p1:
        if os.path.exists(base_p1):
            for entry in os.listdir(base_p1):
                if entry in vistos:
                    continue
                path = os.path.join(base_p1, entry)
                if os.path.isdir(path):
                    meta_file = os.path.join(path, "metadata.json")
                    if os.path.exists(meta_file):
                        try:
                            with open(meta_file, "r", encoding="utf-8") as f:
                                meta = json.load(f)
                                modelos_p1.append(meta)
                                vistos.add(entry)
                        except Exception:
                            modelos_p1.append({"materia_slug": entry, "parcial": "primer_parcial"})
                            vistos.add(entry)

    modelos_p2 = []
    if os.path.exists(MODELS_DIR_PARCIAL_2):
        for entry in os.listdir(MODELS_DIR_PARCIAL_2):
            path = os.path.join(MODELS_DIR_PARCIAL_2, entry)
            if os.path.isdir(path):
                meta_file = os.path.join(path, "metadata.json")
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                            modelos_p2.append(meta)
                    except Exception:
                        modelos_p2.append({"materia_slug": entry, "parcial": "segundo_parcial"})

    return {
        "primer_parcial": modelos_p1,
        "segundo_parcial": modelos_p2,
        "modelos_activos": ["Regresión Logística", "Árbol de Decisión", "Random Forest"],
        "variables_requeridas": ["Primer.Par", "Segundo.Par", "TPLab."]
    }


def _cargar_modelos_materia(materia: str) -> Dict[str, Any]:
    slug = _slugify(materia)
    if slug in _CACHE_MODELOS:
        return _CACHE_MODELOS[slug]

    # 1. Buscar en saved_models interno
    folder = os.path.join(MODELS_DIR_PACKAGE, slug)
    if not os.path.exists(folder):
        # 2. Buscar en carpeta ejemplos_modelos
        folder = os.path.join(MODELS_DIR_PARCIAL_1, slug)

    # 3. Si no existe, intentar fallback a estatica interna
    if not os.path.exists(folder):
        folder = os.path.join(MODELS_DIR_PACKAGE, "estatica")
        if not os.path.exists(folder):
            folder = os.path.join(MODELS_DIR_PARCIAL_1, "estatica")

    # 4. Si aún no existe, entrenar
    if not os.path.exists(folder):
        from .trainer import entrenar_modelos_primer_parcial
        try:
            entrenar_modelos_primer_parcial(materia)
            folder = os.path.join(MODELS_DIR_PARCIAL_1, slug)
        except Exception:
            slug = "estatica"
            entrenar_modelos_primer_parcial("ESTATICA")
            folder = os.path.join(MODELS_DIR_PARCIAL_1, slug)

    lr_path = os.path.join(folder, "logistic_regression.joblib")
    scaler_path = os.path.join(folder, "scaler.joblib")
    dt_path = os.path.join(folder, "decision_tree.joblib")
    rf_path = os.path.join(folder, "random_forest.joblib")

    if not (os.path.exists(lr_path) and os.path.exists(dt_path) and os.path.exists(rf_path)):
        from .trainer import entrenar_modelos_primer_parcial
        entrenar_modelos_primer_parcial(materia)

    loaded = {
        "lr": joblib.load(lr_path),
        "scaler": joblib.load(scaler_path),
        "dt": joblib.load(dt_path),
        "rf": joblib.load(rf_path),
        "slug": slug,
    }
    _CACHE_MODELOS[slug] = loaded
    return loaded


def predecir_aprobacion(
    materia: str = "ESTATICA",
    primer_parcial: float = 0.0,
    segundo_parcial: float = 0.0,
    tplab: float = 0.0,
) -> Dict[str, Any]:
    """
    Ejecuta la inferencia sobre los 3 modelos desarrollados en el Primer Parcial:
    1. Regresión Logística (modelo probabilístico lineal con normalización)
    2. Árbol de Decisión (modelo no lineal basado en reglas jerárquicas)
    3. Random Forest (ensamble de árboles de decisión)

    Devuelve el valor exacto de la probabilidad calculada por cada uno de los 3 modelos,
    así como la media de consenso y el veredicto estimado.
    """
    modelos = _cargar_modelos_materia(materia)

    # DataFrame con nombres de columnas esperadas
    cols = ["Primer.Par", "Segundo.Par", "TPLab."]
    input_df = pd.DataFrame([{
        "Primer.Par": float(primer_parcial),
        "Segundo.Par": float(segundo_parcial),
        "TPLab.": float(tplab)
    }], columns=cols)

    # 1. Regresión Logística (requiere escalar con StandardScaler)
    scaler = modelos["scaler"]
    lr_model = modelos["lr"]
    input_scaled = scaler.transform(input_df)
    proba_lr = float(lr_model.predict_proba(input_scaled)[0, 1])

    # 2. Árbol de Decisión (datos crudos)
    dt_model = modelos["dt"]
    proba_dt = float(dt_model.predict_proba(input_df)[0, 1])

    # 3. Random Forest (datos crudos)
    rf_model = modelos["rf"]
    proba_rf = float(rf_model.predict_proba(input_df)[0, 1])

    # Porcentajes redondeados a 1 decimal
    pct_lr = round(proba_lr * 100, 1)
    pct_dt = round(proba_dt * 100, 1)
    pct_rf = round(proba_rf * 100, 1)
    pct_promedio = round((pct_lr + pct_dt + pct_rf) / 3.0, 1)

    # Veredicto cualitativo
    if pct_promedio >= 70.0:
        diagnostico = "Alta probabilidad de aprobar"
        recomendacion = "Excelente rendimiento en parciales y taller. Mantén el ritmo para asegurar la firma y preparar el examen final."
    elif pct_promedio >= 50.0:
        diagnostico = "Probabilidad moderada de aprobar"
        recomendacion = "Estás en zona de aprobación según la mayoría de los modelos, pero no debes descuidar la preparación del examen final."
    else:
        diagnostico = "Riesgo de no aprobación"
        recomendacion = "Los puntajes actuales sitúan el pronóstico por debajo del umbral de aprobación. Es recomendable reforzar temas clave y maximizar el rendimiento."

    return {
        "materia": materia,
        "materia_modelo": modelos["slug"].upper(),
        "parcial_origen": "primer_parcial",
        "inputs": {
            "primer_parcial": float(primer_parcial),
            "segundo_parcial": float(segundo_parcial),
            "tplab": float(tplab)
        },
        "probabilidades": {
            "regresion_logistica": {
                "nombre": "Regresión Logística",
                "probabilidad": pct_lr,
                "prediccion": "Aprueba" if pct_lr >= 50.0 else "No Aprueba",
                "descripcion": "Modelo lineal probabilístico base"
            },
            "arbol_decision": {
                "nombre": "Árbol de Decisión",
                "probabilidad": pct_dt,
                "prediccion": "Aprueba" if pct_dt >= 50.0 else "No Aprueba",
                "descripcion": "Modelo no lineal jerárquico"
            },
            "random_forest": {
                "nombre": "Random Forest",
                "probabilidad": pct_rf,
                "prediccion": "Aprueba" if pct_rf >= 50.0 else "No Aprueba",
                "descripcion": "Ensamble de 200 árboles de decisión"
            }
        },
        "resumen": {
            "probabilidad_promedio": pct_promedio,
            "diagnostico": diagnostico,
            "recomendacion": recomendacion
        }
    }

