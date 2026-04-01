import os
import requests
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from premailer import transform
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- 1. ENABLE CORS (Allows your HTML file to talk to this script) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. CONFIGURATION ---
# Using the Groq API Key you provided
GROQ_API_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

class EmailRequest(BaseModel):
    prompt: str

SYSTEM_PROMPT = (
    "You are an expert AJO Developer. Generate professional HTML using <table> layouts. "
    "IMPORTANT: Do NOT use {{profile...}} tags. Instead, look at the prompt I send you. "
    "If the prompt says 'Write for Sanju', you must write 'Hello Sanju' directly in the HTML. "
    "Always include this image: <img src='https://images.unsplash.com/photo-1505751172107-130095c979d3?w=600' style='width:100%; max-width:600px;'>"
)

@app.post("/generate-email")
async def generate_email(request: EmailRequest):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Updated to the current active Groq model
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": request.prompt}
            ],
            "temperature": 0.6
        }

        print(f"🚀 Generating email for: {request.prompt}")
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"❌ Groq Error: {response.text}")
            raise Exception(f"Groq API Error: {response.json().get('error', {}).get('message', 'Unknown')}")

        data = response.json()
        raw_html = data['choices'][0]['message']['content']
        
        # Clean up markdown formatting if the AI includes it
        raw_html = raw_html.replace("```html", "").replace("```", "").strip()
        
        # --- 3. CSS INLINING ---
        # This converts <style> tags into inline style='' attributes for email clients
        inlined_html = transform(raw_html)
        
        print("✅ Success! Email sent to browser.")
        return {"status": "success", "html": inlined_html}

    except Exception as e:
        print(f"⚠️ CRITICAL ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Staying on Port 8005 to avoid the 'Address in use' errors
    print("--- SERVER STARTING ON PORT 8005 ---")
    uvicorn.run(app, host="0.0.0.0", port=8005)