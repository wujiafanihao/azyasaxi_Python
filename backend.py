from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile,HTTPException,Request
# from chains import text_generate_model,docs_generate_model
from chains import text_generate_model
import uvicorn
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from colorama import init
import os
import shutil
import re

# 加载环境变量
load_dotenv()
# 初始化 colorama
init()

# 创建用户模型
class User(BaseModel):
    username: str
    password: str

# 创建FastAPI应用实例
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许来自该源的请求
    allow_credentials=True,
    allow_methods=["POST"],  # 只允许 POST 方法
    allow_headers=["*"],
)


# 文件存储路径
userdata_dir = "userdata"
username_file = os.path.join(userdata_dir, "user.txt")
password_file = os.path.join(userdata_dir, "password.txt")

# 创建存储目录
os.makedirs(userdata_dir, exist_ok=True)

# 登录路由
@app.post("/login")
async def login(user: User):
    # 从请求体提取 username 和 password
    username = user.username
    password = user.password
    
    # 检查用户名和密码是否匹配
    if not os.path.exists(username_file) or not os.path.exists(password_file):
        raise HTTPException(status_code=401, detail="User data not found")

    with open(username_file, "r") as uf, open(password_file, "r") as pf:
        usernames = [line.strip() for line in uf.readlines()]  # 去除每行末尾的换行符
        passwords = [line.strip() for line in pf.readlines()]  # 去除每行末尾的换行符
        for stored_username, stored_password in zip(usernames, passwords):
            if username == stored_username and password == stored_password:
                return JSONResponse(content={"message": "Login successful"})
    
    raise HTTPException(status_code=401, detail="Invalid username or password")

# 注册路由
@app.post("/register")
async def register(request: Request):
    data = await request.json()
    username = data.get("username")
    password = data.get("password")

    # 检查用户名是否为邮箱格式
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, username):
        raise HTTPException(status_code=400, detail="Username must be in email format")

    # 检查密码是否符合要求
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    if not re.match(password_regex, password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter, one lowercase letter, one number, one special character, and be at least 8 characters long")

    # 检查用户名是否已存在
    if os.path.exists(username_file):
        with open(username_file, "r") as f:
            if username in f.read():
                raise HTTPException(status_code=400, detail="Username already exists")

    # 保存用户名和密码
    with open(username_file, "a") as f:
        f.write(username + "\n")
    with open(password_file, "a") as f:
        f.write(password + "\n")

    return JSONResponse(content={"message": "Registration successful"})

# def clear_and_create_uploads_dir():
#     """清空并重新创建 uploads 目录"""
#     if os.path.exists(UPLOAD_DIRECTORY):
#         shutil.rmtree(UPLOAD_DIRECTORY)
#     os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# UPLOAD_DIRECTORY = "uploads"
# @app.post("/upload")
# async def upload_file(file: UploadFile = File(...)):
#     # 判断是否有文件被上传
#     if not file:
#         raise HTTPException(status_code=400, detail="No file uploaded")

#     # 创建 uploads 目录(如果不存在)
#     os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

#     # 获取文件名
#     file_name = file.filename

#     # 创建文件路径以保存上传的文件
#     file_path = os.path.join(UPLOAD_DIRECTORY, file_name)

#     # 保存上传的文件到指定位置
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # 返回成功消息
#     return JSONResponse(content={"message": f"File '{file_name}' uploaded successfully"})


# upload_directory = "uploads"
# 定义一个POST路由，用于处理用户提问
@app.post("/v1/chat/completions", response_class=StreamingResponse)
async def ask(body: dict):
    # if os.path.exists(upload_directory) and os.path.isdir(upload_directory):
    #     files = os.listdir(upload_directory)
    #     pdf_files = [file for file in files if file.lower().endswith(".pdf")]
    #     if pdf_files:
    #         return StreamingResponse(docs_generate_model(body['question']), media_type="text/event-stream")
    #     else:
    return StreamingResponse(text_generate_model(body['question']), media_type="text/event-stream")

# 程序入口点
if __name__ == "__main__":
    # clear_and_create_uploads_dir()
    uvicorn.run("backend:app", host="127.0.0.1", port=8088, reload=True, log_level="debug")
