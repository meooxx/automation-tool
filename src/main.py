import webview
import sys
import os
import subprocess
import time
from dotenv import load_dotenv
import json
from webview.dom import DOMEventHandler, _dnd_state
# load environment variables from .env file
if len(sys.argv) > 1:
    env = sys.argv[1]
else:
    env = 'production'

print(env)
load_dotenv(dotenv_path=f'.env.{env.lower()}')


class JSAPI:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def select_file(self):
        """打开文件选择弹窗，返回选中的文件真实绝对路径"""
        # 支持参数：
        # webview.OPEN_DIALOG (打开单个/多个文件)
        file_types = (
            'Excel 文件 (*.xls;*.xlsx)',
            '所有文件 (*.*)'
        )

        result = self._window.create_file_dialog(
            webview.FileDialog.OPEN,
            allow_multiple=False,
            file_types=file_types
        )

        # result 返回一个元组，如 ('C:\\Users\\xxx\\Documents\\test.pdf',)
        if result and len(result) > 0:
            return result[0]  # 返回单个路径字符串
        return None

    # def onDrop(self, event):
        



js_api = JSAPI()
ui_url = os.getenv('UI_URL')
if env == 'development':
    print(ui_url)
    is_dev = True
    ui_path = os.path.join('.', 'ui', 'pytool-ui')
    # subprocess.Popen('npm run dev', cwd=ui_path, shell=True)
    window = webview.create_window('webview_dev', ui_url, js_api=js_api,
                                   easy_drag=False, resizable=True, )
    time.sleep(2)
else:
    is_dev = False
    window = webview.create_window('tool_ui', ui_url, js_api=js_api,
                                   easy_drag=False)


js_api.set_window(window)
webview.start(debug=is_dev,)
