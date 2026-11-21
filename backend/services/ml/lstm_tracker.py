import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score

# Rutas
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
PROJECT_ROOT = os.path.dirname(BASE_DIR) if os.path.basename(BASE_DIR) == "backend" else BASE_DIR

from .trainer import CSV_PATH, CSV_PATH_COMPACT
MODELS_DIR_LSTM = os.path.join(CURRENT_DIR, "saved_models", "lstm")

_CACHE_LSTM: Dict[str, Any] = {}


def _slugify(nombre: str) -> str:
    slug = nombre.strip().lower()
    for acc, raw in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        slug = slug.replace(acc, raw)
    return "".join(c if c.isalnum() else "_" for c in slug).strip("_")


class AcademicLSTM(nn.Module):
    """
    Red Neuronal Recurrente LSTM para modelar la serie temporal de evaluaciones.
    Capas:
    1. LSTM bidireccional / apilada con 2 capas (hidden_size=32).
    2. Regularización mediante Dropout (0.2).
    3. Capa Densa Intermedia (32 -> 16 con ReLU).
    4. Capa de Salida de Clasificación (16 -> 1 con Sigmoid).
    """
    def __init__(self, input_size: int = 4, hidden_size: int = 32, num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 16),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(16, 1),
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        # x shape: [batch_size, seq_len, input_size]
        out, (hn, cn) = self.lstm(x)
        # Tomar el último estado oculto de la secuencia temporal: out[:, -1, :]
        last_hidden = out[:, -1, :]
        logits = self.fc(last_hidden)
        return logits, last_hidden


def _construir_secuencias_estudiante(df: pd.DataFrame) -> Tuple[list, list, list]:
    """
    Convierte cada registro de estudiante en 3 muestras de secuencia temporal:
    - Longitud 1: [Hito 1: Primer Parcial]
    - Longitud 2: [Hito 1: Primer Parcial, Hito 2: TPLab]
    - Longitud 3: [Hito 1: Primer Parcial, Hito 2: TPLab, Hito 3: Segundo Parcial]
    """
    seqs_1 = []
    seqs_2 = []
    seqs_3 = []
    labels = []

    for _, row in df.iterrows():
        p1 = float(row["Primer.Par"])
        sp = float(row["Segundo.Par"])
        tp = float(row["TPLab."])
        y = float(row["target"])

        # Características por paso: [nota/100, prom_acum/100, delta/100, paso_norm]
        step1 = [p1 / 100.0, p1 / 100.0, 0.0, 1.0 / 3.0]
        step2 = [tp / 100.0, ((p1 + tp) / 2.0) / 100.0, (tp - p1) / 100.0, 2.0 / 3.0]
        step3 = [sp / 100.0, ((p1 + tp + sp) / 3.0) / 100.0, (sp - tp) / 100.0, 3.0 / 3.0]

        seqs_1.append([step1])
        seqs_2.append([step1, step2])
        seqs_3.append([step1, step2, step3])
        labels.append(y)

    return seqs_1, seqs_2, seqs_3, labels


def limpiar_cache_lstm(slug: Optional[str] = None) -> None:
    if slug:
        _CACHE_LSTM.pop(slug, None)
    else:
        _CACHE_LSTM.clear()


