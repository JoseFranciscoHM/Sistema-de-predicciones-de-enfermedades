#!/usr/bin/env python3
import os
import sys
import argparse
import logging
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from database import Database
from synthetic_data import DISEASES, KEYWORDS, MUNICIPALITIES, get_municipality_population_weight

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train_model")

SEQUENCE_LENGTH = 21
N_FEATURES = 15
EPOCHS = 100
BATCH_SIZE = 32
EARLY_STOPPING_PATIENCE = 10
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"


def build_lstm_model(
    sequence_length: int = SEQUENCE_LENGTH,
    n_features: int = N_FEATURES,
) -> keras.Model:
    inputs = keras.Input(shape=(sequence_length, n_features), name="input")

    x = layers.Bidirectional(
        layers.LSTM(128, return_sequences=True, dropout=0.3)
    )(inputs)
    x = layers.Bidirectional(
        layers.LSTM(64, dropout=0.3)
    )(x)
    x = layers.Dense(32, activation="relu")(x)
    x = layers.Dropout(0.2)(x)

    outbreak_prob = layers.Dense(1, activation="sigmoid", name="outbreak_prob")(x)
    daily_cases = layers.Dense(1, activation="relu", name="daily_cases")(x)

    model = keras.Model(
        inputs=inputs,
        outputs=[outbreak_prob, daily_cases],
        name="disease_predictor",
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss={
            "outbreak_prob": "binary_crossentropy",
            "daily_cases": "mse",
        },
        metrics={
            "outbreak_prob": ["accuracy"],
            "daily_cases": ["mse"],
        },
    )
    return model


