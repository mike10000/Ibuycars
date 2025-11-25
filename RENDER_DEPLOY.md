# iBuyCars - Render.com Deployment Instructions

## Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with your GitHub account (mike10000)

## Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect repository: `mike10000/Ibuycars`
3. Configure:
   - **Name**: `ibuycars`
   - **Environment**: `Python 3`
   - **Build Command**: Leave empty (auto-detected)
   - **Start Command**: `gunicorn app:app`
   - **Plan**: **Free**

## Step 3: Set Environment Variables
Click "Advanced" → "Add Environment Variable":
- `APP_PASSWORD` = `YourSecurePassword123` (change this!)
- `SECRET_KEY` = `your-random-secret-key-here-make-it-long`
- `PYTHON_VERSION` = `3.11.0`

## Step 4: Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for deployment
- Your app will be at: `https://ibuycars.onrender.com`

## Step 5: Login
- Visit your app URL
- Enter the password you set in `APP_PASSWORD`
- Start searching for cars!

## Important Notes
- **Free tier sleeps after 15 min of inactivity**
- First request after sleep takes 30-60 seconds
- **Change the default password immediately!**
- The app is now password-protected

## Updating Your App
```bash
git add .
git commit -m "Update message"
git push origin main
```
Render will auto-deploy changes.

## Default Password
If you don't set `APP_PASSWORD`, the default is: `ibuycars2024`
**CHANGE THIS IN PRODUCTION!**
