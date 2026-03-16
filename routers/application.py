from fastapi import APIRouter, Request, status, HTTPException
from fastapi.templating import Jinja2Templates
from utils import user_dependency

router = APIRouter(
    tags=['Application views']
)

templates = Jinja2Templates(directory="templates")

@router.get("/", status_code=status.HTTP_200_OK)
def index(request : Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)

@router.get("/login")
def login_template(request : Request):
    context = {"request": request}
    return templates.TemplateResponse("login.html", context)

@router.get("/register")
def register_template(request : Request):
    context = {"request": request}
    return templates.TemplateResponse("register.html", context)
