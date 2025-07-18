from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import json
import os

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

# Function to load data from the JSON file


def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return []

# Function to save data to the JSON file


def save_data(snippets):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(snippets, f, indent=4)

# GET all snippets or by specific language parameter if passed in


@app.get("/snippets", response_model=List[Snippet])
def get_snippets(language: Optional[str] = Query(None)):
    snippets = load_data()
    if language:
        snippets = [s for s in snippets if s["language"].lower() ==
                    language.lower()]
    return snippets

# GET snippet by id


@app.get("/snippets/{snippet_id}", response_model=Snippet)
def get_snippet(snippet_id: int):
    # get all snippets in json file
    snippets = load_data()

    # get the individual snippet you are looking for
    for snippet in snippets:
        if snippet["id"] == snippet_id:
            return snippet
    raise HTTPException(status_code=404, detail="Snippet not found")

# GET snippets by passed in language parameter


# POST new snippet


@app.post("/snippets", response_model=Snippet, status_code=201)
def create_snippet(snippet: SnippetCreate):
    snippets = load_data()

    snippet_id = max([s['id'] for s in snippets], default=0) + 1
    new_snippet = Snippet(
        id=snippet_id,
        language=snippet.language,
        code=snippet.code
    )

    snippets.append(new_snippet.model_dump())
    save_data(snippets)
    return new_snippet
