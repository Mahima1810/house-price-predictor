import os
import tempfile
from typing import Any, Dict, Tuple

import joblib
import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from sklearn.linear_model import LinearRegression


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_model_path() -> str:
    # Vercel's filesystem is read-only except /tmp.
    if os.environ.get("VERCEL"):
        return os.path.join(tempfile.gettempdir(), "house_price_model.pkl")
    return os.path.join(BASE_DIR, "model.pkl")


MODEL_PATH = _get_model_path()
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

_model: LinearRegression | None = None


def _train_and_save_dummy_model(model_path: str) -> None:
    rng = np.random.default_rng(42)

    # Dummy training data (beginner-friendly + deterministic)
    # Features: [area_sqft, rooms, location_score]
    n = 400
    area = rng.integers(400, 3500, size=n)
    rooms = rng.integers(1, 7, size=n)
    location = rng.integers(1, 11, size=n)

    X = np.column_stack([area, rooms, location]).astype(float)

    # Simple synthetic pricing formula (+ small noise)
    noise = rng.normal(0, 25_000, size=n)
    y = (
        50_000
        + 120 * area
        + 15_000 * rooms
        + 10_000 * location
        + noise
    ).astype(float)

    model = LinearRegression()
    model.fit(X, y)

    joblib.dump(model, model_path)


def _load_model() -> LinearRegression:
    global _model

    if _model is not None:
        return _model

    if not os.path.exists(MODEL_PATH):
        _train_and_save_dummy_model(MODEL_PATH)

    _model = joblib.load(MODEL_PATH)
    return _model


def _parse_and_validate(payload: Dict[str, Any] | None) -> Tuple[np.ndarray, str | None]:
    if not isinstance(payload, dict):
        return np.empty((0, 3)), "Request body must be JSON."

    missing = [k for k in ("area", "rooms", "location") if k not in payload]
    if missing:
        return np.empty((0, 3)), f"Missing fields: {', '.join(missing)}"

    try:
        area = float(payload["area"])
        rooms = int(payload["rooms"])
        location = float(payload["location"])
    except (TypeError, ValueError):
        return np.empty((0, 3)), "area, rooms, and location must be numbers."

    if area <= 0:
        return np.empty((0, 3)), "area must be greater than 0."
    if rooms <= 0:
        return np.empty((0, 3)), "rooms must be at least 1."
    if location < 1 or location > 10:
        return np.empty((0, 3)), "location must be between 1 and 10."

    X = np.array([[area, float(rooms), location]], dtype=float)
    return X, None


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.post("/predict")
def predict():
    payload = request.get_json(silent=True)
    X, error = _parse_and_validate(payload)
    if error:
        return jsonify({"error": error}), 400

    model = _load_model()

    try:
        prediction = float(model.predict(X)[0])
    except Exception:
        return jsonify({"error": "Prediction failed."}), 500

    # Return rounded value for nicer UX
    return jsonify({"predicted_price": round(prediction, 2)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
