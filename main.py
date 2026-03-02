from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from query_data import search_walled_garden_stream # Import the NEW async function

app = FastAPI(title="Group 50: DSA Walled Garden API")

# Setup CORS (Standardized)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    prompt: str

@app.get("/")
def health_check():
    return {"status": "online", "model": "llama3.2-3b"}

@app.post("/ask")
async def ask_question(request: QueryRequest):
    try:
        # We return a StreamingResponse.
        # This keeps the connection open until the LLM finishes typing.
        return StreamingResponse(
            search_walled_garden_stream(request.prompt),
            media_type="text/plain"
        )
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
