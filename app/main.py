from fastapi import FastAPI
from app.repositories.user_repository import UserRepository

app = FastAPI()

@app.get("/hello_world")
def hello_world():
    a = UserRepository.create(("test1@test.com", "Test1", "12345678"), "w4ed5rf6tg7yh8uj9iko")
    return {'message': f'{a}'}