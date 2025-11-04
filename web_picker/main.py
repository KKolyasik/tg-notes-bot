from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from web_picker.endpoints.tma import router as tma_router

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
INDEX_FILE = STATIC_DIR / "picker.html"

app = FastAPI()
app.include_router(tma_router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/picker", response_class=FileResponse, include_in_schema=False)
async def picker_page() -> FileResponse:
    """Ручка на отдачку статики для приложения."""
    return FileResponse(INDEX_FILE)
