# RAG LLM Backend - Render Deployment

This FastAPI backend is optimized for deployment on Render.

## 🚀 Render Deployment

### Prerequisites
1. GitHub account with this repository
2. Render account (free tier available)

### Deployment Steps

1. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Sign up/login with GitHub
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service:**
   - **Name**: `rag-llm-backend` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables:**
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   MONGODB_URI=your_mongodb_connection_string
   MONGODB_DB=your_database_name
   ```

4. **Deploy:**
   - Click "Create Web Service"
   - Wait 3-5 minutes for build to complete
   - Your API will be live at: `https://your-service-name.onrender.com`

### 🔧 Service Configuration
- **Instance Type**: Free tier (512MB RAM) - upgrade to Starter ($7/month) for better performance
- **Auto-Deploy**: Enabled (deploys on git push)
- **Health Check**: `/health` endpoint available

### 📁 File Storage
- Uploaded PDFs are stored persistently in the `uploads/` directory
- Files persist between deployments and restarts

### 🎯 API Endpoints
Once deployed, your API will be available at:
- `GET /` - Health check
- `POST /upload/` - Upload PDF files
- `POST /ask/` - Ask questions about uploaded files
- `GET /history/` - Get user's question history
- `POST /register/` - User registration
- `POST /login/` - User login

### 🔍 Testing
```bash
curl https://your-service-name.onrender.com/health
```

### 💡 Performance Notes
- First request may take 30-60 seconds (model loading)
- Subsequent requests are fast (<2 seconds)
- Consider upgrading to Starter plan for production use

### 🔧 Troubleshooting
- Check Render logs if deployment fails
- Ensure all environment variables are set
- MongoDB connection string must be accessible from Render's IPs
