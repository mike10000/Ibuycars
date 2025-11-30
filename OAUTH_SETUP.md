# Google OAuth Setup Guide for Local Testing

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "iBuyCars" (or any name you prefer)
4. Click "Create"

## Step 2: Enable Google+ API

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and click "Enable"

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose "External" (unless you have Google Workspace)
3. Fill in the required fields:
   - **App name**: iBuyCars
   - **User support email**: Your email
   - **Developer contact email**: Your email
4. Click "Save and Continue"
5. Skip "Scopes" and "Test users" for now
6. Click "Save and Continue" until done

## Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Choose "Web application"
4. Fill in:
   - **Name**: iBuyCars Local
   - **Authorized JavaScript origins**: 
     ```
     http://localhost:5000
     ```
   - **Authorized redirect URIs**: 
     ```
     http://localhost:5000/oauth2callback
     ```
5. Click "Create"

## Step 5: Save Your Credentials

You'll see a popup with:
- **Your Client ID** (looks like: `xxxxx.apps.googleusercontent.com`)
- **Your Client Secret** (random string)

**IMPORTANT**: Copy these values! You'll need them in the next step.

## Step 6: Create .env File

Create a file named `.env` in your project directory with the following:

```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
SECRET_KEY=your_random_secret_key_here
```

Replace:
- `your_client_id_here` with your actual Client ID
- `your_client_secret_here` with your actual Client Secret
- `your_random_secret_key_here` with any random string (e.g., generate one from: https://randomkeygen.com/)

## Next Steps

Once you've completed these steps and created the `.env` file, I'll implement the OAuth flow in your application!

**Ready?** Let me know when you have your credentials, and I'll proceed with the implementation.
