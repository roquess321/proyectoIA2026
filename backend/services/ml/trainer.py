import os
import json
import joblib
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, precision_score, recall_score, f1_score

# Rutas base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(BASE_DIR) if os.path.basename(BASE_DIR) == "backend" else BASE_DIR

CSV_PATH = os.path.join(PROJECT_ROOT, "ejemplos_modelos_ingorar_github", "datos_concatenados.csv")
MODELS_DIR_PARCIAL_1 = os.path.join(PROJECT_ROOT, "ejemplos_modelos_ingorar_github", "modelos_primer_parcial")
MODELS_DIR_PARCIAL_2 = os.path.join(PROJECT_ROOT, "ejemplos_modelos_ingorar_github", "modelos_segundo_parcial")

VARIABLES_ENTRADA = ["Primer.Par", "Segundo.Par", "TPLab."]


def normalizar_slug(nombre: str) -> str:
    """Convierte el nombre de la materia en un slug seguro para carpetas."""
    slug = nombre.strip().lower()
    for acc, raw in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        slug = slug.replace(acc, raw)
    return "".join(c if c.isalnum() else "_" for c in slug).strip("_")


def cargar_y_limpiar_datos(csv_path: str = CSV_PATH, materia_filtro: str = "ESTATICA") -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el dataset en: {csv_path}")

    df = pd.read_csv(csv_path)

    # Filtrar por materia si se especifica
    if materia_filtro:
        mask = df["Asignatura"].str.upper().str.contains(materia_filtro.upper(), na=False)
        df_materia = df[mask].copy()
        if len(df_materia) < 30:
            # Fallback a todas si hay muy pocos registros
            df_materia = df.copy()
    else:
        df_materia = df.copy()

    df_modelo = df_materia[VARIABLES_ENTRADA].copy()
    df_modelo["Aprobado"] = df_materia["Aprobado"].map({"S": 1, "N": 0})

    for col in VARIABLES_ENTRADA:
        df_modelo[col] = pd.to_numeric(df_modelo[col], errors="coerce")

    df_limpio = df_modelo.dropna().copy()
    return df_limpio, df_materia


def evaluar_modelo(nombre: str, modelo, X_test, y_test) -> Dict[str, float]:
    y_pred = modelo.predict(X_test)
    y_proba = modelo.predict_proba(X_test)[:, 1] if hasattr(modelo, "predict_proba") else None
    
    return {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "auc_roc": round(float(roc_auc_score(y_test, y_proba)), 4) if y_proba is not None else 0.0,
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
    }


def entrenar_modelos_primer_parcial(
    materia: str = "ESTATICA",
    salida_dir: str = MODELS_DIR_PARCIAL_1
) -> Dict[str, Any]:
    """
    Entrena los 3 modelos desarrollados en el Primer Parcial:
    1. Regresión Logística (con StandardScaler)
    2. Árbol de Decisión
    3. Random Forest
    y guarda los artefactos en disco.
    """
    print(f"🔄 Iniciando entrenamiento de modelos de 1er Parcial para: {materia}")
    df_limpio, _ = cargar_y_limpiar_datos(CSV_PATH, materia_filtro=materia)
    
    X = df_limpio[VARIABLES_ENTRADA]
    y = df_limpio["Aprobado"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # 1. Scaler y Regresión Logística
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    lr_model = LogisticRegression(random_state=42, max_iter=1000, class_weight="balanced")
    lr_model.fit(X_train_s, y_train)
    lr_metrics = evaluar_modelo("Regresión Logística", lr_model, X_test_s, y_test)

    # 2. Árbol de Decisión
    dt_model = DecisionTreeClassifier(
        max_depth=6, min_samples_leaf=10, class_weight="balanced", random_state=42
    )
    dt_model.fit(X_train, y_train)
    dt_metrics = evaluar_modelo("Árbol de Decisión", dt_model, X_test, y_test)

    # 3. Random Forest
    rf_model = RandomForestClassifier(
        n_estimators=200, max_depth=6, min_samples_leaf=10, class_weight="balanced", random_state=42, n_jobs=-1
    )
    rf_model.fit(X_train, y_train)
    rf_metrics = evaluar_modelo("Random Forest", rf_model, X_test, y_test)

    # Preparar directorio de guardado
    materia_slug = normalizar_slug(materia)
    target_folder = os.path.join(salida_dir, materia_slug)
    os.makedirs(target_folder, exist_ok=True)
    os.makedirs(MODELS_DIR_PARCIAL_2, exist_ok=True)  # Crear carpeta vacía preparada para 2do parcial

    # Guardar artefactos con joblib
    joblib.dump(lr_model, os.path.join(target_folder, "logistic_regression.joblib"))
    joblib.dump(scaler, os.path.join(target_folder, "scaler.joblib"))
    joblib.dump(dt_model, os.path.join(target_folder, "decision_tree.joblib"))
    joblib.dump(rf_model, os.path.join(target_folder, "random_forest.joblib"))

    metadata = {
        "materia": materia,
        "materia_slug": materia_slug,
        "parcial_origen": "primer_parcial",
        "total_muestras": len(df_limpio),
        "tasa_aprobacion_real": round(float(y.mean()), 4),
        "variables": VARIABLES_ENTRADA,
        "metricas": {
            "regresion_logistica": lr_metrics,
            "arbol_decision": dt_metrics,
            "random_forest": rf_metrics,
        }
    }

    with open(os.path.join(target_folder, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"✅ Modelos del 1er Parcial guardados exitosamente en: {target_folder}")
    print(f"📊 Métricas:")
    print(f"   - Regresión Logística : Acc={lr_metrics['accuracy']}, AUC={lr_metrics['auc_roc']}")
    print(f"   - Árbol de Decisión   : Acc={dt_metrics['accuracy']}, AUC={dt_metrics['auc_roc']}")
    print(f"   - Random Forest       : Acc={rf_metrics['accuracy']}, AUC={rf_metrics['auc_roc']}")

    return metadata


if __name__ == "__main__":
    entrenar_modelos_primer_parcial("ESTATICA")

