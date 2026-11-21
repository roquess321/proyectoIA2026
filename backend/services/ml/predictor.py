import os
import json
import threading
import time
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
_RETRAIN_LOCK = threading.Lock()


def limpiar_cache_modelos(slug: Optional[str] = None) -> None:
    if slug:
        _CACHE_MODELOS.pop(slug, None)
    else:
        _CACHE_MODELOS.clear()


def reentrenar_modelos_materia(materia: str) -> Dict[str, Any]:
    """
    Reentrena los 5 modelos (3 clásicos + Serie Temporal GB + Red Neuronal LSTM)
    filtrando el dataset histórico por la materia solicitada (con fallback global
    si no existen suficientes registros históricos para esa asignatura).
    """
    materia_clean = materia.strip() if materia and materia.strip() else "ESTATICA"
    slug = _slugify(materia_clean) or "estatica"

    with _RETRAIN_LOCK:
        t0 = time.perf_counter()
        from .trainer import entrenar_modelos_primer_parcial
        from .sequential_tracker import entrenar_modelos_serie_temporal, limpiar_cache_serie
        from .lstm_tracker import entrenar_modelo_lstm, limpiar_cache_lstm

        meta_clasico = entrenar_modelos_primer_parcial(
            materia=materia_clean,
            salida_dir=MODELS_DIR_PACKAGE,
        )
        meta_serie = entrenar_modelos_serie_temporal(materia=materia_clean)
        meta_lstm = entrenar_modelo_lstm(materia=materia_clean)

        limpiar_cache_modelos(slug)
        limpiar_cache_serie(slug)
        limpiar_cache_lstm(slug)

        duracion_seg = round(time.perf_counter() - t0, 2)

        auc_gb_h3 = (
            meta_serie.get("metricas", {})
            .get("hito_3_proceso_completo", {})
            .get("auc_roc", 0.0)
        )
        auc_lstm_h3 = (
            meta_lstm.get("metricas_por_hito", {})
            .get("hito_3_proceso_completo", {})
            .get("auc_roc", 0.0)
        )
        auc_rf = (
            meta_clasico.get("metricas", {})
            .get("random_forest", {})
            .get("auc_roc", 0.0)
        )

        return {
            "ok": True,
            "materia": materia_clean,
            "materia_slug": slug,
            "materia_dataset": meta_clasico.get("materia_dataset", materia_clean),
            "fallback_global": bool(meta_clasico.get("fallback_global", False)),
            "total_muestras": int(meta_clasico.get("total_muestras", 0)),
            "duracion_seg": duracion_seg,
            "metricas": {
                "tasa_aprobacion_real": meta_clasico.get("tasa_aprobacion_real", 0.0),
                "clasicos": meta_clasico.get("metricas", {}),
                "serie_temporal_hitos": meta_serie.get("metricas", {}),
                "lstm_hitos": meta_lstm.get("metricas_por_hito", {}),
                "serie_temporal_auc_h3": auc_gb_h3,
                "lstm_auc_h3": auc_lstm_h3,
                "random_forest_auc": auc_rf,
            },
            "mensaje": (
                f"Modelos reentrenados en {duracion_seg}s usando "
                f"{meta_clasico.get('total_muestras', 0)} registros de "
                f"{meta_clasico.get('materia_dataset', materia_clean)}."
            ),
        }


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

    modelos_series = []
    dir_series = os.path.join(MODELS_DIR_PACKAGE, "series_temporales")
    if os.path.exists(dir_series):
        for entry in os.listdir(dir_series):
            path = os.path.join(dir_series, entry)
            if os.path.isdir(path):
                meta_file = os.path.join(path, "metadata_serie.json")
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            modelos_series.append(json.load(f))
                    except Exception:
                        pass

    modelos_lstm = []
    dir_lstm = os.path.join(MODELS_DIR_PACKAGE, "lstm")
    if os.path.exists(dir_lstm):
        for entry in os.listdir(dir_lstm):
            path = os.path.join(dir_lstm, entry)
            if os.path.isdir(path):
                meta_file = os.path.join(path, "metadata_lstm.json")
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            modelos_lstm.append(json.load(f))
                    except Exception:
                        pass

    return {
        "primer_parcial": modelos_p1,
        "segundo_parcial": modelos_p2,
        "series_temporales": {
            "ensamble_clasico": modelos_series,
            "red_neuronal_lstm": modelos_lstm,
        },
        "modelos_activos": [
            "Regresión Logística (1er Parcial)",
            "Árbol de Decisión (1er Parcial)",
            "Random Forest (1er Parcial)",
            "Ensamble Temporal por Hitos (Gradient Boosting)",
            "Red Neuronal Recurrente LSTM (PyTorch Deep Learning)",
        ],
        "variables_requeridas": {
            "estatico": ["Primer.Par", "Segundo.Par", "TPLab."],
            "serie_temporal": ["Primer.Par", "TPLab (opcional)", "Segundo.Par (opcional)"]
        }
    }