def entrenar_modelo_lstm(
    materia: str = "ESTATICA",
    csv_path: str = CSV_PATH,
    salida_dir: str = MODELS_DIR_LSTM,
    epochs: int = 40,
    lr: float = 0.003,
) -> Dict[str, Any]:
    """
    Entrena la Red Neuronal Recurrente LSTM con los datos históricos de FIUNA.
    Aprende a mapear secuencias de evaluaciones de longitud variable a la probabilidad de aprobación.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset de entrenamiento no encontrado en: {csv_path}")

    from .trainer import resolver_dataset_materia

    torch.manual_seed(42)
    np.random.seed(42)

    df_materia, materia_dataset, fallback_global = resolver_dataset_materia(
        csv_path, materia_filtro=materia, min_muestras=50
    )
    df_materia["target"] = (df_materia["Aprobado"].astype(str).str.upper() == "S").astype(float)

    if len(df_materia) > 6000:
        df_materia, _ = train_test_split(
            df_materia,
            train_size=6000,
            random_state=42,
            stratify=df_materia["target"],
        )
        df_materia = df_materia.copy()

    effective_epochs = 28 if len(df_materia) > 3000 else epochs

    for col in ["Primer.Par", "Segundo.Par", "TPLab."]:
        df_materia[col] = pd.to_numeric(df_materia[col], errors="coerce").fillna(0)

    # Train / Test split a nivel de estudiantes para evitar data leakage
    df_train, df_test = train_test_split(df_materia, test_size=0.25, random_state=42, stratify=df_materia["target"])

    tr1, tr2, tr3, y_tr = _construir_secuencias_estudiante(df_train)
    te1, te2, te3, y_te = _construir_secuencias_estudiante(df_test)

    # Balanceo de clases para el desbalance histórico de FIUNA (~29% aprobados)
    pos_count = sum(y_tr)
    neg_count = len(y_tr) - pos_count
    pos_weight = torch.tensor([neg_count / max(pos_count, 1.0)], dtype=torch.float32)

    model = AcademicLSTM(input_size=4, hidden_size=32, num_layers=2, dropout=0.2)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    # Convertir a Tensores PyTorch
    X_tr1 = torch.tensor(tr1, dtype=torch.float32)
    X_tr2 = torch.tensor(tr2, dtype=torch.float32)
    X_tr3 = torch.tensor(tr3, dtype=torch.float32)
    y_tr_tensor = torch.tensor(y_tr, dtype=torch.float32).unsqueeze(1)

    X_te1 = torch.tensor(te1, dtype=torch.float32)
    X_te2 = torch.tensor(te2, dtype=torch.float32)
    X_te3 = torch.tensor(te3, dtype=torch.float32)
    y_te_np = np.array(y_te)

    # Ciclo de entrenamiento (Multi-Horizon Sequence Training)
    model.train()
    for epoch in range(effective_epochs):
        # Paso en secuencias completas (Hito 3)
        optimizer.zero_grad()
        logits3, _ = model(X_tr3)
        loss3 = criterion(logits3, y_tr_tensor)
        
        # Paso en secuencias intermedias (Hito 2)
        logits2, _ = model(X_tr2)
        loss2 = criterion(logits2, y_tr_tensor)

        # Paso en secuencias tempranas (Hito 1)
        logits1, _ = model(X_tr1)
        loss1 = criterion(logits1, y_tr_tensor)

        # Pérdida total multi-horizonte (pesando más el proceso avanzado pero obligando a aprender temprano)
        total_loss = 0.25 * loss1 + 0.35 * loss2 + 0.40 * loss3
        total_loss.backward()
        optimizer.step()

    # Evaluación en Test Set para cada horizonte temporal
    model.eval()
    with torch.no_grad():
        l1_te, _ = model(X_te1)
        l2_te, _ = model(X_te2)
        l3_te, _ = model(X_te3)

        p1_te = torch.sigmoid(l1_te).squeeze().numpy()
        p2_te = torch.sigmoid(l2_te).squeeze().numpy()
        p3_te = torch.sigmoid(l3_te).squeeze().numpy()

        auc_h1 = float(roc_auc_score(y_te_np, p1_te))
        auc_h2 = float(roc_auc_score(y_te_np, p2_te))
        auc_h3 = float(roc_auc_score(y_te_np, p3_te))
        acc_h3 = float(accuracy_score(y_te_np, (p3_te >= 0.5).astype(int)))
        f1_h3 = float(f1_score(y_te_np, (p3_te >= 0.5).astype(int), zero_division=0))

    # Guardar artefactos
    slug = _slugify(materia)
    folder = os.path.join(salida_dir, slug)
    os.makedirs(folder, exist_ok=True)

    weights_path = os.path.join(folder, "lstm_weights.pt")
    torch.save(model.state_dict(), weights_path)

    metadata = {
        "materia": materia.upper(),
        "slug": slug,
        "materia_dataset": materia_dataset,
        "fallback_global": fallback_global,
        "tipo_arquitectura": "Red Neuronal Recurrente LSTM (PyTorch)",
        "hiperparametros": {
            "input_size": 4,
            "hidden_size": 32,
            "num_layers": 2,
            "dropout": 0.2,
            "epochs": effective_epochs,
            "learning_rate": lr,
            "optimizer": "Adam",
        },
        "metricas_por_hito": {
            "hito_1_primer_parcial": {
                "auc_roc": round(auc_h1, 4),
                "longitud_secuencia": 1,
            },
            "hito_2_tp_taller": {
                "auc_roc": round(auc_h2, 4),
                "longitud_secuencia": 2,
            },
            "hito_3_proceso_completo": {
                "auc_roc": round(auc_h3, 4),
                "accuracy": round(acc_h3, 4),
                "f1_score": round(f1_h3, 4),
                "longitud_secuencia": 3,
            },
        },
        "total_estudiantes_entrenamiento": int(len(df_train)),
        "total_estudiantes_test": int(len(df_test)),
    }

    with open(os.path.join(folder, "metadata_lstm.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    limpiar_cache_lstm(slug)
    return metadata


def _cargar_modelo_lstm(materia: str) -> Tuple[AcademicLSTM, Dict[str, Any]]:
    slug = _slugify(materia)
    if slug in _CACHE_LSTM:
        return _CACHE_LSTM[slug]["model"], _CACHE_LSTM[slug]["metadata"]

    folder = os.path.join(MODELS_DIR_LSTM, slug)
    weights_path = os.path.join(folder, "lstm_weights.pt")

    if not os.path.exists(weights_path):
        # Fallback a 'estatica' o entrenar
        folder_est = os.path.join(MODELS_DIR_LSTM, "estatica")
        if not os.path.exists(os.path.join(folder_est, "lstm_weights.pt")):
            entrenar_modelo_lstm("ESTATICA")
        folder = folder_est
        weights_path = os.path.join(folder, "lstm_weights.pt")

    model = AcademicLSTM(input_size=4, hidden_size=32, num_layers=2, dropout=0.2)
    model.load_state_dict(torch.load(weights_path, map_location=torch.device("cpu")))
    model.eval()

    meta_file = os.path.join(folder, "metadata_lstm.json")
    meta = {}
    if os.path.exists(meta_file):
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)

    _CACHE_LSTM[slug] = {"model": model, "metadata": meta}
    return model, meta


def predecir_probabilidad_lstm(
    materia: str = "ESTATICA",
    primer_parcial: float = 0.0,
    tplab: Optional[float] = None,
    segundo_parcial: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Inferencia de la Red Neuronal Recurrente LSTM.
    Recibe la secuencia de evaluaciones según los hitos rendidos hasta el momento.
    """
    model, meta = _cargar_modelo_lstm(materia)

    p1 = max(0.0, min(100.0, float(primer_parcial)))
    tiene_tp = tplab is not None and not (isinstance(tplab, float) and np.isnan(tplab))
    tiene_sp = segundo_parcial is not None and not (isinstance(segundo_parcial, float) and np.isnan(segundo_parcial))

    # Construir secuencia de longitud 1, 2 o 3
    seq = [[p1 / 100.0, p1 / 100.0, 0.0, 1.0 / 3.0]]

    if tiene_tp:
        tp = max(0.0, min(100.0, float(tplab)))
        seq.append([tp / 100.0, ((p1 + tp) / 2.0) / 100.0, (tp - p1) / 100.0, 2.0 / 3.0])

    if tiene_sp and segundo_parcial is not None:
        sp = max(0.0, min(100.0, float(segundo_parcial)))
        prev_tp = float(tplab) if (tiene_tp and tplab is not None) else p1
        prom_acum = ((p1 + float(tplab) + sp) / 3.0) if (tiene_tp and tplab is not None) else ((p1 + sp) / 2.0)
        seq.append([sp / 100.0, prom_acum / 100.0, (sp - prev_tp) / 100.0, 3.0 / 3.0])

    x_tensor = torch.tensor([seq], dtype=torch.float32)

    with torch.no_grad():
        logits_tensor, last_hidden = model(x_tensor)
        prob = float(torch.sigmoid(logits_tensor).item()) * 100.0
        hidden_norm = float(torch.norm(last_hidden).item())

    seq_len = len(seq)
    hito_key = f"hito_{seq_len}_{'primer_parcial' if seq_len==1 else 'tp_taller' if seq_len==2 else 'proceso_completo'}"
    auc_historico = meta.get("metricas_por_hito", {}).get(hito_key, {}).get("auc_roc", 0.90)

    return {
        "modelo": "Red Neuronal Recurrente (LSTM)",
        "probabilidad": round(prob, 1),
        "prediccion": "Aprueba" if prob >= 50.0 else "No Aprueba",
        "longitud_secuencia": seq_len,
        "auc_roc_historico": auc_historico,
        "magnitud_estado_oculto": round(hidden_norm, 4),
        "descripcion": (
            f"Red LSTM de 2 capas con celdas de compuertas recurrentes. Infiere la memoria continua "
            f"con una secuencia temporal de longitud {seq_len} paso(s)."
        ),
    }
