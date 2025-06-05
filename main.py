# main.py

import logging
import uvicorn

from app.config import settings

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "wsgi:app",
        host=settings.get_host(),
        port=settings.get_port(),
        reload=settings.get_reload(),
        workers=settings.get_uvicorn_workers()
    )
