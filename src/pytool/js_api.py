import os

import webview

from pytool.settings import load_settings, save_settings


class JSAPI:
    def __init__(self):
        self._window = None
        self._file_path = None

    def set_window(self, window):
        self._window = window

    def select_file(self, FileDialog="OPEN"):
        switcher = {
            "OPEN": webview.FileDialog.OPEN,
            "DIR": webview.FileDialog.DIRECTORY,
        }
        file_types = (
            "Excel files (*.xls;*.xlsx)",
            "all files (*.*)",
        )
        last_dir = load_settings().get("last_source_dir") or ""
        result = self._window.create_file_dialog(
            switcher.get(FileDialog, webview.FileDialog.OPEN),
            directory=last_dir,
            allow_multiple=False,
            file_types=file_types,
        )
        if result and len(result) > 0:
            self._file_path = result[0]
            return result[0]
        return None

    def save_output_file(self, file_path):
        output_dir = os.path.join(os.path.dirname(file_path), "reports")
        os.makedirs(output_dir, exist_ok=True)
        data = load_settings()
        data["report_dir"] = output_dir
        save_settings(data)
        return output_dir
