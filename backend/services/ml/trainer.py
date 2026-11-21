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
MODELS_DIR_SAVED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")
MODELS_DIR_PARCIAL_1 = os.path.join(PROJECT_ROOT, "ejemplos_modelos_ingorar_github", "modelos_primer_parcial")
MODELS_DIR_PARCIAL_2 = os.path.join(PROJECT_ROOT, "ejemplos_modelos_ingorar_github", "modelos_segundo_parcial")

VARIABLES_ENTRADA = ["Primer.Par", "Segundo.Par", "TPLab."]


def _quitar_acentos(texto: str) -> str:
    res = texto.strip().upper()
    for acc, raw in [("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"), ("Ñ", "N")]:
        res = res.replace(acc, raw)
    return " ".join(res.split())


def normalizar_slug(nombre: str) -> str:
    """Convierte el nombre de la materia en un slug seguro para carpetas."""
    slug = nombre.strip().lower()
    for acc, raw in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        slug = slug.replace(acc, raw)
    return "".join(c if c.isalnum() else "_" for c in slug).strip("_")


def resolver_dataset_materia(
    csv_path: str = CSV_PATH,
    materia_filtro: str = "ESTATICA",
    min_muestras: int = 60,
    min_por_clase: int = 20,
) -> Tuple[pd.DataFrame, str, bool]:
    """
    Carga el CSV histórico, elimina filas duplicadas (ignorando ALUMNO_ID para evitar Data Leakage
    entre Train y Test), unifica TPLab./Lab. y resuelve el subconjunto de la asignatura.
    Si la asignatura no alcanza el mínimo estadístico por clase (ej. < 20 aprobados o < 20 reprobados),
    conserva sus registros propios y los complementa con una muestra estratificada de su misma
    carrera (o cohorte global FIUNA).
    Retorna: (df_filtrado, nombre_dataset_resuelto, fallback_global).
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No se encontró el dataset en: {csv_path}")

    df = pd.read_csv(csv_path, low_memory=False)
    df = df.dropna(subset=["Aprobado"]).copy()
    df["Aprobado"] = df["Aprobado"].astype(str).str.upper().str.strip()
    df = df[df["Aprobado"].isin(["S", "N"])].copy()

    # 1. Deduplicación estricta ignorando ALUMNO_ID para eliminar clones entre Train y Test
    cols_dedup = [c for c in df.columns if c != "ALUMNO_ID"]
    df = df.drop_duplicates(subset=cols_dedup).copy()

    # 2. Conversión numérica y fusión de Lab. en TPLab. cuando TPLab. sea 0
    for col in ["Primer.Par", "Segundo.Par", "TPLab."]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    if "Lab." in df.columns:
        lab_col = pd.to_numeric(df["Lab."], errors="coerce").fillna(0.0)
        df["TPLab."] = df["TPLab."].where(df["TPLab."] > 0, lab_col)

    if not materia_filtro or not materia_filtro.strip():
        return df, "Cohorte Global FIUNA (Deduplicada)", True

    target_norm = _quitar_acentos(materia_filtro)
    asig_norm = df["Asignatura"].astype(str).map(_quitar_acentos)

    # Búsqueda jerárquica de la asignatura
    mask = asig_norm == target_norm
    matched_name = target_norm

    if int(mask.sum()) == 0:
        mask_contains = asig_norm.str.contains(target_norm, regex=False, na=False)
        if int(mask_contains.sum()) > 0:
            mask = mask_contains

    if int(mask.sum()) == 0:
        unicas = sorted(
            {u for u in asig_norm.unique() if u and u != "NAN"},
            key=len,
            reverse=True,
        )
        for cand in unicas:
            if len(cand) >= 5 and cand in target_norm:
                cand_mask = asig_norm == cand
                if int(cand_mask.sum()) > 0:
                    mask = cand_mask
                    matched_name = cand
                    break

    if int(mask.sum()) == 0:
        stopwords = {"PARA", "INGENIERIA", "GENERAL", "APLICADA", "BASICA", "TECNICA"}
        tokens = [t for t in target_norm.split() if len(t) >= 5 and t not in stopwords]
        for tok in tokens:
            tok_mask = asig_norm.str.contains(tok, regex=False, na=False)
            if int(tok_mask.sum()) > 0:
                mask = tok_mask
                matched_name = tok
                break

    df_propios = df[mask].copy()
    n_propios = len(df_propios)

    if n_propios > 0:
        top_vals = df.loc[mask, "Asignatura"].dropna().astype(str).value_counts()
        if not top_vals.empty and len(top_vals) <= 3:
            matched_name = str(top_vals.index[0])

    n_s = int((df_propios["Aprobado"] == "S").sum()) if n_propios > 0 else 0
    n_n = int((df_propios["Aprobado"] == "N").sum()) if n_propios > 0 else 0

    # Caso A: La materia cumple el mínimo total y el mínimo por clase (S y N)
    if n_propios >= min_muestras and n_s >= min_por_clase and n_n >= min_por_clase:
        return df_propios, matched_name, False

    # Caso B: Muestra propia insuficiente en alguna clase -> complementar con cohorte de carrera / FIUNA
    if n_propios > 0:
        carrera_principal = "FIUNA"
        pool = df[~mask].copy()
        if "Carrera" in df_propios.columns:
            modas = df_propios["Carrera"].dropna().astype(str).str.strip()
            modas = modas[modas != ""]
            if not modas.empty:
                cand_carrera = str(modas.mode().iloc[0])
                pool_carrera = df[(df["Carrera"].astype(str).str.strip() == cand_carrera) & (~mask)].copy()
                c_s = int((pool_carrera["Aprobado"] == "S").sum())
                c_n = int((pool_carrera["Aprobado"] == "N").sum())
                if len(pool_carrera) >= 120 and c_s >= 40 and c_n >= 40:
                    pool = pool_carrera
                    carrera_principal = f"Carrera {cand_carrera}"

        # Muestreo estratificado de complemento (~360 registros de la cohorte)
        n_comp = min(360, len(pool))
        if n_comp > 20 and pool["Aprobado"].nunique() == 2:
            df_comp, _ = train_test_split(
                pool,
                train_size=n_comp,
                random_state=42,
                stratify=pool["Aprobado"],
            )
            df_combinado = pd.concat([df_propios, df_comp], ignore_index=True)
        else:
            df_combinado = pd.concat([df_propios, pool], ignore_index=True)

        etiqueta = (
            f"{matched_name} ({n_propios} únicos: {n_s}S/{n_n}N) + "
            f"Cohorte {carrera_principal}"
        )
        return df_combinado, etiqueta, True

    # Caso C: 0 registros propios -> cohorte global deduplicada
    return df, "Cohorte Global FIUNA (Deduplicada)", True


def cargar_y_limpiar_datos(csv_path: str = CSV_PATH, materia_filtro: str = "ESTATICA") -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_materia, _, _ = resolver_dataset_materia(csv_path, materia_filtro=materia_filtro, min_muestras=30)

    df_modelo = df_materia[VARIABLES_ENTRADA].copy()
    df_modelo["Aprobado"] = df_materia["Aprobado"].astype(str).str.upper().map({"S": 1, "N": 0})

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
    salida_dir: str = MODELS_DIR_SAVED
) -> Dict[str, Any]:
    """
    Entrena los 3 modelos desarrollados en el Primer Parcial:
    1. Regresión Logística (con StandardScaler)
    2. Árbol de Decisión
    3. Random Forest
    y guarda los artefactos en disco.
    """
    print(f"🔄 Iniciando entrenamiento de modelos clásicos para: {materia}")
    df_materia, materia_dataset, fallback_global = resolver_dataset_materia(
        CSV_PATH, materia_filtro=materia, min_muestras=30
    )

    df_modelo = df_materia[VARIABLES_ENTRADA].copy()
    df_modelo["Aprobado"] = df_materia["Aprobado"].astype(str).str.upper().map({"S": 1, "N": 0})
    for col in VARIABLES_ENTRADA:
        df_modelo[col] = pd.to_numeric(df_modelo[col], errors="coerce")
    df_limpio = df_modelo.dropna().copy()
    
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
        "materia_dataset": materia_dataset,
        "fallback_global": fallback_global,
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

