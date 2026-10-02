import json
import logging
import os
from datetime import datetime
from pathlib import Path
import subprocess
import sys
import tempfile

import openpyxl
import webview

from pytool.channel_report import write_channel_performance
from pytool.filter_by_rules import filter_by_rules
from pytool.paths import app_root
from pytool.read_source_data import read_source_data
from pytool.settings import get_log_path, load_settings, save_settings
from pytool.event import ui_ready_event
from pytool.push_logs import SentToBrowser
logger = logging.getLogger("pytool")


def _ensure_writable_directory(path: str) -> Path:
    directory = Path(path).expanduser()
    if not directory.is_dir():
        raise NotADirectoryError(f"Output directory does not exist: {directory}")
    try:
        with tempfile.NamedTemporaryFile(
            dir=directory,
            prefix=".automation-tool-write-test-",
            delete=False,
        ) as probe:
            probe_path = Path(probe.name)
        probe_path.unlink()
    except OSError as exc:
        raise PermissionError(
            f"Output directory is not writable: {directory}. "
            "Choose a folder where you have write permission."
        ) from exc
    return directory


def _write_workbook(path: Path, title: str, headers: list, rows: list) -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = title
    ws.append(headers)
    for row in rows:
        ws.append(row)
    wb.save(path)


class JSAPI:
    def __init__(self):
        self._window = None
        self._logs = None
        self._file_path = None
        self._output_dir = None

    def set_window(self, window):
        self._window = window
        self._logs = SentToBrowser(window)

    def _push_log(self, message: str, path: str = "", icon: str = "success") -> None:
        if self._logs is not None:
            self._logs.pushMessage(message, path, icon)

    def select_file_impl(self, filetype="OPEN"):
        switcher = {
            "OPEN": webview.FileDialog.OPEN,
            "DIR": webview.FileDialog.FOLDER,
        }
        dialog_type = switcher.get(filetype, webview.FileDialog.OPEN)
        kwargs = {
            "allow_multiple": False,
        }
        if dialog_type == webview.FileDialog.OPEN:
            kwargs["file_types"] = (
                "Excel files (*.xls;*.xlsx)",
            )
        result = self._window.create_file_dialog(dialog_type, **kwargs)
        if result and len(result) > 0:
            # if (Path(result[0]).is_file()):
            #     self._file_path = result[0]
            return result[0]
        return None

    def select_dir(self, savedir=False):
        selected_dir = self.select_file_impl("DIR")
        if selected_dir:
            _ensure_writable_directory(selected_dir)
        self._output_dir = selected_dir
        if savedir:
            data = load_settings()
            data["report_dir"] = self._output_dir
            save_settings(data)
        return self._output_dir

    def select_file(self):
        self._file_path = self.select_file_impl("OPEN")
        return self._file_path

    def get_file_path(self):
        return self._file_path

    def get_output_dir(self):
        if self._output_dir:
            return self._output_dir
        data = load_settings()
        outdir = data.get("report_dir")
        if outdir:
            self._output_dir = outdir
            return outdir
        return str(Path(self._file_path).parent) if self._file_path else None

    def get_log_path(self):
        return str(get_log_path().parent)

    def save_output_file(self, file_path):
        output_dir = os.path.join(os.path.dirname(file_path))
        os.makedirs(output_dir, exist_ok=True)
        data = load_settings()
        data["report_dir"] = output_dir
        save_settings(data)
        return output_dir

    def ready(self):
        ui_ready_event.set()

    def open_dir(self, path: str):
        self._open_path(path, expect_dir=True)

    def open_path(self, path: str):
        self._open_path(path)

    def _open_path(self, path: str, expect_dir: bool = False):
        target = Path(path).expanduser()
        if not target.exists():
            raise FileNotFoundError(f"Path does not exist: {target}")
        if expect_dir and not target.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {target}")
        if sys.platform == "darwin":
            subprocess.run(["open", str(target)], check=True)
        elif sys.platform == "win32":
            os.startfile(str(target))
        else:
            subprocess.run(["xdg-open", str(target)], check=True)

    def process_file(self, current_month, prior_month):
        source_file = self._file_path
        todayStr = datetime.strftime(datetime.now(), '%m.%d.%y')
        step = "validate input"
        if self._logs is not None:
            self._logs.clear()
        self._push_log("Starting report processing", icon="processing")
        try:
            if source_file is None:
                raise ValueError("Source file path is not set.")
            outdir = self.get_output_dir()
            if not outdir:
                raise ValueError("Output directory is not set.")
            outdir_path = Path(outdir) / todayStr
            step = "prepare output directory"
            _ensure_writable_directory(outdir)
            outdir_path.mkdir(parents=True, exist_ok=True)
            current_date = datetime.strptime(current_month, "%Y-%m")
            prior_date = datetime.strptime(prior_month, "%Y-%m")

            def on_row_error(err_step, row_no, row, err):
                try:
                    data = json.dumps(row, default=str, ensure_ascii=False)
                except Exception:
                    data = str(row)
                logger.error("[%s] row %s: %s | %s", err_step, row_no, err, data)

            step = "read source"
            originData = read_source_data(
                source_file,
                current_date,
                prior_date,
                on_error=on_row_error,
            )

            step = "filter"
            filtered = filter_by_rules(originData, on_error=on_row_error)
            current = filtered["current"]
            year = current_date.year
            headers = originData["headers"]

            step = "write Direct IC"
            _write_workbook(
                outdir_path /
                f"MCR-{year}-Channel Performance Direct IC-{todayStr}.xlsx",
                "Direct IC",
                headers,
                current["direct_ic"],
            )
            self._push_log("Finished Direct IC")
            step = "write Direct OOC"
            _write_workbook(
                outdir_path /
                f"MCR-{year}-Channel Performance Direct OCC-{todayStr}.xlsx",
                "Direct OOC",
                headers,
                current["direct_ooc"],
            )
            self._push_log("Finished Direct OOC")
            step = "write NonDirect IC"
            _write_workbook(
                outdir_path /
                f"MCR-{year}-Channel Performance NonDirect IC-{todayStr}.xlsx",
                "NonDirect IC",
                headers,
                current["non_direct_ic"],
            )
            self._push_log("Finished NonDirect IC")
            step = "write NonDirect OOC"
            _write_workbook(
                outdir_path /
                f"MCR-{year}-Channel Performance NonDirect OCC-{todayStr}.xlsx",
                "NonDirect OOC",
                headers,
                current["non_direct_ooc"],
            )
            self._push_log("Finished NonDirect OOC")
            step = "write Channel Performance"
            report = write_channel_performance(
                outdir_path /
                f"MCR-{year}-Channel Performance-{todayStr}.xlsx",
                current_month,
                originData["current"],
                current,
                prior_month,
                originData["prior"],
                filtered["prior"],
                filtered["current_mailable"],
                filtered["prior_mailable"],
                filtered["new_this_month"],
                filtered["new_prior_month"],
            )
            self._push_log("Finished Channel Performance", str(report))
            return str(report)
        except OSError as exc:
            if step == "prepare output directory":
                logger.exception("Failed at %s", step)
                raise PermissionError(
                    f"Cannot write output to: {outdir}. "
                    "Choose a folder where you have write permission."
                ) from exc
            logger.exception("Failed at %s", step)
            raise
        except Exception:
            logger.exception("Failed at %s", step)
            raise
