from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlite3
import os

app = FastAPI()

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE = 'identity_verification.db'

# Ensure the database file exists
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            verified BOOLEAN NOT NULL DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE verification_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    # Seed data
    cursor.execute("INSERT INTO users (name, email, verified) VALUES ('John Doe', 'john@example.com', 0)")
    cursor.execute("INSERT INTO users (name, email, verified) VALUES ('Jane Smith', 'jane@example.com', 1)")
    conn.commit()
    conn.close()

# Data models
class User(BaseModel):
    id: int
    name: str
    email: str
    verified: bool

class VerificationRequest(BaseModel):
    request_id: int
    user_id: int
    status: str
    timestamp: datetime

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_home():
    return templates.TemplateResponse("index.html", {"request": {}})

@app.get("/register", response_class=HTMLResponse)
async def read_register():
    return templates.TemplateResponse("register.html", {"request": {}})

@app.get("/verify", response_class=HTMLResponse)
async def read_verify():
    return templates.TemplateResponse("verify.html", {"request": {}})

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard():
    return templates.TemplateResponse("dashboard.html", {"request": {}})

@app.get("/api-docs", response_class=HTMLResponse)
async def read_api_docs():
    return templates.TemplateResponse("api_docs.html", {"request": {}})

# API Endpoints
@app.post("/api/register", response_model=User)
async def register_user(user: User):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, verified) VALUES (?, ?, ?)", (user.name, user.email, user.verified))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return {"id": user_id, "name": user.name, "email": user.email, "verified": user.verified}

@app.get("/api/verify/{user_id}", response_model=VerificationRequest)
async def verify_user(user_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Simulate verification process
    status = "verified" if user[3] else "unverified"
    timestamp = datetime.now()
    cursor.execute("INSERT INTO verification_requests (user_id, status, timestamp) VALUES (?, ?, ?)", (user_id, status, timestamp))
    conn.commit()
    request_id = cursor.lastrowid
    conn.close()
    return {"request_id": request_id, "user_id": user_id, "status": status, "timestamp": timestamp}

@app.get("/api/users", response_model=List[User])
async def get_users():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return [{"id": user[0], "name": user[1], "email": user[2], "verified": bool(user[3])} for user in users]

@app.put("/api/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name = ?, email = ?, verified = ? WHERE id = ?", (user.name, user.email, user.verified, user_id))
    conn.commit()
    conn.close()
    return user

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"detail": "User deleted"}
