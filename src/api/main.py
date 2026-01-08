"""Main FastAPI application with Gradio UI."""

import gradio as gr
from fastapi import FastAPI

from src.api.routes import router as api_router
from src.ui.gradio_app import create_gradio_app
from src.config import SERVER_HOST, SERVER_PORT

# Create FastAPI app
app = FastAPI(
    title="Hadith Search API",
    description="Semantic search for Sahih Bukhari and Sahih Muslim",
    version="1.0"
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Create and mount Gradio app
gradio_app = create_gradio_app()
app = gr.mount_gradio_app(app, gradio_app, path="/")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
