import os

import webview

from pytool.settings import load_settings, save_settings
from pytool.read_source_data import read_source_data
from datetime import datetime
from pathlib import Path
import openpyxl

from pytool.filter_by_rules import filter_by_rules
from pytool.channel_report import write_channel_performance


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

    def set_window(self, window):
        self._window = window

    def select_file(self, filetype="OPEN"):
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
                "all files (*.*)",
            )
        result = self._window.create_file_dialog(dialog_type, **kwargs)
        if result and len(result) > 0:
            self._file_path = result[0]
            return result[0]
        return None

    def save_output_file(self, file_path):
        output_dir = os.path.join(os.path.dirname(file_path))
        os.makedirs(output_dir, exist_ok=True)
        data = load_settings()
        data["report_dir"] = output_dir
        save_settings(data)
        return output_dir

    def process_file(self, current_month, prior_month):
        setting = load_settings()
        todayStr = datetime.strftime(datetime.now(), '%m.%d.%y')
        outdir_config = setting.get("report_dir", "")
        
        source_file = self._file_path
        if not source_file:
            raise ValueError("Source file path is not set.")
        outdir_path = Path(outdir_config) if outdir_config else Path(source_file).parent / todayStr
        outdir_path.mkdir(parents=True, exist_ok=True)

        current_date = datetime.strptime(current_month, "%Y-%m")
        prior_date = datetime.strptime(prior_month, "%Y-%m")
        originData = read_source_data(source_file, current_date, prior_date)
        filtered = filter_by_rules(originData)
        current = filtered["current"]
        year = current_date.year
        headers = originData["headers"]

        _write_workbook(
            outdir_path / f"MCR-{year}-Channel Performance Direct IC-{todayStr}.xlsx",
            "Direct IC",
            headers,
            current["direct_ic"],
        )
        _write_workbook(
            outdir_path / f"MCR-{year}-Channel Performance Direct OCC-{todayStr}.xlsx",
            "Direct OOC",
            headers,
            current["direct_ooc"],
        )
        _write_workbook(
            outdir_path / f"MCR-{year}-Channel Performance NonDirect IC-{todayStr}.xlsx",
            "NonDirect IC",
            headers,
            current["non_direct_ic"],
        )
        _write_workbook(
            outdir_path / f"MCR-{year}-Channel Performance NonDirect OCC-{todayStr}.xlsx",
            "NonDirect OOC",
            headers,
            current["non_direct_ooc"],
        )
        report = write_channel_performance(
            outdir_path / f"MCR-{year}-Channel Performance-{todayStr}.xlsx",
            current_month,
            originData["current"],
            current,
            prior_month,
            originData["prior"],
            filtered["prior"],
            headers,
        )
        return str(report)
        