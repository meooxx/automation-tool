# Clear Mark-of-the-Web before importing webview/pythonnet (Windows downloads).
from pytool.win_motw import clear_mark_of_the_web

clear_mark_of_the_web()

from pytool.app import run

if __name__ == "__main__":
    run()
