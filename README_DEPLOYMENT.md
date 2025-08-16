# RAG LLM Backend - Vercel Deployment

This FastAPI backend is configured for deployment on Vercel.

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
GOOGLE_API_KEY=your_google_api_key
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB=your_database_name
```

3. Run locally:
```bash
uvicorn main:app --reload
```

## Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Set environment variables in Vercel:
```bash
vercel env add GOOGLE_API_KEY
vercel env add MONGODB_URI
vercel env add MONGODB_DB
```

4. Deploy:
```bash
vercel --prod
```

## Environment Variables

Make sure to set these environment variables in your Vercel dashboard:
- `GOOGLE_API_KEY`: Your Google Generative AI API key
- `MONGODB_URI`: Your MongoDB connection string
- `MONGODB_DB`: Your MongoDB database name

## API Endpoints

- `POST /upload/`: Upload a PDF file
- `POST /ask/`: Ask a question about an uploaded file
- `GET /history/`: Get question history for a user
- Authentication endpoints (from auth router)
