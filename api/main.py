from fastapi import FastAPI
from api.routers import author_router, book_router, storing_information_router

app = FastAPI()


app.include_router(author_router.router, prefix="/authors", tags=["authors"])
app.include_router(book_router.router, prefix="/books", tags=["books"])
app.include_router(storing_information_router.router, prefix="/storing", tags=["storing"])


@app.get("/ping")
async def ping():
    return {"message": "pong"}


def exe(host, port):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    exe('localhost', 8000)
