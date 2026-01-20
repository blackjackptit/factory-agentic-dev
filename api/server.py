#!/usr/bin/env python3
"""
Claude Code API Server
Connects your API to Claude Code CLI with full codebase context
"""

import subprocess
import json
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Claude Code API",
    description="API to communicate with Claude Code CLI"
)


class QueryRequest(BaseModel):
    prompt: str
    cwd: Optional[str] = "/Users/nghia.dinh/factory-agentic-dev"
    stream: Optional[bool] = False


class QueryResponse(BaseModel):
    response: str
    success: bool


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Send a prompt to Claude Code and get response.
    Claude Code will have full context of the codebase at cwd.
    """
    try:
        result = subprocess.run(
            [
                "claude",
                "--dangerously-skip-permissions",
                "--print",
                "-p", request.prompt
            ],
            cwd=request.cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        return QueryResponse(
            response=result.stdout,
            success=result.returncode == 0
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Claude Code timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    """
    Stream response from Claude Code using Server-Sent Events (SSE).
    """
    async def generate():
        process = await asyncio.create_subprocess_exec(
            "claude",
            "--dangerously-skip-permissions",
            "--print",
            "-p", request.prompt,
            cwd=request.cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        buffer = ""
        while True:
            chunk = await process.stdout.read(100)
            if not chunk:
                break
            buffer += chunk.decode()
            # Send accumulated text as SSE
            if buffer:
                yield f"data: {json.dumps({'text': buffer})}\n\n"
                buffer = ""

        await process.wait()
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.post("/query/stream/raw")
async def query_stream_raw(request: QueryRequest):
    """
    Stream raw text response from Claude Code.
    """
    async def generate():
        process = await asyncio.create_subprocess_exec(
            "claude",
            "--dangerously-skip-permissions",
            "--print",
            "-p", request.prompt,
            cwd=request.cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        while True:
            chunk = await process.stdout.read(100)
            if not chunk:
                break
            yield chunk.decode()

        await process.wait()

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
