from fastapi import FastAPI


from app.routers import users, security,students, buildings, rooms
from app.routers import schedules,credit,teachers,credit, Enrollment
# app = FastAPI(dependencies=[Depends(get_query_token)])
app = FastAPI()


app.include_router(users.router)
app.include_router(security.router)
app.include_router(students.router)
app.include_router(buildings.router)
app.include_router(rooms.router)
app.include_router(schedules.router)
app.include_router(Enrollment.router)
app.include_router(credit.router)
app.include_router(teachers.router)
app.include_router(credit.router)

# app.include_router(items.router)
# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}