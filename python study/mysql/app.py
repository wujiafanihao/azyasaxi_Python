from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import mysql.connector
import uvicorn

app = FastAPI()

# 连接到 MySQL 数据库
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="251605",
    database="auth"
)

# 初始化模板
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/set_username", response_class=HTMLResponse)
async def set_username(request: Request, username: str):
    # 在数据库中插入用户名
    cursor = db.cursor()
    query = "INSERT INTO users (username) VALUES (%s)"
    cursor.execute(query, (username,))
    db.commit()
    cursor.close()

    return templates.TemplateResponse("username_set.html", {"request": request, "username": username})
