# TDS Virtual Teaching Assistant

A FastAPI-based virtual teaching assistant for the IIT Madras Tools in Data Science course. Uses OpenAI embeddings and GPT for intelligent question answering based on course content and discussion forum data.

## Features

- **Intelligent Q&A**: Answers questions using course content and forum discussions
- **Image Support**: Processes base64-encoded images in questions
- **Semantic Search**: Uses OpenAI embeddings for relevant content retrieval
- **RESTful API**: FastAPI-based endpoint with JSON responses
- **Vercel Ready**: Configured for easy deployment on Vercel

## Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the Server**
   ```bash
   python main.py
   ```

4. **Test the API**
   ```bash
   python test_api.py
   ```

### API Usage

**Endpoint**: `POST /api/`

**Request Format**:
```json
{
  "question": "Your question here",
  "image": "base64_encoded_image_data" // optional
}
```

**Response Format**:
```json
{
  "answer": "Generated answer based on course content",
  "links": [
    {
      "url": "https://relevant-url.com",
      "text": "Link description"
    }
  ]
}
```

**Example cURL**:
```bash
curl "http://localhost:8000/api/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the difference between gpt-4o-mini and gpt-3.5-turbo?"}'
```

### Vercel Deployment

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Deploy**
   ```bash
   vercel --prod
   ```

3. **Set Environment Variables**
   ```bash
   vercel env add OPENAI_API_KEY
   ```

## Architecture

- **Data Sources**: CourseContentData.jsonl (558 records) and DicourseData.jsonl (3,380 records)
- **Embeddings**: OpenAI text-embedding-3-small for semantic search
- **LLM**: OpenAI GPT-3.5-turbo for answer generation  
- **Search**: Cosine similarity with 0.7 threshold for relevance
- **Framework**: FastAPI with Pydantic models

## Health Check

**Endpoint**: `GET /health`

Returns server status and data loading information.

## Environment Variables

- `OPENAI_API_KEY`: Required OpenAI API key
- `OPENAI_ORG_ID`: Optional OpenAI organization ID