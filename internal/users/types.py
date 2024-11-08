from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    display_name: str
    email: str
    phone_number: str
    country: str
    lang: str
    hashed_password: str
