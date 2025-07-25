from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import json
import os
import bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("FERNET_KEY").encode()  # convert string back to bytes

# fernet instance
fernet = Fernet(key)

DATA_FILE = "seedData.json"

# FastApi instance
app = FastAPI()

# pydantic model for Snippet


class Snippet(BaseModel):
    id: int
    language: str
    code: str

# pydantic model for Snippet when creating a new object


class SnippetCreate(BaseModel):
    language: str
    code: str

# pydantic model for User


class User(BaseModel):
    id: int
    email: str
    password: str

# pydantic model for User when creating a new user or logging an existing user in


class UserAuth(BaseModel):
    email: str
    password: str

# Function to load data from the JSON file


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"snippets": [], "users": []}

# Function to save data to the JSON file


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# GET all snippets or by specific language parameter if passed in


@app.get("/snippets", response_model=List[Snippet])
def get_snippets(language: Optional[str] = Query(None)):
    data = load_data()
    snippets = data.get("snippets", [])
    if language:
        snippets = [s for s in snippets if s["language"].lower() ==
                    language.lower()]
    for snippet in snippets:
        # decrypts the code
        snippet['code'] = fernet.decrypt(snippet['code'].encode()).decode()
    return snippets

# GET snippet by id


@app.get("/snippets/{snippet_id}", response_model=Snippet)
def get_snippet(snippet_id: int):
    data = load_data()
    snippets = data.get("snippets", [])

    # get the individual snippet you are looking for
    for snippet in snippets:
        if snippet["id"] == snippet_id:
            # decrypts the code
            snippet['code'] = fernet.decrypt(snippet['code'].encode()).decode()
            return snippet
    raise HTTPException(status_code=404, detail="Snippet not found")


# POST new snippet


@app.post("/snippets", response_model=Snippet, status_code=201)
def create_snippet(snippet: SnippetCreate):
    data = load_data()
    snippets = data.setdefault("snippets", [])

    snippet_id = max([s['id'] for s in snippets], default=0) + 1
    # encypt the code before storing
    encrypted_code = fernet.encrypt(snippet.code.encode()).decode()

    new_snippet = Snippet(
        id=snippet_id,
        language=snippet.language,
        code=encrypted_code
    )

    snippets.append(new_snippet.model_dump())
    save_data(data)
    return new_snippet


# POST new user
@app.post("/user", status_code=201)
def create_user(user: UserAuth):
    data = load_data()
    users = data.setdefault("users", [])

    # get new user id
    user_id = max([u['id'] for u in users], default=0) + 1

    # generate salt
    salt = bcrypt.gensalt()

    # hash the password
    hashed_password = bcrypt.hashpw(user.password.encode(), salt)

    # create new user instance
    new_user = User(
        id=user_id,
        email=user.email,
        password=hashed_password.decode()
    )

    # append new user and save to json file
    users.append(new_user.model_dump())
    save_data(data)
    return {"message": "New user successfully created!", "user": new_user.email}

# Login user


@app.post("/user/login")
def login_user(user: UserAuth):
    data = load_data()
    users = data.get("users", [])

    found_user = next((u for u in users if u["email"] == user.email), None)

    # first checks if user exists and then compares passwords
    if not found_user or not bcrypt.checkpw(user.password.encode(), found_user["password"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # login was successful
    return {
        "message": "Login successful",
        "user": found_user["email"]
    }
