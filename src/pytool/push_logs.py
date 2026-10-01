

class SentToBrowser:
    def __init__(self, window):
        self.window = window

    def pushMessage(self, message: str, path: str = ''):

        self.window.evaluate_js(
            f"window['CALL_METHODS'].get('push_log')({{type: 'new', content: '{message}', path: '{path}', icon: 'success'}})")

    def clear(self):
        self.window.evaluate_js(
            f"window['CALL_METHODS'].get('push_log')({{type: 'clear'}})")
