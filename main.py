# main.py

import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.wsgi:app",
        host=settings.get_host(),
        port=settings.get_port(),
        reload=settings.get_reload(),
        workers=settings.get_uvicorn_workers()
    )
