from fastapi.responses import FileResponse

favicon_path = 'beatbox_backend/assets/favicon.ico'

class Other():
    def __init__(self):
        pass

    async def favicon(self):
        return FileResponse(favicon_path)