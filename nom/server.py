import threading
from websocket_server import WebsocketServer


class MarkdownServer():
    def __init__(self, port=9001):
        self.port = port

    def start(self):
        server = WebsocketServer(self.port)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        self.server = server
        self.thread = thread

    def shutdown(self):
        self.server.shutdown()
        self.thread.join()

    def update_clients(self):
        self.server.send_message_to_all('update')