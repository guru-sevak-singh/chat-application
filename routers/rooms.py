from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from utils import db_dependency, user_dependency
from models import Users, Rooms, connected_users, Messages

router = APIRouter(
    prefix='/rooms',
    tags=['Rooms']
)

class ConnectUser(BaseModel):
    phone_number : str


@router.get("/")
def get_all_rooms(user : user_dependency, db : db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorised Access')
    
    current_user = db.query(Users).filter(Users.id == user.id).first()
    rooms = current_user.rooms

    return_data = []

    for room in rooms:
        room_data = {
            "id": room.id,
        }

        other_user = next(user for user in room.users if user != current_user)

        return_data.append({
                "id": room.id,
                "phone_number": other_user.phone_number,
                "name": other_user.name
            })

    return return_data           


@router.post("/create-room/{phone_number}", status_code=status.HTTP_201_CREATED)
def create_room(user : user_dependency, db : db_dependency, phone_number : str):

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorised Access')
    
    if user.phone_number == phone_number:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can't create room with own")

    current_user = db.query(Users).filter(Users.id == user.id).first()
    
    another_user = db.query(Users).filter(Users.phone_number == phone_number).first()
    if not another_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'There is not user with Phone Number : {phone_number}')

    room = (
        db.query(Rooms)
        .join(connected_users, Rooms.id == connected_users.c.room_id)
        .filter(connected_users.c.user_id == current_user.id)
        .filter(Rooms.id.in_(
            db.query(connected_users.c.room_id)
            .filter(connected_users.c.user_id == another_user.id)
        ))
        .first()
    )

    if room:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Room Already Exists')

    new_room = Rooms()
    new_room.users.append(current_user)
    new_room.users.append(another_user)
    db.add(new_room)
    db.commit()

    return {"detail": "New Room Created Successfully"}

@router.get('/all-messages')
def get_messages(db: db_dependency):
    return db.query(Messages).all()