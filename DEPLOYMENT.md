# Render.com Deployment Guide for iBuyCars

## Quick Setup Instructions

### 1. Sign up for Render.com
- Go to https://render.com
- Sign up with your GitHub account

### 2. Create a New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `mike10000/Ibuycars`
3. Configure the service:
   - **Name**: `ibuycars` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: `Free`

### 3. Set Environment Variables
In the Render dashboard, add these environment variables:
- `APP_PASSWORD`: Your desired password (e.g., `MySecurePassword123`)
- `SECRET_KEY`: A random secret key (e.g., `your-random-secret-key-here`)
- `PYTHON_VERSION`: `3.11.0`

### 4. Deploy
- Click "Create Web Service"
- Render will automatically deploy your app
- Wait 5-10 minutes for the first deployment

### 5. Access Your App
- Your app will be available at: `https://ibuycars.onrender.com` (or your chosen name)
- Default password is: `ibuycars2024` (change this in environment variables!)

## Important Notes

### Password Protection
- The app is password-protected by default
- Change the `APP_PASSWORD` environment variable in Render dashboard
- Users must login before accessing the search functionality

### Free Tier Limitations
- App sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds (cold start)
- 750 hours/month of runtime
- 512MB RAM

### Updating Your App
1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push origin main
   ```
3. Render will automatically redeploy

## Troubleshooting

### If deployment fails:
1. Check the Render logs in the dashboard
2. Verify all environment variables are set
3. Make sure `requirements.txt` includes all dependencies

### If web scraping doesn't work:
- Some sites may block Render's IP addresses
- Consider using proxies or rotating user agents
- Facebook Marketplace may require additional configuration

## Security Tips
1. **Change the default password immediately**
2. Use a strong `SECRET_KEY`
3. Don't commit sensitive data to GitHub
4. Use environment variables for all secrets
