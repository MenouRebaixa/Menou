from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import socketio
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import re
import random
import aiofiles

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'menou_rpg')]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# SocketIO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

security = HTTPBearer()

# ============ MODELS ============

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

class TableBase(BaseModel):
    name: str
    description: Optional[str] = ""
    grid_size: int = 30  # pixels per cell
    grid_scale: float = 1.5  # meters per cell
    show_grid: bool = True
    background_url: Optional[str] = None

class TableCreate(TableBase):
    pass

class TableResponse(TableBase):
    id: str
    master_id: str
    created_at: str
    players: List[str] = []

class Character3DT(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    table_id: str
    user_id: str
    name: str
    # Atributos 3D&T
    forca: int = 1
    habilidade: int = 1
    resistencia: int = 1
    armadura: int = 0
    poder_de_fogo: int = 0
    # Pontos
    pv_max: int = 5
    pv_current: int = 5
    pm_max: int = 5
    pm_current: int = 5
    # Outros
    vantagens: List[Dict[str, Any]] = []  # [{name, description, book_ref}]
    desvantagens: List[Dict[str, Any]] = []
    pericias: List[Dict[str, Any]] = []
    equipamentos: List[str] = []
    notas: str = ""
    avatar_url: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CharacterCreate(BaseModel):
    table_id: str
    name: str
    forca: int = 1
    habilidade: int = 1
    resistencia: int = 1

class TokenBase(BaseModel):
    name: str
    color: str = "#c5a059"
    size: int = 1  # size in grid cells
    image_url: Optional[str] = None
    visible_to_all: bool = True

class TokenCreate(TokenBase):
    table_id: str
    x: int = 0
    y: int = 0

class TokenResponse(TokenBase):
    id: str
    table_id: str
    x: int
    y: int
    created_at: str

class MessageBase(BaseModel):
    content: str
    message_type: str = "text"  # text, roll, system

class MessageCreate(MessageBase):
    table_id: str

class MessageResponse(MessageBase):
    id: str
    table_id: str
    user_id: str
    username: str
    timestamp: str

class DiceRollRequest(BaseModel):
    expression: str  # e.g., "2d6+3", "d20adv"
    table_id: str
    is_private: bool = False

class DiceRollResponse(BaseModel):
    expression: str
    result: int
    rolls: List[int]
    breakdown: str

class BookBase(BaseModel):
    title: str
    description: Optional[str] = ""
    file_url: Optional[str] = None
    link: Optional[str] = None

class BookCreate(BookBase):
    table_id: str

class BookResponse(BookBase):
    id: str
    table_id: str
    abilities_index: List[Dict[str, Any]] = []  # [{name, page, anchor}]
    created_at: str

class MusicTrackBase(BaseModel):
    title: str
    file_url: Optional[str] = None
    link: Optional[str] = None
    duration: Optional[int] = None

class MusicTrackCreate(MusicTrackBase):
    table_id: str

class MusicTrackResponse(MusicTrackBase):
    id: str
    table_id: str
    created_at: str

class InitiativeEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    table_id: str
    name: str
    initiative_value: int
    is_npc: bool = False
    character_id: Optional[str] = None
    hp_current: Optional[int] = None
    hp_max: Optional[int] = None
    notes: str = ""
    order_index: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class InitiativeCreate(BaseModel):
    table_id: str
    name: str
    initiative_value: int
    is_npc: bool = False
    character_id: Optional[str] = None
    hp_current: Optional[int] = None
    hp_max: Optional[int] = None
    notes: str = ""

class InitiativeState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    table_id: str
    entries: List[InitiativeEntry] = []
    current_turn_index: int = 0
    round_number: int = 1
    is_active: bool = False
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ============ AUTH UTILITIES ============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============ DICE ROLLER ============

def parse_and_roll_dice(expression: str) -> DiceRollResponse:
    expression = expression.lower().strip()
    rolls = []
    
    # Handle advantage/disadvantage
    if 'd20adv' in expression:
        r1, r2 = random.randint(1, 20), random.randint(1, 20)
        rolls = [r1, r2]
        result = max(r1, r2)
        breakdown = f"d20adv: [{r1}, {r2}] = {result}"
        return DiceRollResponse(expression=expression, result=result, rolls=rolls, breakdown=breakdown)
    
    if 'd20dis' in expression:
        r1, r2 = random.randint(1, 20), random.randint(1, 20)
        rolls = [r1, r2]
        result = min(r1, r2)
        breakdown = f"d20dis: [{r1}, {r2}] = {result}"
        return DiceRollResponse(expression=expression, result=result, rolls=rolls, breakdown=breakdown)
    
    # Parse standard notation: NdX+Y
    pattern = r'(\d*)d(\d+)([+\-]\d+)?'
    match = re.search(pattern, expression)
    
    if not match:
        raise ValueError("Invalid dice expression")
    
    num_dice = int(match.group(1)) if match.group(1) else 1
    die_size = int(match.group(2))
    modifier = int(match.group(3)) if match.group(3) else 0
    
    if num_dice > 100 or die_size > 1000:
        raise ValueError("Dice values too large")
    
    rolls = [random.randint(1, die_size) for _ in range(num_dice)]
    total = sum(rolls) + modifier
    
    breakdown = f"{num_dice}d{die_size}"
    if modifier:
        breakdown += f"{modifier:+d}"
    breakdown += f": {rolls}"
    if modifier:
        breakdown += f" {modifier:+d}"
    breakdown += f" = {total}"
    
    return DiceRollResponse(expression=expression, result=total, rolls=rolls, breakdown=breakdown)

# ============ API ROUTES ============

@api_router.get("/")
async def root():
    return {"message": "RPG Virtual Table API"}

# Auth routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "password_hash": hash_password(user_data.password),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    return UserResponse(
        id=user_id,
        email=user_data.email,
        username=user_data.username,
        created_at=user_doc["created_at"]
    )

