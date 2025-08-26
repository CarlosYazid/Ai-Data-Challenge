from fastapi import FastAPI

from routes import AgentRouter

app = FastAPI()
app.include_router(AgentRouter)

@app.get("/")
async def root():
    return {"status": "Ok"}