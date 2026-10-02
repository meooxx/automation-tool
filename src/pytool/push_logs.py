
import json


class SentToBrowser:
    def __init__(self, window):
        self.window = window

    def pushMessage(self, message: str, path: str = '', icon: str = 'success'):
        self.window.evaluate_js(
            "window['CALL_METHODS'].get('push_log')("
            f"{json.dumps({'type': 'new', 'content': message, 'path': path, 'icon': icon})})"
        )

    def clear(self):
        self.window.evaluate_js(
            f"window['CALL_METHODS'].get('push_log')({{type: 'clear'}})")
