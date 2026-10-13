from fastapi import FastAPI

app = FastAPI(title="keepy")


@app.get("/")
async def root():
    return {"message": "Hello, keepy!"}
