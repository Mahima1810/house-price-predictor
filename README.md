# House Price Predictor

Beginner-friendly full-stack ML project:
- **ML**: Linear Regression (scikit-learn)
- **Backend**: Flask API (`/predict`)
- **Frontend**: HTML/CSS/JS (dark, responsive)

## Project structure

- `backend/app.py` — Flask app + model training fallback
- `backend/model.pkl` — saved trained model
- `frontend/index.html` — UI
- `frontend/style.css` — dark theme
- `frontend/script.js` — calls `/predict`
- `requirements.txt`

## Run locally

From the `rent_predictor` folder:

```bash
python -m pip install -r requirements.txt
python backend/app.py
```

Open:
- http://localhost:5000/

## API usage

`POST /predict` with JSON:

```json
{
  "area": 1200,
  "rooms": 3,
  "location": 7
}
```

Response:

```json
{
  "predicted_price": 271234.56
}
```

## Deploy notes

- The app serves the frontend at `/`, so it opens directly in a browser (good for portfolio links).
- Most platforms set a `PORT` environment variable automatically; `backend/app.py` uses it if provided.
- For a production server on Linux, you can use Gunicorn:

```bash
pip install gunicorn
gunicorn -w 2 -b 0.0.0.0:$PORT backend.app:app
```
