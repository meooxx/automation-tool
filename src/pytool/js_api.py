import os

import webview

from pytool.settings import load_settings, save_settings
from pytool.read_source_data import read_source_data
from pytool.paths import app_root
from datetime import datetime
from pathlib import Path
import openpyxl

from pytool.filter_by_rules import filter_by_rules


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
        if not outdir_config:
            outdir_path = Path(source_file).parent / todayStr
            outdir_path.mkdir(parents=True, exist_ok=True)

        current_date = datetime.strptime(current_month, "%Y-%m")
        prior_date = datetime.strptime(prior_month, "%Y-%m")
        # output_dir = self.save_output_file(source_file)
        originData = read_source_data(source_file, current_date, prior_date)
        filtered = filter_by_rules(originData)

        # MCR-2026-Channel Performance Direct IC–9.24.26.xlsx
        dir_ic = f"MCR-{current_date.year}-Channel Performance Direct IC-{todayStr}.xlsx",
        # MCR-2026-Channel Performance Direct IC–9.24.26.xlsx
        non_dir_ic = f"MCR-{current_date.year}-Channel Performance NonDirect IC-{todayStr}.xlsx",
        dir_occ = f"MCR-{current_date.year}-Channel Performance Direct OCC-{todayStr}.xlsx",
        non_dir_occ = f"MCR-{current_date.year}-Channel Performance NonDirect OCC-{todayStr}.xlsx",
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Direct IC"
        ws.append(originData["headers"][:])
        ws.append(**filtered["direct_ic"])
        wb.save(Path(outdir_path) / dir_ic)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Direct OOC"
        ws.append(originData["headers"][:])
        ws.append(**filtered["direct_ooc"])
        wb.save(Path(outdir_path) / dir_occ)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "NonDirect IC"
        ws.append(originData["headers"][:])
        ws.append(**filtered["non_direct_ic"])
        wb.save(Path(outdir_path) / non_dir_ic)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "NonDirect OOC"
        ws.append(originData["headers"][:])
        ws.append(**filtered["non_direct_ooc"])
        wb.save(Path(outdir_path) / non_dir_occ)
