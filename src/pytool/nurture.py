from pathlib import Path

import openpyxl

from pytool.settings import get_nurture_config


def load_nurture_values() -> set[str]:

    config = get_nurture_config()
    if config.get("enable") is not True:
        return set()
    if not config["file_path"]:
        return set()
    path = Path(config["file_path"])
    if not path.is_file():
        raise FileNotFoundError(f"Nurture list not found: {path}")
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        headers = ["" if value is None else str(
            value).strip() for value in next(rows)]
        field = config["nurture_header"]
        if not field:
            raise ValueError("Nurture match column has not been selected")
        wanted = {field.casefold()}
        index = next(
            (
                i
                for i, header in enumerate(headers)
                if header.casefold() in wanted
            ),
            -1,
        )
        if index == -1:
            raise ValueError(
                f"Nurture list is missing the configured match field: {field}"
            )
        return {
            str(row[index]).strip()
            for row in rows
            if index < len(row) and row[index] is not None and str(row[index]).strip()
        }
    finally:
        workbook.close()
