import webview


class JSAPI:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def select_file(self):
        file_types = (
            "Excel files (*.xls;*.xlsx)",
            "all files (*.*)",
        )
        result = self._window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=file_types,
        )
        if result and len(result) > 0:
            return result[0]
        return None