@api_router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    user = await db.users.find_one({"email": login_data.email}, {"_id": 0})
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user["id"])
    return LoginResponse(
        token=token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            created_at=user["created_at"]
        )
    )

# Table routes
@api_router.post("/tables", response_model=TableResponse)
async def create_table(table_data: TableCreate, current_user: dict = Depends(get_current_user)):
    table_id = str(uuid.uuid4())
    table_doc = {
        "id": table_id,
        "master_id": current_user["id"],
        "name": table_data.name,
        "description": table_data.description,
        "grid_size": table_data.grid_size,
        "grid_scale": table_data.grid_scale,
        "show_grid": table_data.show_grid,
        "players": [current_user["id"]],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.tables.insert_one(table_doc)
    return TableResponse(**{k: v for k, v in table_doc.items() if k != '_id'})

@api_router.get("/tables", response_model=List[TableResponse])
async def list_tables(current_user: dict = Depends(get_current_user)):
    tables = await db.tables.find(
        {"$or": [{"master_id": current_user["id"]}, {"players": current_user["id"]}]},
        {"_id": 0}
    ).to_list(100)
    return tables

@api_router.get("/tables/{table_id}", response_model=TableResponse)
async def get_table(table_id: str, current_user: dict = Depends(get_current_user)):
    table = await db.tables.find_one({"id": table_id}, {"_id": 0})
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@api_router.put("/tables/{table_id}/background")
async def update_table_background(table_id: str, background_url: dict, current_user: dict = Depends(get_current_user)):
    table = await db.tables.find_one({"id": table_id}, {"_id": 0})
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Only master can update
    if table["master_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only master can update table settings")
    
    await db.tables.update_one(
        {"id": table_id},
        {"$set": {"background_url": background_url.get("url", "")}}
    )
    
    return {"message": "Background updated", "background_url": background_url.get("url", "")}

# Character routes
@api_router.post("/characters", response_model=Character3DT)
async def create_character(char_data: CharacterCreate, current_user: dict = Depends(get_current_user)):
    char_id = str(uuid.uuid4())
    pv_max = char_data.resistencia * 5
    pm_max = char_data.resistencia * 5
    
    char_doc = {
        "id": char_id,
        "table_id": char_data.table_id,
        "user_id": current_user["id"],
        "name": char_data.name,
        "forca": char_data.forca,
        "habilidade": char_data.habilidade,
        "resistencia": char_data.resistencia,
        "armadura": 0,
        "poder_de_fogo": 0,
        "pv_max": pv_max,
        "pv_current": pv_max,
        "pm_max": pm_max,
        "pm_current": pm_max,
        "vantagens": [],
        "desvantagens": [],
        "pericias": [],
        "equipamentos": [],
        "notas": "",
        "avatar_url": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.characters.insert_one(char_doc)
    return Character3DT(**{k: v for k, v in char_doc.items() if k != '_id'})

@api_router.get("/characters/table/{table_id}", response_model=List[Character3DT])
async def list_characters_by_table(table_id: str, current_user: dict = Depends(get_current_user)):
    characters = await db.characters.find({"table_id": table_id}, {"_id": 0}).to_list(100)
    return characters

@api_router.put("/characters/{char_id}", response_model=Character3DT)
async def update_character(char_id: str, char_data: Character3DT, current_user: dict = Depends(get_current_user)):
    char = await db.characters.find_one({"id": char_id}, {"_id": 0})
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    
    update_doc = char_data.model_dump()
    await db.characters.update_one({"id": char_id}, {"$set": update_doc})
    return char_data

# Token routes
@api_router.post("/tokens", response_model=TokenResponse)
async def create_token(token_data: TokenCreate, current_user: dict = Depends(get_current_user)):
    token_id = str(uuid.uuid4())
    token_doc = {
        "id": token_id,
        "table_id": token_data.table_id,
        "name": token_data.name,
        "color": token_data.color,
        "size": token_data.size,
        "image_url": token_data.image_url,
        "visible_to_all": token_data.visible_to_all,
        "x": token_data.x,
        "y": token_data.y,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.tokens.insert_one(token_doc)
    return TokenResponse(**{k: v for k, v in token_doc.items() if k != '_id'})

@api_router.get("/tokens/table/{table_id}", response_model=List[TokenResponse])
async def list_tokens(table_id: str, current_user: dict = Depends(get_current_user)):
    tokens = await db.tokens.find({"table_id": table_id}, {"_id": 0}).to_list(100)
    return tokens

@api_router.delete("/tokens/{token_id}")
async def delete_token(token_id: str, current_user: dict = Depends(get_current_user)):
    await db.tokens.delete_one({"id": token_id})
    return {"message": "Token deleted"}

# Chat routes
@api_router.post("/messages", response_model=MessageResponse)
async def create_message(msg_data: MessageCreate, current_user: dict = Depends(get_current_user)):
    msg_id = str(uuid.uuid4())
    msg_doc = {
        "id": msg_id,
        "table_id": msg_data.table_id,
        "user_id": current_user["id"],
        "username": current_user["username"],
        "content": msg_data.content,
        "message_type": msg_data.message_type,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    await db.messages.insert_one(msg_doc)
    return MessageResponse(**{k: v for k, v in msg_doc.items() if k != '_id'})

@api_router.get("/messages/table/{table_id}", response_model=List[MessageResponse])
async def list_messages(table_id: str, current_user: dict = Depends(get_current_user)):
    messages = await db.messages.find({"table_id": table_id}, {"_id": 0}).sort("timestamp", 1).to_list(500)
    return messages

# Dice routes
@api_router.post("/dice/roll", response_model=DiceRollResponse)
async def roll_dice(roll_data: DiceRollRequest, current_user: dict = Depends(get_current_user)):
    try:
        result = parse_and_roll_dice(roll_data.expression)
        
        # Save to chat if not private
        if not roll_data.is_private:
            msg_doc = {
                "id": str(uuid.uuid4()),
                "table_id": roll_data.table_id,
                "user_id": current_user["id"],
                "username": current_user["username"],
                "content": result.breakdown,
                "message_type": "roll",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await db.messages.insert_one(msg_doc)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Book routes
@api_router.post("/books", response_model=BookResponse)
async def create_book(book_data: BookCreate, current_user: dict = Depends(get_current_user)):
    book_id = str(uuid.uuid4())
    book_doc = {
        "id": book_id,
        "table_id": book_data.table_id,
        "title": book_data.title,
        "description": book_data.description,
        "file_url": book_data.file_url,
        "link": book_data.link,
        "abilities_index": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.books.insert_one(book_doc)
    return BookResponse(**{k: v for k, v in book_doc.items() if k != '_id'})

@api_router.get("/books/table/{table_id}", response_model=List[BookResponse])
async def list_books(table_id: str, current_user: dict = Depends(get_current_user)):
    books = await db.books.find({"table_id": table_id}, {"_id": 0}).to_list(100)
    return books

# Music routes
@api_router.post("/music", response_model=MusicTrackResponse)
async def create_music(music_data: MusicTrackCreate, current_user: dict = Depends(get_current_user)):
    music_id = str(uuid.uuid4())
    music_doc = {
        "id": music_id,
        "table_id": music_data.table_id,
        "title": music_data.title,
        "file_url": music_data.file_url,
        "link": music_data.link,
        "duration": music_data.duration,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.music.insert_one(music_doc)
    return MusicTrackResponse(**{k: v for k, v in music_doc.items() if k != '_id'})

@api_router.get("/music/table/{table_id}", response_model=List[MusicTrackResponse])
async def list_music(table_id: str, current_user: dict = Depends(get_current_user)):
    tracks = await db.music.find({"table_id": table_id}, {"_id": 0}).to_list(100)
    return tracks

# Initiative routes
@api_router.get("/initiative/table/{table_id}")
async def get_initiative_state(table_id: str, current_user: dict = Depends(get_current_user)):
    state = await db.initiative_states.find_one({"table_id": table_id}, {"_id": 0})
    if not state:
        # Create default state
        default_state = {
            "id": str(uuid.uuid4()),
            "table_id": table_id,
            "entries": [],
            "current_turn_index": 0,
            "round_number": 1,
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        await db.initiative_states.insert_one(default_state)
        return default_state
    return state

@api_router.post("/initiative/entry")
async def add_initiative_entry(entry_data: InitiativeCreate, current_user: dict = Depends(get_current_user)):
    # Get current state
    state = await db.initiative_states.find_one({"table_id": entry_data.table_id}, {"_id": 0})
    if not state:
        state = {
            "id": str(uuid.uuid4()),
            "table_id": entry_data.table_id,
            "entries": [],
            "current_turn_index": 0,
            "round_number": 1,
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    # Create new entry
    new_entry = {
        "id": str(uuid.uuid4()),
        "table_id": entry_data.table_id,
        "name": entry_data.name,
        "initiative_value": entry_data.initiative_value,
        "is_npc": entry_data.is_npc,
        "character_id": entry_data.character_id,
        "hp_current": entry_data.hp_current,
        "hp_max": entry_data.hp_max,
        "notes": entry_data.notes,
        "order_index": len(state["entries"]),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    state["entries"].append(new_entry)
    
    # Sort by initiative_value (descending)
    state["entries"].sort(key=lambda x: x["initiative_value"], reverse=True)
    
    # Update order_index
    for idx, entry in enumerate(state["entries"]):
        entry["order_index"] = idx
    
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Upsert state
    await db.initiative_states.update_one(
        {"table_id": entry_data.table_id},
        {"$set": state},
        upsert=True
    )
    
    return state

@api_router.delete("/initiative/entry/{entry_id}")
async def remove_initiative_entry(entry_id: str, table_id: str, current_user: dict = Depends(get_current_user)):
    state = await db.initiative_states.find_one({"table_id": table_id}, {"_id": 0})
    if not state:
        raise HTTPException(status_code=404, detail="Initiative state not found")
    
    state["entries"] = [e for e in state["entries"] if e["id"] != entry_id]
    
    # Update order_index
    for idx, entry in enumerate(state["entries"]):
        entry["order_index"] = idx
    
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.initiative_states.update_one(
        {"table_id": table_id},
        {"$set": state}
    )
    
    return state

@api_router.post("/initiative/next-turn/{table_id}")
async def next_turn(table_id: str, current_user: dict = Depends(get_current_user)):
    state = await db.initiative_states.find_one({"table_id": table_id}, {"_id": 0})
    if not state:
        raise HTTPException(status_code=404, detail="Initiative state not found")
    
    if not state["entries"]:
        raise HTTPException(status_code=400, detail="No entries in initiative")
    
    state["current_turn_index"] = (state["current_turn_index"] + 1) % len(state["entries"])
    
    # Increment round if we wrapped around
    if state["current_turn_index"] == 0:
        state["round_number"] += 1
    
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.initiative_states.update_one(
        {"table_id": table_id},
        {"$set": state}
    )
    
    return state

@api_router.post("/initiative/start/{table_id}")
async def start_initiative(table_id: str, current_user: dict = Depends(get_current_user)):
    state = await db.initiative_states.find_one({"table_id": table_id}, {"_id": 0})
    if not state:
        raise HTTPException(status_code=404, detail="Initiative state not found")
    
    state["is_active"] = True
    state["current_turn_index"] = 0
    state["round_number"] = 1
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.initiative_states.update_one(
        {"table_id": table_id},
        {"$set": state}
    )
    
    return state

@api_router.post("/initiative/reset/{table_id}")
async def reset_initiative(table_id: str, current_user: dict = Depends(get_current_user)):
    state = await db.initiative_states.find_one({"table_id": table_id}, {"_id": 0})
    if not state:
        raise HTTPException(status_code=404, detail="Initiative state not found")
    
    state["entries"] = []
    state["current_turn_index"] = 0
    state["round_number"] = 1
    state["is_active"] = False
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.initiative_states.update_one(
        {"table_id": table_id},
        {"$set": state}
    )
    
    return state

@api_router.put("/initiative/entry/{entry_id}")
async def update_initiative_entry(entry_id: str, table_id: str, updates: dict, current_user: dict = Depends(get_current_user)):
    state = await db.initiative_states.find_one({"table_id": table_id}, {"_id": 0})
    if not state:
        raise HTTPException(status_code=404, detail="Initiative state not found")
    
    for entry in state["entries"]:
        if entry["id"] == entry_id:
            entry.update(updates)
            break
    
    # Re-sort if initiative_value changed
    if "initiative_value" in updates:
        state["entries"].sort(key=lambda x: x["initiative_value"], reverse=True)
        for idx, entry in enumerate(state["entries"]):
            entry["order_index"] = idx
    
    state["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.initiative_states.update_one(
        {"table_id": table_id},
        {"$set": state}
    )
    
    return state

# ============ WEBSOCKET EVENTS ============

@sio.event
async def connect(sid, environ):
    logging.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logging.info(f"Client disconnected: {sid}")

@sio.event
async def join_table(sid, data):
    table_id = data.get('table_id')
    await sio.enter_room(sid, table_id)
    await sio.emit('user_joined', {'sid': sid}, room=table_id, skip_sid=sid)

@sio.event
async def leave_table(sid, data):
    table_id = data.get('table_id')
    await sio.leave_room(sid, table_id)
    await sio.emit('user_left', {'sid': sid}, room=table_id)

@sio.event
async def token_moved(sid, data):
    table_id = data.get('table_id')
    # Update token position in database
    token_id = data.get('token_id')
    x = data.get('x')
    y = data.get('y')
    
    await db.tokens.update_one({"id": token_id}, {"$set": {"x": x, "y": y}})
    
    # Broadcast to all clients in table
    await sio.emit('token_updated', data, room=table_id, skip_sid=sid)

@sio.event
async def chat_message(sid, data):
    table_id = data.get('table_id')
    await sio.emit('new_message', data, room=table_id)

@sio.event
async def dice_rolled(sid, data):
    table_id = data.get('table_id')
    await sio.emit('dice_result', data, room=table_id)

@sio.event
async def initiative_updated(sid, data):
    table_id = data.get('table_id')
    await sio.emit('initiative_changed', data, room=table_id, skip_sid=sid)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],  # Permite todas as origens
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount SocketIO
socket_app = socketio.ASGIApp(sio, app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()