# Flow Deployment Guide

Deploy Flow to the cloud so users don't need to run the backend locally.

## Quick Deploy Options

### 🚀 Railway (Recommended - Easiest)

1. **Push to GitHub** (if not already)
2. **Go to [Railway.app](https://railway.app)**
3. **Connect GitHub** and select your Flow repository
4. **Deploy** - Railway auto-detects Python and uses the `Procfile`
5. **Get your API URL** (e.g., `https://flow-api-production.up.railway.app`)

### 🌐 Render

1. **Push to GitHub** (if not already)
2. **Go to [Render.com](https://render.com)**
3. **New Web Service** → Connect GitHub → Select Flow repo
4. **Configure:**
   - Build Command: `pip install -r backend/requirements-api.txt`
   - Start Command: `python -m backend.api_server`
   - Health Check Path: `/api/health`
5. **Deploy** and get your API URL

### ☁️ Heroku

1. **Install Heroku CLI**
2. **Login:** `heroku login`
3. **Create app:** `heroku create your-flow-api`
4. **Deploy:** `git push heroku main`
5. **Get URL:** `heroku info`

## Update Frontend

After deploying the backend, update your Vercel deployment:

1. **Go to Vercel Dashboard** → Your Flow project
2. **Settings** → **Environment Variables**
3. **Add:** `NEXT_PUBLIC_API_URL` = `https://your-api-url.com`
4. **Redeploy** the frontend

## Environment Variables

The backend automatically uses these environment variables:

- `PORT` - Port number (auto-set by cloud providers)
- `HOST` - Host address (defaults to 0.0.0.0)

## CORS Configuration

The API server is already configured to allow requests from:
- `http://localhost:3000` (local development)
- `http://localhost:3001` (local development)
- Your Vercel domain (add this after deployment)

To add your Vercel domain, update `backend/api_server.py`:

```python
allow_origins=[
    "http://localhost:3000", 
    "http://localhost:3001",
    "https://your-vercel-app.vercel.app"  # Add your Vercel URL
]
```

## Cost Considerations

- **Railway:** Free tier includes 500 hours/month
- **Render:** Free tier with limitations
- **Heroku:** No free tier (paid only)

## Troubleshooting

### Models Not Loading
- Cloud providers may have memory limits
- Consider using smaller models for production
- Add error handling for model loading failures

### CORS Errors
- Make sure your Vercel URL is in the CORS allow list
- Check that environment variables are set correctly

### Timeout Issues
- Cloud functions may have execution time limits
- Consider optimizing the analysis pipeline
- Add progress indicators for long operations

## Production Optimizations

1. **Use smaller models** for faster loading
2. **Add caching** for repeated analyses
3. **Implement rate limiting** to prevent abuse
4. **Add monitoring** and error tracking
5. **Use CDN** for static assets

## Example Railway Deployment

```bash
# 1. Push to GitHub
git add .
git commit -m "Add deployment config"
git push origin main

# 2. Go to Railway.app
# 3. Connect GitHub repo
# 4. Deploy automatically
# 5. Copy the API URL
# 6. Update Vercel environment variables
```

Your Flow app will then be fully cloud-hosted! 🎉
