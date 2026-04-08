# Flipkart Product Recommender

This project is a Flask-based RAG application that uses a vector store and a language model to answer product-related queries from Flipkart review data.

## Project Structure

- `app.py` - Flask application and request handling
- `Dockerfile` - Container build definition
- `requirements.txt` - Python dependencies
- `setup.py` - package installation setup
- `flipkart/` - application modules for configuration, ingestion, conversion, and RAG chain
- `data/flipkart_product_review.csv` - source review dataset
- `templates/index.html` - web UI
- `static/style.css` - UI styling
- `.env` - environment variables used by the app

## Environment Variables

Create a `.env` file with the following values before running locally or configuring Cloud Run:

```env
ASTRA_DB_API_ENDPOINT=<your_astra_db_api_endpoint>
ASTRA_DB_APPLICATION_TOKEN=<your_astra_db_application_token>
ASTRA_DB_KEYSPACE=<your_astra_db_keyspace>
GROQ_API_KEY=<your_groq_api_key>
```

> In GCP, store these values securely using Cloud Run environment variables or Secret Manager instead of committing them to source control.

## Local Setup

1. Create and activate a Python virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Open the browser at:

- `http://127.0.0.1:5000`

## Docker Build

Build the Docker image locally:

```bash
docker build -t flipkart-product-recommender .
```

Run the container locally:

```bash
docker run -p 5000:5000 --env-file .env flipkart-product-recommender
```

## Deploying to GCP Cloud Run

This project can be deployed to GCP Cloud Run using the provided `Dockerfile`.

### 1. Authenticate and set your project

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud config set run/region us-central1
```

### 2. Build and push the container

```bash
gcloud builds submit --tag gcr.io/$GOOGLE_CLOUD_PROJECT/flipkart-product-recommender
```

### 3. Deploy to Cloud Run

```bash
gcloud run deploy flipkart-product-recommender \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/flipkart-product-recommender \
  --platform managed \
  --allow-unauthenticated \
  --port 5000 \
  --memory 2Gi \
  --timeout 300
```

### 4. Set environment variables for Cloud Run

Option 1: Set env vars during deploy

```bash
gcloud run deploy flipkart-product-recommender \
  --image gcr.io/$GOOGLE_CLOUD_PROJECT/flipkart-product-recommender \
  --platform managed \
  --allow-unauthenticated \
  --port 5000 \
  --set-env-vars ASTRA_DB_API_ENDPOINT="<value>",ASTRA_DB_APPLICATION_TOKEN="<value>",ASTRA_DB_KEYSPACE="<value>",GROQ_API_KEY="<value>"
```

Option 2: Use Secret Manager and attach secrets to Cloud Run if you prefer stronger security.

## Production Notes

- The Flask app currently runs in debug mode by default. For production, disable debug and use a production WSGI server or Cloud Run's managed runtime.
- The container exposes port `5000`.
- Ensure GCP service account permissions are configured to access Cloud Run, Container Registry / Artifact Registry, and Secret Manager if used.

## Troubleshooting

- If you run into module import errors, verify that the virtual environment is active and `requirements.txt` is installed.
- If the app fails on startup due to model loading or Hugging Face errors, confirm your `GROQ_API_KEY` and any external service credentials.
- Use `gcloud run logs read flipkart-product-recommender` to inspect Cloud Run logs.

## Summary

This app is ready for GCP deployment with Docker and Cloud Run. Keep secret values out of source control and use environment variables or GCP Secret Manager for production.
