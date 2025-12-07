# Deploying iBuyCars to Google Cloud Run

This guide will help you deploy your application to Google Cloud Run.

## Prerequisites

1.  **Google Cloud Project**: You need a Google Cloud project.
2.  **Google Cloud SDK**: You need `gcloud` installed and initialized.
    - [Install Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

## Deployment Steps

### 1. Initialize Google Cloud SDK

Open your terminal (PowerShell or Command Prompt) and run:

```bash
gcloud init
```

Follow the prompts to log in and select your project.

### 2. Enable Required Services

Enable the Cloud Run and Container Registry APIs:

```bash
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com
```

### 3. Deploy to Cloud Run

Run the following command to build and deploy your application. Replace `YOUR_PROJECT_ID` with your actual project ID (you can find it in the Google Cloud Console).

```bash
gcloud run deploy ibuycars --source . --platform managed --region us-central1 --allow-unauthenticated
```

-   `--source .`: Builds the container image from the current directory (using the Dockerfile).
-   `--platform managed`: Uses the fully managed Cloud Run platform.
-   `--region us-central1`: Deploys to the US Central 1 region (you can change this).
-   `--allow-unauthenticated`: Makes the service publicly accessible (required for a public web app).

### 4. Configure Environment Variables

During deployment (or afterwards in the Cloud Console), you need to set your environment variables. You can pass them in the deploy command using `--set-env-vars`:

```bash
gcloud run deploy ibuycars --source . --platform managed --region us-central1 --allow-unauthenticated --set-env-vars "GOOGLE_CLIENT_ID=your_id,GOOGLE_CLIENT_SECRET=your_secret,SECRET_KEY=your_key"
```

**OR** set them in the Google Cloud Console:
1.  Go to [Cloud Run Console](https://console.cloud.google.com/run).
2.  Click on your service (`ibuycars`).
3.  Click "Edit & Deploy New Revision".
4.  Go to the "Variables & Secrets" tab.
5.  Add your variables (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `SECRET_KEY`).
6.  Click "Deploy".

### 5. Update OAuth Redirect URI

1.  Get your Cloud Run URL (e.g., `https://ibuycars-xyz-uc.a.run.app`).
2.  Go to [Google Cloud Console > APIs & Services > Credentials](https://console.cloud.google.com/apis/credentials).
3.  Edit your OAuth 2.0 Client ID.
4.  Add the Cloud Run URL to "Authorized JavaScript origins".
5.  Add `https://YOUR_APP_URL/oauth2callback` to "Authorized redirect URIs".
6.  Save.

## Important Notes

-   **Statelessness**: Cloud Run is stateless. Any data saved to `users.db` or `notes.db` will be **lost** when the container restarts (which happens frequently).
-   **Scraping**: The application uses Selenium with Chrome. The Dockerfile includes Chrome, but scraping performance on Cloud Run might vary.
