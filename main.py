from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
import base64
import io
import os
from openai import OpenAI
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="TDS Virtual TA", description="AI-powered teaching assistant for TDS course")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Request/Response models
class Link(BaseModel):
    url: str
    text: str

class QuestionRequest(BaseModel):
    question: str
    image: Optional[str] = None  # base64 encoded image

class QuestionResponse(BaseModel):
    answer: str
    links: List[Link]

# Global variables for embeddings and data
course_data = []
discourse_data = []
course_embeddings = []
discourse_embeddings = []

def load_data():
    """Load course content and discourse data"""
    global course_data, discourse_data
    
    # Load course content
    try:
        with open("CourseContentData.jsonl", "r", encoding="utf-8") as f:
            course_data = [json.loads(line) for line in f]
    except FileNotFoundError:
        print("CourseContentData.jsonl not found")
        course_data = []
    
    # Load discourse data
    try:
        with open("DicourseData.jsonl", "r", encoding="utf-8") as f:
            discourse_data = [json.loads(line) for line in f]
    except FileNotFoundError:
        print("DicourseData.jsonl not found")
        discourse_data = []

def generate_embeddings():
    """Generate embeddings for course content and discourse data"""
    global course_embeddings, discourse_embeddings
    
    print("Generating embeddings...")
    
    # Generate course content embeddings
    if course_data:
        course_texts = [item.get("content", "") for item in course_data]
        course_embeddings = get_embeddings(course_texts)
    
    # Generate discourse embeddings
    if discourse_data:
        discourse_texts = [item.get("content", "") for item in discourse_data]
        discourse_embeddings = get_embeddings(discourse_texts)
    
    print(f"Generated {len(course_embeddings)} course embeddings and {len(discourse_embeddings)} discourse embeddings")

def get_embeddings(texts: List[str], batch_size: int = 100):
    """Get embeddings from OpenAI API in batches"""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        # Filter out empty texts
        batch = [text for text in batch if text.strip()]
        
        if not batch:
            continue
            
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch
            )
            batch_embeddings = [item.embedding for item in response.data]
            embeddings.extend(batch_embeddings)
        except Exception as e:
            print(f"Error generating embeddings for batch {i//batch_size + 1}: {e}")
            # Add zero embeddings for failed batch
            embeddings.extend([[0] * 1536 for _ in batch])
    
    return np.array(embeddings)

def find_relevant_content(question: str, top_k: int = 5):
    """Find most relevant content using cosine similarity"""
    if not course_embeddings.size and not discourse_embeddings.size:
        return []
    
    # Get question embedding
    try:
        question_response = client.embeddings.create(
            model="text-embedding-3-small",
            input=[question]
        )
        question_embedding = np.array(question_response.data[0].embedding).reshape(1, -1)
    except Exception as e:
        print(f"Error generating question embedding: {e}")
        return []
    
    relevant_items = []
    
    # Search in course content
    if course_embeddings.size > 0:
        similarities = cosine_similarity(question_embedding, course_embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        for idx in top_indices:
            if similarities[idx] > 0.7:  # Similarity threshold
                item = course_data[idx].copy()
                item['similarity'] = float(similarities[idx])
                item['source'] = 'course'
                relevant_items.append(item)
    
    # Search in discourse data
    if discourse_embeddings.size > 0:
        similarities = cosine_similarity(question_embedding, discourse_embeddings)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        for idx in top_indices:
            if similarities[idx] > 0.7:  # Similarity threshold
                item = discourse_data[idx].copy()
                item['similarity'] = float(similarities[idx])
                item['source'] = 'discourse'
                relevant_items.append(item)
    
    # Sort by similarity and return top results
    relevant_items.sort(key=lambda x: x['similarity'], reverse=True)
    return relevant_items[:top_k]

def generate_answer(question: str, relevant_content: List[dict], image_data: Optional[str] = None):
    """Generate answer using OpenAI GPT"""
    # Prepare context from relevant content
    context_parts = []
    links = []
    
    for item in relevant_content:
        if item['source'] == 'course':
            context_parts.append(f"Course Content: {item.get('content', '')}")
            if 'url' in item and item['url']:
                links.append(Link(url=item['url'], text="Course material"))
        else:  # discourse
            context_parts.append(f"Discussion: {item.get('content', '')}")
            if 'url' in item and item['url']:
                links.append(Link(url=item['url'], text=item.get('content', '')[:100] + "..."))
    
    context = "\n\n".join(context_parts)
    
    # Prepare messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful teaching assistant for the IIT Madras Tools in Data Science course. Answer questions based on the provided context from course materials and discussion forums. Be concise and accurate."
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}"
        }
    ]
    
    # Add image if provided
    if image_data:
        try:
            messages[1]["content"] = [
                {"type": "text", "text": f"Context:\n{context}\n\nQuestion: {question}"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_data}"
                    }
                }
            ]
        except Exception as e:
            print(f"Error processing image: {e}")
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        return answer, links[:3]  # Return top 3 links
        
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "I apologize, but I'm unable to generate an answer at the moment. Please try again later.", []

@app.on_event("startup")
async def startup_event():
    """Load data and generate embeddings on startup"""
    load_data()
    generate_embeddings()

@app.post("/api/", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Main API endpoint for asking questions"""
    try:
        # Find relevant content
        relevant_content = find_relevant_content(request.question)
        
        if not relevant_content:
            return QuestionResponse(
                answer="I couldn't find relevant information to answer your question. Please try rephrasing or asking about course-related topics.",
                links=[]
            )
        
        # Generate answer
        answer, links = generate_answer(request.question, relevant_content, request.image)
        
        return QuestionResponse(answer=answer, links=links)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "data_loaded": len(course_data) + len(discourse_data)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)