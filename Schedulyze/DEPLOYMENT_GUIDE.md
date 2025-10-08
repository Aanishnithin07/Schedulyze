# 🚀 Schedulyze Deployment Guide

## Overview
This guide covers multiple deployment options for your Schedulyze AI Study Scheduler application.

## 🟢 Option 1: Vercel Deployment (FastAPI Version)

### What I've Created for You:
1. **`api.py`** - FastAPI version of your Streamlit app with web interface
2. **`main.py`** - Entry point for Vercel
3. **`vercel.json`** - Vercel configuration file
4. **Updated `requirements.txt`** - Added FastAPI dependencies

### Deployment Steps:

1. **Prepare Your Repository:**
   ```bash
   cd /Users/aanishnithin/Schedulyze/Schedulyze/Schedulyze
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign up/in with your GitHub account
   - Click "New Project"
   - Import your `Schedulyze` repository
   - Vercel will automatically detect the configuration
   - Click "Deploy"

3. **Configuration in Vercel Dashboard:**
   - Root Directory: `Schedulyze/Schedulyze`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

### ⚠️ Note:
The FastAPI version provides a web interface but differs from your original Streamlit app. It includes:
- Web-based form for adding subjects
- Schedule generation API
- Basic styling and interactions

---

## 🔵 Option 2: Streamlit Community Cloud (Recommended for Streamlit)

### Why This is Better for Streamlit:
- **Free hosting** specifically designed for Streamlit apps
- **Zero configuration** needed
- **Direct GitHub integration**
- **Automatic deployments** on git push

### Deployment Steps:

1. **Prepare Repository:**
   - Ensure your `app.py` is in the root of your repo
   - Make sure `requirements.txt` is up to date

2. **Deploy:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `Aanishnithin07/Schedulyze`
   - Set Main file path: `Schedulyze/Schedulyze/app.py`
   - Click "Deploy"

3. **Your app will be live at:**
   `https://aanishnithin07-schedulyze-schedulyze-schedulyze-app-xxxxx.streamlit.app`

---

## 🟡 Option 3: Railway Deployment

Railway supports both Streamlit and FastAPI applications:

1. **Go to [railway.app](https://railway.app)**
2. **Connect your GitHub repository**
3. **Add environment variables if needed**
4. **Deploy automatically**

### For Streamlit on Railway, create a `Procfile`:
```
web: streamlit run Schedulyze/Schedulyze/app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## 🟠 Option 4: Render Deployment

1. **Go to [render.com](https://render.com)**
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Configure:**
   - Build Command: `pip install -r Schedulyze/Schedulyze/requirements.txt`
   - Start Command: `streamlit run Schedulyze/Schedulyze/app.py --server.port=$PORT --server.address=0.0.0.0`

---

## 📋 Pre-Deployment Checklist

### For ALL deployment options:

1. **Repository Structure Check:**
   ```
   Schedulyze/
   ├── README.md
   └── Schedulyze/
       └── Schedulyze/
           ├── app.py (main Streamlit app)
           ├── api.py (FastAPI version)
           ├── main.py (Vercel entry point)
           ├── requirements.txt
           ├── vercel.json
           └── other files...
   ```

2. **Requirements.txt Verification:**
   ```
   streamlit>=1.28.0
   pandas>=2.0.0
   numpy>=1.24.0
   plotly>=5.15.0
   icalendar>=5.0.0
   fastapi>=0.104.0  # For Vercel/FastAPI version
   uvicorn>=0.24.0   # For Vercel/FastAPI version
   pydantic>=2.0.0   # For Vercel/FastAPI version
   ```

3. **Test Locally:**
   ```bash
   # Test Streamlit version
   cd Schedulyze/Schedulyze
   streamlit run app.py
   
   # Test FastAPI version (for Vercel)
   python api.py
   ```

---

## 🎯 My Recommendations

### For Easiest Deployment: **Streamlit Community Cloud**
- Zero configuration
- Free
- Perfect for Streamlit apps
- Automatic deployments

### For Custom Domain/Advanced Features: **Railway or Render**
- Support custom domains
- More configuration options
- Supports both Streamlit and other frameworks

### For Vercel Lovers: **Use the FastAPI version**
- Modern web interface
- API-based architecture
- Works well with Vercel's infrastructure

---

## 🔧 Troubleshooting

### Common Issues:

1. **Module Not Found Errors:**
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version compatibility

2. **Port Issues:**
   - Most platforms provide a `$PORT` environment variable
   - Use `--server.port=$PORT` for Streamlit

3. **File Path Issues:**
   - Use absolute paths in deployment
   - Verify your repository structure

### Need Help?
If you encounter any issues during deployment, let me know and I'll help you troubleshoot!

---

## 🚀 Quick Start Commands

```bash
# Navigate to your project
cd /Users/aanishnithin/Schedulyze/Schedulyze/Schedulyze

# Add deployment files to git
git add .
git commit -m "Add deployment configuration for multiple platforms"
git push origin main

# Now choose your preferred deployment platform from the options above!
```