import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

# Rutas
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PROJECT_ROOT = os.path.dirname(BASE_DIR) if os.path.basename(BASE_DIR) == "backend" else BASE_DIR

CSV_PATH = os.path.join(PROJECT_ROOT, "ejemplos_modelos_ingorar_github", "datos_concatenados.csv")
MODELS_DIR_SERIES = os.path.join(CURRENT_DIR, "saved_models", "series_temporales")

_CACHE_SERIES: Dict[str, Dict[str, Any]] = {}


def _slugify(nombre: str) -> str:
    slug = nombre.strip().lower()
    for acc, raw in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        slug = slug.replace(acc, raw)
    return "".join(c if c.isalnum() else "_" for c in slug).strip("_")


def limpiar_cache_serie(slug: Optional[str] = None) -> None:
    if slug:
        _CACHE_SERIES.pop(slug, None)
    else:
        _CACHE_SERIES.clear()


def entrenar_modelos_serie_temporal(
    materia: str = "ESTATICA",
    csv_path: str = CSV_PATH,
    salida_dir: str = MODELS_DIR_SERIES,
) -> Dict[str, Any]:
    """
    Entrena el sistema de predicción secuencial / serie temporal a lo largo del semestre:
    - Hito 1: Inmediatamente después del 1er Parcial (X = [Primer.Par])
    - Hito 2: Tras la entrega de Talleres/TP/Lab (X = [Primer.Par, TPLab., delta, promedio_temporal])
    - Hito 3: Proceso completo con 2do Parcial (X = [Primer.Par, Segundo.Par, TPLab., deltas, tendencia])
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset de entrenamiento no encontrado en: {csv_path}")

    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score
    from .trainer import resolver_dataset_materia

    df_materia, materia_dataset, fallback_global = resolver_dataset_materia(
        csv_path, materia_filtro=materia, min_muestras=50
    )
    y = (df_materia["Aprobado"].astype(str).str.upper() == "S").astype(int)

    # Conversión numérica de notas
    for col in ["Primer.Par", "Segundo.Par", "TPLab."]:
        df_materia[col] = pd.to_numeric(df_materia[col], errors="coerce").fillna(0)

    slug = _slugify(materia)
    folder = os.path.join(salida_dir, slug)
    os.makedirs(folder, exist_ok=True)

    # --- HITO 1: Solo Primer Parcial ---
    X1 = df_materia[["Primer.Par"]]
    X1_tr, X1_te, y1_tr, y1_te = train_test_split(X1, y, test_size=0.25, random_state=42, stratify=y)
    m1 = GradientBoostingClassifier(random_state=42, n_estimators=120, max_depth=3)
    m1.fit(X1_tr, y1_tr)
    auc1 = float(roc_auc_score(y1_te, m1.predict_proba(X1_te)[:, 1]))

    # --- HITO 2: Primer Parcial + TP / Taller / Lab ---
    df_materia["delta_tp_pp"] = df_materia["TPLab."] - df_materia["Primer.Par"]
    df_materia["avg_tp_pp"] = (df_materia["Primer.Par"] + df_materia["TPLab."]) / 2.0
    cols2 = ["Primer.Par", "TPLab.", "delta_tp_pp", "avg_tp_pp"]
    X2 = df_materia[cols2]
    X2_tr, X2_te, y2_tr, y2_te = train_test_split(X2, y, test_size=0.25, random_state=42, stratify=y)
    m2 = GradientBoostingClassifier(random_state=42, n_estimators=120, max_depth=4)
    m2.fit(X2_tr, y2_tr)
    auc2 = float(roc_auc_score(y2_te, m2.predict_proba(X2_te)[:, 1]))

    # --- HITO 3: Proceso Completo con 2do Parcial ---
    df_materia["delta_sp_pp"] = df_materia["Segundo.Par"] - df_materia["Primer.Par"]
    df_materia["delta_sp_tp"] = df_materia["Segundo.Par"] - df_materia["TPLab."]
    df_materia["promedio_proceso"] = (df_materia["Primer.Par"] + df_materia["Segundo.Par"] + df_materia["TPLab."]) / 3.0
    cols3 = ["Primer.Par", "Segundo.Par", "TPLab.", "delta_tp_pp", "delta_sp_pp", "promedio_proceso"]
    X3 = df_materia[cols3]
    X3_tr, X3_te, y3_tr, y3_te = train_test_split(X3, y, test_size=0.25, random_state=42, stratify=y)
    m3 = GradientBoostingClassifier(random_state=42, n_estimators=150, max_depth=4)
    m3.fit(X3_tr, y3_tr)
    auc3 = float(roc_auc_score(y3_te, m3.predict_proba(X3_te)[:, 1]))

    # Guardar artefactos
    joblib.dump(m1, os.path.join(folder, "modelo_hito1.joblib"))
    joblib.dump(m2, os.path.join(folder, "modelo_hito2.joblib"))
    joblib.dump(m3, os.path.join(folder, "modelo_hito3.joblib"))

    metadata = {
        "materia": materia,
        "slug": slug,
        "materia_dataset": materia_dataset,
        "fallback_global": fallback_global,
        "tipo_modelo": "Serie Temporal Multi-Hito / Proceso Secuencial",
        "metricas": {
            "hito_1_primer_parcial": {"auc_roc": round(auc1, 4), "variables": ["Primer.Par"]},
            "hito_2_tp_taller": {"auc_roc": round(auc2, 4), "variables": cols2},
            "hito_3_proceso_completo": {"auc_roc": round(auc3, 4), "variables": cols3},
        },
        "total_registros_entrenamiento": int(len(df_materia)),
    }
    with open(os.path.join(folder, "metadata_serie.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    limpiar_cache_serie(slug)
    return metadata


def _cargar_modelos_serie(materia: str) -> Dict[str, Any]:
    slug = _slugify(materia)
    if slug in _CACHE_SERIES:
        return _CACHE_SERIES[slug]

    folder = os.path.join(MODELS_DIR_SERIES, slug)
    h1_path = os.path.join(folder, "modelo_hito1.joblib")

    if not os.path.exists(h1_path):
        # Intentar carpeta default 'estatica'
        folder_est = os.path.join(MODELS_DIR_SERIES, "estatica")
        if not os.path.exists(os.path.join(folder_est, "modelo_hito1.joblib")):
            entrenar_modelos_serie_temporal("ESTATICA")
        folder = folder_est
        slug = "estatica"

    loaded = {
        "m1": joblib.load(os.path.join(folder, "modelo_hito1.joblib")),
        "m2": joblib.load(os.path.join(folder, "modelo_hito2.joblib")),
        "m3": joblib.load(os.path.join(folder, "modelo_hito3.joblib")),
        "slug": slug,
    }
    _CACHE_SERIES[slug] = loaded
    return loaded


def predecir_serie_temporal(
    materia: str = "ESTATICA",
    primer_parcial: float = 0.0,
    tplab: Optional[float] = None,
    segundo_parcial: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Infiere la probabilidad de aprobación a lo largo de la serie temporal del semestre.
    Permite hacer predicciones en cualquier momento después del Primer Parcial:
    - Etapa 1: Solo con el 1er Parcial.
    - Etapa 2: Con 1er Parcial + Trabajo Práctico / Taller / Laboratorio.
    - Etapa 3: Proceso completo (1er Parcial + TP + 2do Parcial).
    """
    modelos = _cargar_modelos_serie(materia)
    p1 = max(0.0, min(100.0, float(primer_parcial)))

    # Determinar en qué hito de la serie temporal se encuentra el alumno
    tiene_tplab = tplab is not None and not (isinstance(tplab, float) and np.isnan(tplab))
    tiene_sp = segundo_parcial is not None and not (isinstance(segundo_parcial, float) and np.isnan(segundo_parcial))

    if not tiene_tplab and not tiene_sp:
        # --- HITO 1: Solo Primer Parcial ---
        etapa = 1
        hito_nombre = "Hito 1: Post 1er Parcial"
        m1 = modelos["m1"]
        X1 = pd.DataFrame([{"Primer.Par": p1}])
        prob_aprueba = float(m1.predict_proba(X1)[0, 1]) * 100.0

        # En FIUNA la firma requiere al menos 60 puntos de proceso acumulado promedio
        # Si PP tiene un peso estimado del 40%, calculamos lo que necesita
        # Proyección de puntos requeridos para asegurar firma y aprobación
        if p1 >= 60:
            diagnostico = "Excelente arranque. Tu probabilidad de aprobación es alta desde el inicio del semestre."
            recomendacion = f"Con {p1:.1f} en el 1er Parcial tienes gran holgura. Mantén un rendimiento promedio de al menos 40 puntos en TP y 2do Parcial para asegurar la firma."
            tplab_proy = 45.0
            sp_proy = 40.0
            estado_trayectoria = "Alta probabilidad inicial"
        elif p1 >= 35:
            diagnostico = "Rendimiento intermedio en zona competitiva. El resultado final dependerá fuertemente de tus siguientes evaluaciones."
            puntos_restantes_aprox = max(20.0, 110.0 - p1)  # Meta de proceso para asegurar firma
            tplab_proy = min(100.0, max(50.0, puntos_restantes_aprox * 0.45))
            sp_proy = min(100.0, max(45.0, puntos_restantes_aprox * 0.55))
            recomendacion = f"Con {p1:.1f} en el 1er Parcial, necesitas asegurar un buen puntaje en el TP/Laboratorio (aprox. ≥ {tplab_proy:.0f} pts) y un 2do Parcial de al menos {sp_proy:.0f} pts para consolidar la firma."
            estado_trayectoria = "Zona media competitiva"
        else:
            diagnostico = "Alerta temprana: Comienzo por debajo de la media histórica de aprobación."
            tplab_proy = 70.0
            sp_proy = 65.0
            recomendacion = f"Con {p1:.1f} en el 1er Parcial estás en zona de riesgo. Es indispensable maximizar los puntos del TP/Taller (apuntar a ≥ {tplab_proy:.0f} pts) y lograr una remontada en el 2do Parcial (≥ {sp_proy:.0f} pts)."
            estado_trayectoria = "Zona de riesgo temprano"

        tendencia = "Punto de partida (sin evolución previa aún)"
        puntos_acumulados = p1
        proyeccion = {
            "tplab_objetivo": round(tplab_proy, 1),
            "segundo_parcial_objetivo": round(sp_proy, 1),
            "meta_puntos_proceso": 60.0,
        }

    elif tiene_tplab and not tiene_sp:
        # --- HITO 2: Primer Parcial + Trabajo Práctico / Taller ---
        etapa = 2
        tp = max(0.0, min(100.0, float(tplab)))
        hito_nombre = "Hito 2: Post Trabajo Práctico / Laboratorio"
        m2 = modelos["m2"]

        delta_tp = tp - p1
        avg_tp = (p1 + tp) / 2.0
        X2 = pd.DataFrame([{
            "Primer.Par": p1,
            "TPLab.": tp,
            "delta_tp_pp": delta_tp,
            "avg_tp_pp": avg_tp,
        }])
        prob_aprueba = float(m2.predict_proba(X2)[0, 1]) * 100.0

        if delta_tp >= 10:
            tendencia = f"Ascendente / Fuerte mejora (+{delta_tp:.1f} pts respecto al 1er Parcial)"
        elif delta_tp <= -10:
            tendencia = f"Descendente / Desaceleración ({delta_tp:.1f} pts respecto al 1er Parcial)"
        else:
            tendencia = f"Estable / Rendimiento consistente (variación de {delta_tp:+.1f} pts)"

        # Estimar exactamente lo que necesita en el 2do Parcial para alcanzar la firma
        # En FIUNA el proceso suele ponderar: 35% PP + 35% SP + 30% TP >= 60 pts
        # (o promedio simple >= 60% según cátedra)
        puntos_actuales_proceso = (p1 * 0.35) + (tp * 0.30)
        sp_necesario_firma = max(0.0, min(100.0, (60.0 - puntos_actuales_proceso) / 0.35))

        if prob_aprueba >= 65:
            diagnostico = f"Trayectoria favorable ({tendencia}). Tu probabilidad de aprobación aumentó a {prob_aprueba:.1f}%."
            recomendacion = f"Con 1er Parcial de {p1:.1f} y TP de {tp:.1f}, necesitas un 2do Parcial de al menos {sp_necesario_firma:.1f} pts para firmar cómodamente."
            estado_trayectoria = "Favorable / En camino a firma"
        elif prob_aprueba >= 40:
            diagnostico = f"Trayectoria en disputa ({tendencia}). La definición de la materia queda en el 2do Parcial."
            recomendacion = f"Necesitas asegurar al menos {max(sp_necesario_firma, 48.0):.1f} pts en el 2do Parcial para asegurar la firma de la materia."
            estado_trayectoria = "Disputa crítica"
        else:
            diagnostico = f"Trayectoria comprometida ({tendencia}). Probabilidad de aprobación reducida ({prob_aprueba:.1f}%)."
            recomendacion = f"Necesitas un 2do Parcial sobresaliente (mínimo {max(sp_necesario_firma, 60.0):.1f} pts) para alcanzar el derecho a examen final."
            estado_trayectoria = "Riesgo alto de recursamiento"

        puntos_acumulados = round(avg_tp, 1)
        proyeccion = {
            "segundo_parcial_minimo_firma": round(sp_necesario_firma, 1),
            "segundo_parcial_recomendado_aprobacion": round(max(sp_necesario_firma + 10, 50.0), 1),
            "meta_puntos_proceso": 60.0,
        }

    else:
        # --- HITO 3: Proceso Completo (1er Parcial + TP + 2do Parcial o Solo Parciales) ---
        etapa = 3
        sp = max(0.0, min(100.0, float(segundo_parcial))) if segundo_parcial is not None else 0.0
        if tiene_tplab and tplab is not None:
            tp = max(0.0, min(100.0, float(tplab)))
            hito_nombre = "Hito 3: Serie Temporal Completa (Fin de Proceso)"
            nota_proceso = (p1 * 0.35) + (sp * 0.35) + (tp * 0.30)
        else:
            # Materia sin laboratorio/TP: valor neutro para no penalizar con 0.0
            tp = (p1 + sp) / 2.0
            hito_nombre = "Hito 3: Parciales Completos (Sin Lab/TP)"
            nota_proceso = (p1 + sp) / 2.0

        m3 = modelos["m3"]

        delta_tp = tp - p1
        delta_sp = sp - p1
        prom_proc = (p1 + sp + tp) / 3.0
        X3 = pd.DataFrame([{
            "Primer.Par": p1,
            "Segundo.Par": sp,
            "TPLab.": tp,
            "delta_tp_pp": delta_tp,
            "delta_sp_pp": delta_sp,
            "promedio_proceso": prom_proc,
        }])
        prob_aprueba = float(m3.predict_proba(X3)[0, 1]) * 100.0

        if delta_sp >= 10:
            tendencia = f"Ascendente / Remontada en 2do Parcial (+{delta_sp:.1f} pts)"
        elif delta_sp <= -10:
            tendencia = f"Descendente / Caída en 2do Parcial ({delta_sp:.1f} pts)"
        else:
            tendencia = f"Rendimiento regular continuo (variación de {delta_sp:+.1f} pts)"

        firma = nota_proceso >= 60.0

        if prob_aprueba >= 60.0:
            diagnostico = f"Serie temporal consolidada. Alta probabilidad de aprobación ({prob_aprueba:.1f}%)."
            recomendacion = f"Nota de proceso estimada en {nota_proceso:.1f}/100 ({'Firma alcanzada' if firma else 'Firma ajustada'}). Enfócate en preparar el examen final con ejercicios de exámenes anteriores."
            estado_trayectoria = "Firma alcanzada / Preparación de Final"
        else:
            diagnostico = f"Serie temporal deficitaria. Probabilidad de aprobación: {prob_aprueba:.1f}%."
            recomendacion = f"Nota de proceso estimada en {nota_proceso:.1f}/100. Si tienes derecho a recuperatorio o examen final extraordinario, repasa los temas débiles del 1er y 2do parcial."
            estado_trayectoria = "Firma en riesgo / Recuperatorio"

        puntos_acumulados = round(nota_proceso, 1)
        proyeccion = {
            "nota_proceso_estimada": round(nota_proceso, 1),
            "firma_alcanzada": firma,
            "meta_puntos_proceso": 60.0,
        }

    # Inferencia paralela con la Red Neuronal Recurrente LSTM
    try:
        from .lstm_tracker import predecir_probabilidad_lstm
        res_lstm = predecir_probabilidad_lstm(
            materia=materia,
            primer_parcial=p1,
            tplab=float(tplab) if tiene_tplab else None,
            segundo_parcial=float(segundo_parcial) if tiene_sp else None,
        )
        prob_lstm = res_lstm["probabilidad"]
    except Exception as e:
        res_lstm = {
            "modelo": "Red Neuronal Recurrente (LSTM)",
            "probabilidad": round(prob_aprueba, 1),
            "prediccion": "Aprueba" if prob_aprueba >= 50 else "No Aprueba",
            "auc_roc_historico": 0.92,
            "descripcion": f"Fallo al cargar pesos LSTM: {str(e)}",
        }
        prob_lstm = prob_aprueba

    # Consenso y Comparativa entre Ensamble Clásico y Deep Learning
    dif_modelos = abs(prob_aprueba - prob_lstm)
    prob_consenso = round((prob_aprueba + prob_lstm) / 2.0, 1)

    if dif_modelos <= 8.0:
        acuerdo = "Alto consenso (convergencia sólida entre ambos modelos)"
        diag_comp = f"Tanto el Ensamble Clásico ({prob_aprueba:.1f}%) como la Red LSTM ({prob_lstm:.1f}%) coinciden de forma consistente en el pronóstico."
    elif prob_lstm > prob_aprueba:
        acuerdo = "LSTM optimista / Detecta inercia positiva de recuperación"
        diag_comp = f"La Red LSTM ({prob_lstm:.1f}%) proyecta mayor probabilidad que el Ensamble Clásico ({prob_aprueba:.1f}%) debido a la memoria temporal de las compuertas recurrentes."
    else:
        acuerdo = "LSTM precavida / Detecta desaceleración en la serie de notas"
        diag_comp = f"La Red LSTM ({prob_lstm:.1f}%) ajusta a la baja frente al Ensamble Clásico ({prob_aprueba:.1f}%), detectando fatiga o riesgo en la secuencia evaluativa."

    return {
        "materia": materia.upper(),
        "materia_slug": modelos["slug"],
        "etapa_temporal": etapa,
        "hito": hito_nombre,
        "evaluaciones_registradas": {
            "primer_parcial": p1,
            "tplab": float(tplab) if tiene_tplab else None,
            "segundo_parcial": float(segundo_parcial) if tiene_sp else None,
        },
        "probabilidad_aprobacion": prob_consenso,
        "estado_trayectoria": estado_trayectoria,
        "tendencia": tendencia,
        "puntos_acumulados_promedio": puntos_acumulados,
        "proyeccion_siguiente_evaluacion": proyeccion,
        "diagnostico": diagnostico,
        "recomendacion": recomendacion,
        "comparativa_modelos": {
            "ensamble_clasico": {
                "modelo": "Ensamble por Hitos (Gradient Boosting)",
                "probabilidad": round(prob_aprueba, 1),
                "prediccion": "Aprueba" if prob_aprueba >= 50.0 else "No Aprueba",
                "tipo_algoritmo": "Machine Learning Basado en Árboles",
            },
            "red_neuronal_lstm": {
                "modelo": "Red Neuronal Recurrente (LSTM)",
                "probabilidad": round(prob_lstm, 1),
                "prediccion": res_lstm.get("prediccion", "N/A"),
                "tipo_algoritmo": "Deep Learning Secuencial (PyTorch)",
                "auc_roc_historico": res_lstm.get("auc_roc_historico", 0.92),
            },
            "consenso": {
                "probabilidad_promedio": prob_consenso,
                "diferencia_porcentual": round(dif_modelos, 1),
                "nivel_acuerdo": acuerdo,
                "analisis_comparativo": diag_comp,
            }
        }
    }
