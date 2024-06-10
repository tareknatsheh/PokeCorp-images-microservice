import io
from fastapi import FastAPI
from routes import images

app = FastAPI()

@app.get("/", include_in_schema=False)
def main():
    return "Server up and running"

app.include_router(images.router, prefix="/images", tags=["Imges endpoints"])

