import numpy as np
import pytest
from datetime import date

from database import Database


def test_model_output_shape():
    from train_model import build_lstm_model

    n_features = 15
    model = build_lstm_model(sequence_length=21, n_features=n_features)
    assert model.input_shape == (None, 21, n_features)
    assert len(model.output_shape) == 2
    assert model.output_shape[0] == (None, 1)
    assert model.output_shape[1] == (None, 1)
    assert model.count_params() > 0


def test_model_prediction_range():
    from train_model import build_lstm_model
    import tensorflow as tf

    n_features = 15
    model = build_lstm_model(21, n_features)
    dummy_input = tf.random.normal((1, 21, n_features))
    prob_out, cases_out = model.predict(dummy_input, verbose=0)

    prob = prob_out[0, 0]
    cases = cases_out[0, 0]

    assert 0.0 <= prob <= 1.0
    assert cases >= 0.0
    assert np.all(np.isfinite(prob_out))
    assert np.all(np.isfinite(cases_out))


def test_prepare_sequences_shape():
    from train_model import prepare_sequences

    n_samples = 100
    n_features = 10
    data = np.random.randn(n_samples, n_features)
    targets = np.random.randn(n_samples)

    X, y_prob, y_cases = prepare_sequences(
        data, targets, targets, seq_length=21
    )
    expected = n_samples - 21 - 6
    assert X.shape == (expected, 21, n_features)
    assert y_prob.shape == (expected,)
    assert y_cases.shape == (expected,)


def test_predictor_load_nonexistent_model():
    from predictor import Predictor

    predictor = Predictor()
    model = predictor.load_model("nonexistent_model")
    assert model is None


def test_predictor_predict_without_model():
    from predictor import Predictor

    predictor = Predictor()
    result = predictor.predict("nonexistent", sequence_length=21)
    assert result is None


def test_predictor_predict_valid():
    from predictor import Predictor

    predictor = Predictor()
    result = predictor.predict("dengue", sequence_length=21)
    assert result is not None
    assert "outbreak_probability" in result
    assert "estimated_cases_7d" in result
    assert "ci_lower" in result
    assert "ci_upper" in result
    assert 0.0 <= result["outbreak_probability"] <= 1.0
    assert result["estimated_cases_7d"] >= 0
