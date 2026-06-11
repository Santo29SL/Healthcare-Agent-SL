import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.app import triagent, users, medical_profile_user, doctorconnect, store_conversation
from backend.app.database import get_connection
from backend.app.agents import agent 

app = FastAPI(title="AgenticHealthAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class SignupRequest(BaseModel):
    name: str; email: str; password: str; blood_group: str; allergies: str

class LoginRequest(BaseModel):
    email: str; password: str

class UserQuery(BaseModel):
    user_id: int; query: str

class ProfileUpdate(BaseModel):
    user_id: int; blood_group: str; allergies: str

@app.post("/signup")
def signup(data: SignupRequest):
    try:
        user_id = users.create_user(data.name, data.email, data.password)
        medical_profile_user.create_medical_profiles(user_id, data.blood_group, data.allergies)
        return {"id": user_id, "name": data.name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(data: LoginRequest):
    user = users.get_user(data.email, data.password)
    if user:
        profile = medical_profile_user.get_medical_profiles(user[0])
        return {
            "id": user[0], "name": user[1], "email": user[2],
            "profile": {"blood_group": profile[0][2], "allergies": profile[0][3]} if profile else None
        }
    raise HTTPException(status_code=401)

@app.post("/update-profile")
def update_profile(data: ProfileUpdate):
    try:
        medical_profile_user.update_medical_profiles(data.user_id, data.blood_group, data.allergies)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{user_id}")
def get_history(user_id: int):
    try:
        # Targeting the 'conversation' database as per your store_conversation.py
        conn = get_connection("conversation")
        try:
            cursor = conn.cursor()
            try:
                query = "SELECT message, created_at FROM conversations WHERE user_id = %s AND role = 'user' ORDER BY created_at DESC LIMIT 10"
                cursor.execute(query, (user_id,))
                rows = cursor.fetchall()
                return [{"query": r[0], "time": r[1].strftime("%Y-%m-%d %H:%M")} for r in rows]
            finally:
                cursor.close()
        finally:
            conn.close()
    except: return []

@app.post("/triage")
def triage(data: UserQuery):
    return triagent.check_risk(data.query)

@app.post("/chat")
def chat(data: UserQuery):
    """Communicates with the AI Agent and logs the conversation."""
    # Store user message
    store_conversation.store_conversation(data.user_id, "user", data.query)
    
    # Get agent response
    raw_response = agent.get_response(data.query, user_id=str(data.user_id))
    
    # Simple logic to ensure the response can be split into PubMed and AI segments
    # The frontend expects a double newline '\n\n' to segregate blocks
    if "\n\n" not in raw_response:
        formatted_response = f"Literature Summary: Information retrieved.\n\nClinical Interpretation: {raw_response}"
    else:
        formatted_response = raw_response

    # Store AI response
    store_conversation.store_conversation(data.user_id, "assistant", formatted_response)
    
    return {"response": formatted_response}

@app.get("/doctors")
def get_doctors(lat: float, lon: float):
    return [{"name": d[0], "specialty": d[1], "phone": d[2], "dist": d[3]} for d in doctorconnect.find_nearest_doctors(lat, lon)]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)






