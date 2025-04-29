from fastapi import FastAPI
from v1.auth.router import auth_router
from v1.emails.router import emails_router

# Creates the FASTAPI Application object
app = FastAPI()

app.include_router(auth_router, prefix="/v1")
app.include_router(emails_router, prefix="/v1")


# v1 endpoint
@app.get("/v1")
async def main():
    return {'message': 'Hello, from main'}