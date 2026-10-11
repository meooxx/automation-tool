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
from pytool.read_source_data import list_lead_sources, read_source_data
from pytool.settings import get_log_path, load_settings, save_settings
from pytool.event import ui_ready_event
from pytool.push_logs import SentToBrowser
logger = logging.getLogger("pytool")


def _ensure_writable_directory(path: str) -> Path:
    directory = Path(path).expanduser()
    if not directory.is_dir():
        raise NotADirectoryError(
            f"Output directory does not exist: {directory}")
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


def read_lead_sources(file_path: str) -> list:
    if not Path(file_path).is_file():
        raise FileNotFoundError(f"Source file not found: {file_path}")
    return list_lead_sources(file_path)


class JSAPI:
    def __init__(self):
        self._window = None
        self._logs = None
        self._file_path = None
        self._output_dir = None
        self._selected_sources = None

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
                "Excel files (*.xlsx)",
            )
        result = self._window.create_file_dialog(dialog_type, **kwargs)
        if result and len(result) > 0:
            # if (Path(result[0]).is_file()):
            #     self._file_path = result[0]
            return result[0]
        return None

    def select_dir(self, savedir=False):
        selected_dir = self.select_file_impl("DIR")
        if not selected_dir:
            return None
        _ensure_writable_directory(selected_dir)
        self._output_dir = selected_dir
        if savedir:
            data = load_settings()
            data["report_dir"] = self._output_dir
            save_settings(data)
        return self._output_dir

    def select_file(self):
        selected_file = self.select_file_impl("OPEN")
        if selected_file:
            self._file_path = selected_file
        return selected_file

    def select_file_and_get_lead_sources(self):
        path = self.select_file()
        if path:
            sources = list_lead_sources(path)

            return {"file_path": path, "lead_sources": sources}
        return None

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

    def list_lead_sources(self):
        if self._file_path is None:
            raise ValueError("Source file path is not set.")
        return list_lead_sources(self._file_path)

    def get_source_headers(self):
        if self._selected_sources is not None:
            return self._selected_sources
        data = load_settings()
        sources = data.get("source_headers", None)
        if sources is not None:
            self._selected_sources = sources
        return sources or []

    def save_source_headers(self, sources: str):
        sources = json.loads(sources) if isinstance(sources, str) else sources
        if not isinstance(sources, list):
            raise ValueError("sources must be a list")
        selected_sources = []
        for source in sources:
            if not isinstance(source, dict):
                continue
            aliases = source.get("alias") or []
            if not isinstance(aliases, list):
                aliases = []
            selected_sources.append({
                "key": str(source.get("key") or "").strip(),
                "label": str(source.get("label") or "").strip(),
                "value": str(source.get("value") or "").strip(),
                "alias": [str(a).strip() for a in aliases if a is not None],
                "columnName": str(source.get("columnName") or "").strip(),
            })
        data = load_settings()
        data["source_headers"] = selected_sources
        self._selected_sources = selected_sources
        save_settings(data)

    def process_file(self, current_month, prior_month, selected_sources=None):
        source_file = self._file_path
        todayStr = datetime.strftime(datetime.now(), '%m.%d.%y')
        now = datetime.strftime(datetime.now(), '%H.%M.%S%f')
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
            outdir_path = Path(outdir) / (todayStr + '_' + now)
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
                logger.error("[%s] row %s: %s | %s",
                             err_step, row_no, err, data)

            step = "read source"
            originData = read_source_data(
                source_file,
                current_date,
                prior_date,
                on_error=on_row_error,
            )

            step = "filter"
            if isinstance(selected_sources, str):
                selected_sources = json.loads(selected_sources)
            if selected_sources is None:
                raise ValueError("selected_sources is required")
            self.save_source_headers(selected_sources)
            filtered = filter_by_rules(
                originData,
                on_error=on_row_error,
                selected_sources=selected_sources,
            )
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
                f"MCR-{year}-Channel Performance Direct OOC-{todayStr}.xlsx",
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
                f"MCR-{year}-Channel Performance NonDirect OOC-{todayStr}.xlsx",
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
                prospect_id_index=filtered["prospect_id_index"],
                lead_categories=filtered["lead_categories"],
            )
            self._push_log("Finished Channel Performance")
            self._push_log("Finished processing report",
                           icon="success", path=str(outdir_path))
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
