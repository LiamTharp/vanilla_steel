import hashlib
import re
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
    sorted_items = [item for item in sorted_items if item[0] != "material_id"]

    # Create a string of concatenated key-value pairs
    concatenated_string = "".join(f"{k}:{v}" for k, v in sorted_items)

    # Generate a hash of the concatenated string
    unique_id = hashlib.md5(concatenated_string.encode()).hexdigest()

    return unique_id


MATERIAL_REGEX = re.compile(
    r"(?P<grade>[A-Z]+\d+[A-Z]*)\s*\+\s*(?P<coating>[A-Z0-9]+)\s*(?P<finish>[A-Za-z\-]+)\s*(?P<dimensions>\d+[,\d]*\s*x\s*\d+[,\d]*\s*x\s*\d+[,\d]*)"
)


# Define multiple regex patterns to handle different cases
patterns = [
    re.compile(
        r"(?P<grade>[A-Z]+\d+[A-Z]*)\s*\+\s*(?P<coating>[A-Z0-9]+)\s+(?P<finish>[A-Za-z\-]+)\s+(?P<dimensions>\d+[,\d]*\s*x\s*\d+[,\d]*\s*x\s*\d+[,\d]*)(\s*mm)?(\s*(?P<additional>[A-Z]+))?"
    ),
    re.compile(
        r"(?P<grade>[A-Z]+\d+[A-Z]*)\s*\+\s*(?P<coating>[A-Z0-9]+)\s+(?P<finish>[A-Za-z\-]+)\s+(?P<dimensions>\d+[,\d]*\s*x\s*\d+[,\d]*)(\s*mm)?(\s*(?P<additional>[A-Z]+))?"
    ),
    re.compile(
        r"(?P<grade>[A-Z]+\d+[A-Z]*)\s+(?P<finish>[A-Za-z]+)\s+(?P<dimensions>\d+[,\d]*\s*x\s*\d+[,\d]*)(\s*mm)?(\s*(?P<additional>[A-Z]+))?"
    ),
    # re.compile(
    #     r"(?P<grade>[A-Z]+)\s+(?P<height>\d+[.,]?\d*)x(?P<width>\d+[.,]?\d*)\s+(?P<coating>[A-Z0-9\/\-]+)\s+(?P<finish>[A-Z0-9\/\-]+)\s*(?P<additional>[A-Z]+)?"
    # ),
    re.compile(
        r"(?P<grade>[A-Z]+)\s+(?P<height>\d+[.,]?\d*)x(?P<width>\d+[.,]?\d*)\s+(?P<coating>[A-Z0-9\/\+\-]+(?:\s+\d+[.,]?\d*)?)\s+(?P<finish>[A-Z0-9\/\-\+]+)\s*(?P<additional>[A-Z]+)?"
    ),
]


def decompose_dimensions(dimensions: str) -> dict:
    """Decomposes a dimension string into width, length, and height as numeric types."""
    # Split dimensions by 'x' and remove any whitespace
    dim_parts = [dim.strip() for dim in dimensions.split("x")]

    # Decompose into length, width, height (assuming order) and parse as floats
    decomposition = {}
    if len(dim_parts) == 3:
        decomposition = {
            "length": float(dim_parts[2].replace(",", ".")),
            "width": float(dim_parts[1].replace(",", ".")),
            "height": float(dim_parts[0].replace(",", ".")),
        }
    elif len(dim_parts) == 2:
        decomposition = {
            "length": None,  # No length provided
            "width": float(dim_parts[1].replace(",", ".")),
            "height": float(dim_parts[0].replace(",", ".")),
        }

    return decomposition


def extract_material_info(material_string: str) -> dict:
    for pattern in patterns:
        match = pattern.search(material_string)
        if match:
            material_info = match.groupdict()
            dimensions = material_info.get("dimensions", "")
            dimension_parts = decompose_dimensions(dimensions)
            material_info.update(dimension_parts)
            # Remove the combined dimensions key
            material_info.pop("dimensions", None)
            return material_info

    # If no pattern matches, return an empty dictionary
    return {}


# Test the updated function
sample_strings = [
    "DX51D +Z140 Ma-C 1,50 x 1350,00 x 2850,00",
    "DX51D +AZ150 Ma-C 1,00 x 1250,00 mm AFP",
    "S235JR geolied 1,75 x 1250,00 mm",
    "HDC 0.75x1010 GXES G10/10 MB O",
    "HDC 1x1000 HX300LAD+Z 140 MB O",
    "CR 1.47x1390 X-ES A O",
    "HRP 2x1360 HR2 O",
    "HDC 1x1432 HX380LAD+Z 140 MB O",
]

for string in sample_strings:
    material_info = extract_material_info(string)
    print(f"Material: {string}")
    print(material_info)