def prepare_sequences(
    data: np.ndarray,
    prob_targets: np.ndarray,
    cases_targets: np.ndarray,
    seq_length: int = SEQUENCE_LENGTH,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    X, y_prob, y_cases = [], [], []
    total_samples = len(data)
    for i in range(total_samples - seq_length - 6):
        X.append(data[i : i + seq_length])
        y_prob.append(prob_targets[i + seq_length])
        next_7 = cases_targets[i + seq_length : i + seq_length + 7]
        y_cases.append(np.sum(next_7))
    return np.array(X), np.array(y_prob), np.array(y_cases)


def build_features_from_db(
    disease: str, db: Database
) -> tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    end_date = date.today()
    start_date = end_date - timedelta(days=730)

    trends = db.get_search_trends(disease, start_date, end_date)
    epi = db.get_timeseries(disease, start_date, end_date)

    if not epi:
        logger.warning(f"No hay datos epidemiologicos para {disease}")
        return None, None, None

    date_index: dict[date, int] = {}
    for i, entry in enumerate(epi):
        d = entry["date"]
        if isinstance(d, str):
            d = datetime.strptime(d, "%Y-%m-%d").date()
        date_index[d] = i

    keyword_list = db.get_all_keywords(disease)
    n_kw = len(keyword_list)
    n_features = n_kw + 3

    dates = sorted(date_index.keys())
    n_samples = len(dates)

    feature_data = np.zeros((n_samples, n_features))
    prob_targets = np.zeros(n_samples)
    cases_targets = np.zeros(n_samples)

    for i, d in enumerate(dates):
        kw_values = []
        for kw in keyword_list:
            matching = [t for t in trends if t["keyword"] == kw and t["date"] == d]
            val = matching[0]["value"] if matching else 0.0
            kw_values.append(val)
        feature_data[i, :n_kw] = kw_values

        epi_entry = epi[date_index[d]]
        cases = float(epi_entry["confirmed_cases"])
        hosp = float(epi_entry["hospitalizations"])
        deaths = float(epi_entry["deaths"])

        feature_data[i, n_kw] = cases / 100.0
        feature_data[i, n_kw + 1] = hosp / 20.0
        feature_data[i, n_kw + 2] = deaths / 5.0

        prob_targets[i] = 1.0 if cases > 20 else 0.0
        cases_targets[i] = cases

    return feature_data, prob_targets, cases_targets


def train_disease_model(
    disease: str,
    db: Database,
    sequence_length: int = SEQUENCE_LENGTH,
    epochs: int = EPOCHS,
    batch_size: int = BATCH_SIZE,
) -> dict[str, Any]:
    tf.random.set_seed(42)
    np.random.seed(42)

    logger.info(f"Construyendo features para {disease}...")
    data, prob_targets, cases_targets = build_features_from_db(disease, db)
    if data is None:
        raise ValueError(f"No hay datos suficientes para entrenar {disease}")

    n_features = data.shape[1]
    logger.info(f"Features: {n_features}, Muestras: {len(data)}")

    if len(data) < sequence_length + 10:
        raise ValueError(
            f"Se necesitan al menos {sequence_length + 10} muestras "
            f"para {disease}, se tienen {len(data)}"
        )

    X, y_prob, y_cases = prepare_sequences(data, prob_targets, cases_targets, sequence_length)

    split = int(len(X) * 0.8)
    X_train, X_val = X[:split], X[split:]
    y_prob_train, y_prob_val = y_prob[:split], y_prob[split:]
    y_cases_train, y_cases_val = y_cases[:split], y_cases[split:]

    logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}")

    model = build_lstm_model(sequence_length, n_features)

    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6,
        ),
    ]

    start_time = time.time()
    history = model.fit(
        X_train,
        {"outbreak_prob": y_prob_train, "daily_cases": y_cases_train},
        validation_data=(
            X_val,
            {"outbreak_prob": y_prob_val, "daily_cases": y_cases_val},
        ),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1,
    )
    duration = time.time() - start_time

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = str(MODEL_DIR / f"{disease}_model.keras")
    model.save(model_path)
    logger.info(f"Modelo guardado en {model_path}")

    # Evaluate
    y_prob_pred, y_cases_pred = model.predict(X_val, verbose=0)
    y_prob_pred_bin = (y_prob_pred.flatten() > 0.5).astype(float)

    tp = np.sum((y_prob_val == 1) & (y_prob_pred_bin == 1))
    tn = np.sum((y_prob_val == 0) & (y_prob_pred_bin == 0))
    fp = np.sum((y_prob_val == 0) & (y_prob_pred_bin == 1))
    fn = np.sum((y_prob_val == 1) & (y_prob_pred_bin == 0))

    sensitivity = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    accuracy = float((tp + tn) / (tp + tn + fp + fn)) if (tp + tn + fp + fn) > 0 else 0.0
    rmse = float(np.sqrt(np.mean((y_cases_val - y_cases_pred.flatten()) ** 2)))

    logger.info(
        f"Métricas {disease}: sens={sensitivity:.3f}, spec={specificity:.3f}, "
        f"rmse={rmse:.3f}, prec={precision:.3f}, acc={accuracy:.3f}"
    )

    return {
        "disease": disease,
        "sensitivity": round(sensitivity, 4),
        "specificity": round(specificity, 4),
        "rmse": round(rmse, 4),
        "precision": round(precision, 4),
        "accuracy": round(accuracy, 4),
        "training_duration_s": round(duration, 2),
        "num_epochs": len(history.history["loss"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Entrenar modelo RNN por enfermedad"
    )
    parser.add_argument(
        "--disease", type=str, required=True,
        choices=DISEASES,
        help="Enfermedad para entrenar"
    )
    parser.add_argument(
        "--epochs", type=int, default=EPOCHS,
        help="Numero maximo de epocas"
    )
    args = parser.parse_args()

    db = Database()
    metrics = train_disease_model(args.disease, db, epochs=args.epochs)
    if metrics:
        db.insert_model_metrics({
            "disease": args.disease,
            "sensitivity": metrics["sensitivity"],
            "specificity": metrics["specificity"],
            "rmse": metrics["rmse"],
            "precision": metrics["precision"],
            "accuracy": metrics["accuracy"],
        })
    print(f"Métricas finales: {metrics}")


if __name__ == "__main__":
    main()