def _cargar_modelos_materia(materia: str) -> Dict[str, Any]:
    slug = _slugify(materia)
    if slug in _CACHE_MODELOS:
        return _CACHE_MODELOS[slug]

    slug_efectivo = slug
    # 1. Buscar en saved_models interno
    folder = os.path.join(MODELS_DIR_PACKAGE, slug)
    if not os.path.exists(folder):
        # 2. Buscar en carpeta ejemplos_modelos
        folder = os.path.join(MODELS_DIR_PARCIAL_1, slug)

    # 3. Si no existe, intentar fallback a estatica interna
    if not os.path.exists(folder):
        slug_efectivo = "estatica"
        folder = os.path.join(MODELS_DIR_PACKAGE, "estatica")
        if not os.path.exists(folder):
            folder = os.path.join(MODELS_DIR_PARCIAL_1, "estatica")

    # 4. Si aún no existe, entrenar
    if not os.path.exists(folder):
        from .trainer import entrenar_modelos_primer_parcial
        try:
            entrenar_modelos_primer_parcial(materia, salida_dir=MODELS_DIR_PACKAGE)
            folder = os.path.join(MODELS_DIR_PACKAGE, slug)
            slug_efectivo = slug
        except Exception:
            slug_efectivo = "estatica"
            entrenar_modelos_primer_parcial("ESTATICA", salida_dir=MODELS_DIR_PACKAGE)
            folder = os.path.join(MODELS_DIR_PACKAGE, "estatica")

    lr_path = os.path.join(folder, "logistic_regression.joblib")
    scaler_path = os.path.join(folder, "scaler.joblib")
    dt_path = os.path.join(folder, "decision_tree.joblib")
    rf_path = os.path.join(folder, "random_forest.joblib")

    if not (os.path.exists(lr_path) and os.path.exists(dt_path) and os.path.exists(rf_path)):
        from .trainer import entrenar_modelos_primer_parcial
        entrenar_modelos_primer_parcial(materia, salida_dir=MODELS_DIR_PACKAGE)
        folder = os.path.join(MODELS_DIR_PACKAGE, slug)
        slug_efectivo = slug
        lr_path = os.path.join(folder, "logistic_regression.joblib")
        scaler_path = os.path.join(folder, "scaler.joblib")
        dt_path = os.path.join(folder, "decision_tree.joblib")
        rf_path = os.path.join(folder, "random_forest.joblib")

    loaded = {
        "lr": joblib.load(lr_path),
        "scaler": joblib.load(scaler_path),
        "dt": joblib.load(dt_path),
        "rf": joblib.load(rf_path),
        "slug": slug_efectivo,
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

    # Porcentajes de los 3 modelos clásicos
    pct_lr = round(proba_lr * 100, 1)
    pct_dt = round(proba_dt * 100, 1)
    pct_rf = round(proba_rf * 100, 1)
    pct_clasico = round((pct_lr + pct_dt + pct_rf) / 3.0, 1)

    # 4. Inferencia con los Modelos de Serie Temporal (Ensamble Temporal + Red Neuronal LSTM)
    res_temporal = None
    pct_temporal_gb = None
    pct_lstm = None
    try:
        from .sequential_tracker import predecir_serie_temporal
        res_temporal = predecir_serie_temporal(
            materia=materia,
            primer_parcial=float(primer_parcial),
            tplab=float(tplab),
            segundo_parcial=float(segundo_parcial),
        )
        comp = res_temporal.get("comparativa_modelos", {})
        pct_temporal_gb = comp.get("ensamble_clasico", {}).get("probabilidad")
        pct_lstm = comp.get("red_neuronal_lstm", {}).get("probabilidad")
    except Exception as e:
        print(f"Aviso: no se pudo calcular inferencia temporal completa: {e}")

    # Calcular consenso global con todos los modelos disponibles
    todos_porcentajes = [pct_lr, pct_dt, pct_rf]
    if pct_temporal_gb is not None:
        todos_porcentajes.append(pct_temporal_gb)
    if pct_lstm is not None:
        todos_porcentajes.append(pct_lstm)

    pct_promedio = round(sum(todos_porcentajes) / len(todos_porcentajes), 1)
    pct_temporal_avg = res_temporal.get("probabilidad_aprobacion") if res_temporal else None

    # Veredicto cualitativo enriquecido con la trayectoria temporal
    tendencia_str = f" con tendencia {res_temporal['tendencia'].lower()}" if res_temporal and "tendencia" in res_temporal else ""

    if pct_promedio >= 70.0:
        diagnostico = f"Alta probabilidad de aprobar{tendencia_str}"
        recomendacion = "Excelente rendimiento en todas las evaluaciones de proceso. Mantén el ritmo para asegurar una calificación sobresaliente en el examen final."
    elif pct_promedio >= 50.0:
        diagnostico = f"Probabilidad moderada de aprobar{tendencia_str}"
        recomendacion = "Estás en zona de aprobación según el consenso de modelos clásicos y la serie temporal, pero debes consolidar los temas débiles para el examen final."
    else:
        diagnostico = f"Riesgo de no aprobación{tendencia_str}"
        recomendacion = "Los puntajes actuales sitúan el pronóstico en zona de riesgo. Es indispensable maximizar el puntaje en el examen final o recurrir a los periodos extraordinarios/recuperatorios."

    probabilidades_dict: Dict[str, Any] = {
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
    }

    if pct_temporal_gb is not None:
        probabilidades_dict["ensamble_temporal_gb"] = {
            "nombre": "Ensamble Temporal (Gradient Boosting)",
            "probabilidad": pct_temporal_gb,
            "prediccion": "Aprueba" if pct_temporal_gb >= 50.0 else "No Aprueba",
            "descripcion": "Modelo de serie temporal por etapas y deltas dinámicos"
        }

    if pct_lstm is not None:
        probabilidades_dict["red_neuronal_lstm"] = {
            "nombre": "Red Neuronal Recurrente (LSTM)",
            "probabilidad": pct_lstm,
            "prediccion": "Aprueba" if pct_lstm >= 50.0 else "No Aprueba",
            "descripcion": "Deep Learning recurrente con compuertas de memoria (PyTorch)"
        }

    resumen_dict: Dict[str, Any] = {
        "probabilidad_promedio": pct_promedio,
        "diagnostico": diagnostico,
        "recomendacion": recomendacion,
        "probabilidad_modelos_clasicos": pct_clasico,
        "probabilidad_modelos_temporales": pct_temporal_avg,
    }

    if res_temporal:
        resumen_dict["analisis_serie_temporal"] = {
            "tendencia": res_temporal.get("tendencia"),
            "estado_trayectoria": res_temporal.get("estado_trayectoria"),
            "puntos_acumulados_promedio": res_temporal.get("puntos_acumulados_promedio"),
            "proyeccion_siguiente_evaluacion": res_temporal.get("proyeccion_siguiente_evaluacion"),
            "comparativa": res_temporal.get("comparativa_modelos", {}).get("consenso")
        }

    return {
        "materia": materia,
        "materia_modelo": modelos["slug"].upper(),
        "parcial_origen": "proceso_completo",
        "inputs": {
            "primer_parcial": float(primer_parcial),
            "segundo_parcial": float(segundo_parcial),
            "tplab": float(tplab)
        },
        "probabilidades": probabilidades_dict,
        "resumen": resumen_dict
    }

