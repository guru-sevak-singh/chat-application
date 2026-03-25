from fastapi import FastAPI, status
from contextlib import asynccontextmanager  # for the message worker

from database import engine

from models import Base

from routers import users, auth, sockets, application, rooms, messages, web_rtc

from fastapi.staticfiles import StaticFiles

from workers.message_worker import start_worker

# @asynccontextmanager
# async def lifespan(app : FastAPI):
#     start_worker()
#     print("App Start working")
#     yield
#     print("App Shouting Down")


# app = FastAPI(lifespan=lifespan)


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(users.router)
app.include_router(auth.router)
app.include_router(application.router)
app.include_router(sockets.router)
app.include_router(rooms.router)
app.include_router(web_rtc.router)
# app.include_router(messages.router)


@app.get("/health-check", status_code=status.HTTP_200_OK)
def health_check():
    return {"healthy-status": True}


Base.metadata.create_all(bind=engine)
