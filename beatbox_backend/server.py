# import logging

# from beatbox_backend.routes.other import Other
# from beatbox_backend.routes.music import Music

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class Server:
#     def __init__(self, app):
#         self.app = app

#         self.other = Other()
#         self.music = Music()


#     def setup_routes(self):
#         # OTHER
#         self.app.get("/favicon.ico")(self.other.favicon)

#         # MUSIC
#         self.app.get("/musics")(self.music.get_musics)
#         self.app.post("/musics")(self.music.post_music)