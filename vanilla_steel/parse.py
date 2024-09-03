# %%

import hashlib
import os
from typing import MutableMapping

import pandas as pd
from vanilla_steel.utils import parse_xlsx_file, generate_metadata_id

INPUT_DATA_FILE_NAMES: dict[str, str | os.PathLike] = {
    "source1": "./resources/source1.xlsx",
    "source2": "./resources/source2.xlsx",
    "source3": "./resources/source3.xlsx",
}
# %%

RAW_DFS = {}

for name, file_path in INPUT_DATA_FILE_NAMES.items():
    RAW_DFS[name] = parse_xlsx_file(file_path)


# %%

STANDARD_ORDER_INFO = [
    "material_id",
    "material_name",
    "quantity",
    "unit",
    "price_per_unit",
    "supplier",
    "thickness_mm",
    "width_mm",
    "weight",
]

STANDARD_METADATA = [
    "quality",
    "grade",
    "finish",
    "description_i18n",
    "composition",
    "additional_info",
]
# %% Parsing Source 1

df = RAW_DFS["source1"]["Sheet1"][0]

ORDER_INFO_MAP = {
    "Gross weight (kg)": "weight",
    "Width (mm)": "width_mm",
    "Thickness (mm)": "thickness_mm",
}

METADATA_MAP = {
    "Description": "description_i18n",
    "Quality/Choice": "quality",
    "Grade": "grade",
    "Finish": "finish",
}

COMPOSITION_KEYS = [
    "AG",
    "Al",
    "Ars",
    "B",
    "C",
    "Ca",
    "Cr",
    "S",
    "Cu",
    "Mn",
    "Mo",
    "N",
    "Nb",
    "Ni",
    "P",
    "Si",
    "Sn",
    "STA",
    "Ti",
    "V",
    "Zr",
]

# %%

ORDER_INFO = []
METADATA = []

# %%


for index, row in df.iterrows():

    metadata = {METADATA_MAP[k]: v for k, v in row.items() if k in METADATA_MAP}

    # i18n for description
    metadata["description"] = {"de": metadata.pop("description_i18n")}

    # Add Composition
    composition = {k: v for k, v in row.items() if k in COMPOSITION_KEYS}
    metadata.update(
        {
            "composition": composition,
            "supplier": "source1",
            "additional_info": {"RP02": row["RP02"], "RM": row["RM"]},
        }
    )
    metadata["metadata_id"] = generate_metadata_id(metadata)

    order_info = {k: v for k, v in row.items() if k in ORDER_INFO_MAP}
    order_info.update({"unit": "count", })

    order_info["metadata_id"] = metadata["metadata_id"]

    ORDER_INFO.append(order_info)
    METADATA.append(metadata)

# %%
