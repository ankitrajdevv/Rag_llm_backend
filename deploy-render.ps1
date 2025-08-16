# Render Deployment Script for PowerShell
# This script helps deploy your RAG LLM backend to Render

Write-Host "🚀 RAG LLM Backend - Render Deployment" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Check if we have the render.yaml file
if (Test-Path "render.yaml") {
    Write-Host "✅ render.yaml found" -ForegroundColor Green
} else {
    Write-Host "❌ render.yaml not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 Deployment Steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://render.com"
Write-Host "2. Sign up/login with GitHub"
Write-Host "3. Click 'New +' → 'Web Service'"
Write-Host "4. Connect your GitHub repository: ankitrajdevv/Rag_llm_backend"
Write-Host "5. Select branch: development"
Write-Host "6. Render will automatically detect the render.yaml file"
Write-Host "7. Click 'Create Web Service'"
Write-Host ""

Write-Host "🔧 Manual Configuration (if render.yaml isn't detected):" -ForegroundColor Yellow
Write-Host "Build Command: pip install -r requirements.txt"
Write-Host "Start Command: uvicorn main:app --host 0.0.0.0 --port `$PORT"
Write-Host ""

Write-Host "🔐 Environment Variables (if not using render.yaml):" -ForegroundColor Yellow
Write-Host "GOOGLE_API_KEY=AIzaSyBGO0_V6EXzZt8qfd2OHcWZA4aOei7gB0Q"
Write-Host "MONGODB_URI=mongodb+srv://kumarankitverma5:test123@cluster0.bvgikdc.mongodb.net/Rag_llm?retryWrites=true&w=majority&appName=Cluster0"
Write-Host "MONGODB_DB=Rag_llm"
Write-Host ""

Write-Host "⏱️  Expected deployment time: 3-5 minutes" -ForegroundColor Cyan
Write-Host "🌐 Your API will be available at: https://your-service-name.onrender.com" -ForegroundColor Green
Write-Host ""

Write-Host "🧪 Test your deployment with:" -ForegroundColor Cyan
Write-Host "curl https://your-service-name.onrender.com/health"
Write-Host ""

$continue = Read-Host "Press Enter to continue to Render dashboard, or type 'skip' to exit"
if ($continue -ne "skip") {
    Start-Process "https://dashboard.render.com"
}
