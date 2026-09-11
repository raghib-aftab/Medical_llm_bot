from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from vllm import LLM
from vllm.sampling_params import SamplingParams
from vllm.entrypoints.chat_utils import ChatCompletionMessageParam
from typing import List, Optional
from contextlib import asynccontextmanager

# Default values
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 512


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: Optional[str] = "rishabh9559/medical-llama-3.2-3B"
    messages: List[Message]
    temperature: Optional[float] = DEFAULT_TEMPERATURE
    max_tokens: Optional[int] = DEFAULT_MAX_TOKENS


class ModelManager:
    """Manages the LLM instance"""
    def __init__(self):
        self.llm: Optional[LLM] = None
    
    def load(self):
        print("Loading model...")
        self.llm = LLM(
            model="rishabh9559/medical-llama-3.2-3B",
            trust_remote_code=True,
            max_model_len=4096,
            gpu_memory_utilization=0.9,
            dtype="auto",
        )
        print("Model loaded successfully!")
    
    def get_llm(self) -> LLM:
        if self.llm is None:
            raise RuntimeError("Model not loaded")
        return self.llm


# Global model manager
model_manager = ModelManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load model
    model_manager.load()
    yield
    # Shutdown: Cleanup (if needed)


app = FastAPI(title="Medical LLaMA API", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/predict")
async def chat_completions(request: ChatRequest):
    # Get the loaded model
    try:
        llm = model_manager.get_llm()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    
    # Convert to vLLM's expected format
    messages: list[ChatCompletionMessageParam] = [
        {"role": m.role, "content": m.content}  # type: ignore[misc]
        for m in request.messages
    ]
    
    # Use defaults if None is provided
    temperature = request.temperature if request.temperature is not None else DEFAULT_TEMPERATURE
    max_tokens = request.max_tokens if request.max_tokens is not None else DEFAULT_MAX_TOKENS
    
    sampling_params = SamplingParams(
        temperature=temperature,
        max_tokens=max_tokens,
    )

    try:
        outputs = llm.chat(
            messages=messages,
            sampling_params=sampling_params,
        )
        
        output_text = outputs[0].outputs[0].text if outputs and outputs[0].outputs else ""
        
    except Exception as e:
        output_text = f"Error: {str(e)}"

    return {
        "id": "chatcmpl-medical",
        "object": "chat.completion",
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output_text
                },
                "finish_reason": "stop"
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)