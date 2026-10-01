import json
import logging
import os
from datetime import datetime
from pathlib import Path
import subprocess
import sys

import openpyxl
import webview

from pytool.channel_report import write_channel_performance
from pytool.filter_by_rules import filter_by_rules
from pytool.read_source_data import read_source_data
from pytool.settings import load_settings, save_settings
from pytool.event import ui_ready_event
logger = logging.getLogger("pytool")


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
        self._file_path = None
        self._output_dir = None

    def set_window(self, window):
        self._window = window

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
        self._output_dir = self.select_file_impl("DIR")
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
        print(path, Path(path).expanduser())
        if Path(path).expanduser().exists() and Path(path).expanduser().is_dir():
            print(f"Opening directory: {path}")

            if sys.platform == "darwin":
                subprocess.call(["open", Path(path).expanduser()])
            elif sys.platform == "win32":
                os.startfile(Path(path).expanduser())

    def process_file(self, current_month, prior_month):
        source_file = self._file_path

        if (self._file_path is None):
            raise ValueError("Source file path is not set.")
        todayStr = datetime.strftime(datetime.now(), '%m.%d.%y')
        outdir = self.get_output_dir()

        if not source_file:
            raise ValueError("Source file path is not set.")
        outdir_path = Path(outdir) / todayStr
        outdir_path.mkdir(parents=True, exist_ok=True)

        current_date = datetime.strptime(current_month, "%Y-%m")
        prior_date = datetime.strptime(prior_month, "%Y-%m")
        step = "start"

        def on_row_error(err_step, row_no, row, err):
            try:
                data = json.dumps(row, default=str, ensure_ascii=False)
            except Exception:
                data = str(row)
            logger.error("[%s] row %s: %s | %s", err_step, row_no, err, data)

        try:
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
            step = "write Direct OOC"
            _write_workbook(
                outdir_path /
                f"MCR-{year}-Channel Performance Direct OCC-{todayStr}.xlsx",
                "Direct OOC",
                headers,
                current["direct_ooc"],
            )
            step = "write NonDirect IC"
            _write_workbook(
                outdir_path /
                f"MCR-{year}-Channel Performance NonDirect IC-{todayStr}.xlsx",
                "NonDirect IC",
                headers,
                current["non_direct_ic"],
            )
            step = "write NonDirect OOC"
            _write_workbook(
                outdir_path /
                f"MCR-{year}-Channel Performance NonDirect OCC-{todayStr}.xlsx",
                "NonDirect OOC",
                headers,
                current["non_direct_ooc"],
            )
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
            return str(report)
        except Exception:
            logger.exception("Failed at %s", step)
            raise
