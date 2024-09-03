import hashlib
from typing import MutableMapping
import pandas as pd
import numpy as np
import os


## Function LOOSELY based on https://stackoverflow.com/questions/43367805/pandas-read-excel-multiple-tables-on-the-same-sheet
## Own modifications are significant
def parse_xlsx_file(
    file_path: str | os.PathLike, threshold: int = 2
) -> dict[str, list[pd.DataFrame]]:
    xl = pd.ExcelFile(file_path)

    def _parse_sheet(sheet_name):

        sheet_name = xl.sheet_names[0]
        raw_sheet = xl.parse(sheet_name, header=None)

        row_counts = np.logical_not(raw_sheet.isnull()).sum(axis=1)
        row_deltas = np.diff(row_counts)

        table_beginnings = np.where(row_deltas > threshold)[0] + 1
        table_endings = np.where(row_deltas < -threshold)[0]

        # Appending necessary starts and endings (if not detected)
        ACCEPTED_BEGINNINGS = [0, 1]
        ACCEPTED_ENDINGS = [raw_sheet.shape[0] - 1, raw_sheet.shape[0] - 2]

        if len(table_beginnings) == 0:
            table_beginnings = np.array([0])
        elif sorted(table_beginnings)[0] not in ACCEPTED_BEGINNINGS:
            table_beginnings = np.insert(table_beginnings, 0, 0)

        if len(table_endings) == 0:
            table_endings = np.array([raw_sheet.shape[0]])
        elif sorted(table_endings)[-1] not in ACCEPTED_ENDINGS:
            table_endings = np.concat((table_endings, [raw_sheet.shape[0] - 1]))

        if len(table_beginnings) != len(table_endings):
            raise ValueError(
                f"Could not find table boundaries in sheet {sheet_name}.\nTable beginning and ending indices are: {table_beginnings}, {table_endings}"
            )

        # make data frames
        dfs = []
        for i, (start, stop) in enumerate(
            zip(table_beginnings, table_endings, strict=True)
        ):

            num_rows = stop - start if start else stop
            df = xl.parse(
                sheet_name=sheet_name, skiprows=start, nrows=num_rows, header=0
            ).dropna(axis=1, how="all")
            dfs.append(df)

        return dfs

    return {sheet_name: _parse_sheet(sheet_name) for sheet_name in xl.sheet_names}


def flatten_dict(d, parent_key="", sep="_"):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def generate_metadata_id(d: dict) -> str:
    # Flatten the dictionary
    flat_dict = flatten_dict(d)

    # Sort the dictionary by keys
    sorted_items = sorted(flat_dict.items())

    # Remove 'metadata_id' from the list
    sorted_items = [item for item in sorted_items if item[0] != "metadata_id"]

    # Create a string of concatenated key-value pairs
    concatenated_string = "".join(f"{k}:{v}" for k, v in sorted_items)

    # Generate a hash of the concatenated string
    unique_id = hashlib.md5(concatenated_string.encode()).hexdigest()

    return unique_id
