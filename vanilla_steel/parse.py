# %%
import os

import pandas as pd
from vanilla_steel.utils import (
    parse_xlsx_file,
    generate_metadata_id,
    extract_material_info,
)

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
    "finish_i18n",
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
    "Finish": "finish_i18n",
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


ORDER_INFO = []
METADATA = []

for index, row in df.iterrows():

    metadata = {METADATA_MAP[k]: v for k, v in row.items() if k in METADATA_MAP}

    # i18n for description
    metadata["description_i18n"] = {"de": metadata.pop("description_i18n")}
    metadata["finish_i18n"] = {"de": metadata.pop("finish_i18n")}

    # Add Composition
    composition = {k: v for k, v in row.items() if k in COMPOSITION_KEYS}
    metadata.update(
        {
            "composition": composition,
            "supplier": "source1",
            "additional_info": {"RP02": row["RP02"], "RM": row["RM"]},
        }
    )
    metadata["material_id"] = generate_metadata_id(metadata)

    order_info = {k: v for k, v in row.items() if k in ORDER_INFO_MAP}
    order_info.update({"unit": "count", "supplier": "source1"})

    order_info["material_id"] = metadata["material_id"]

    ORDER_INFO.append(order_info)
    METADATA.append(metadata)

# %% Source 2

dfs: list[pd.DataFrame] = RAW_DFS["source2"]["First choice "]

ORDER_INFO_MAP = {
    "Quantity": "quantity",
    "weight": "weight",
}

METADATA_MAP = {"Opmerking": "description", "Description": "description"}

# %% Parsing Source 2

ORDER_INFO = []
METADATA = []

for df in dfs:
    for index, row in df.iterrows():
        material_info = extract_material_info(row["Material "])

        # Handle "Description" and "Opmerking" in different languages
        description_i18n = {}
        if "Description" in row:
            description_i18n["en"] = row["Description"]
        if "Opmerking" in row:
            description_i18n["de"] = row["Opmerking"]

        # Use the updated decompose_dimensions function to parse and extract dimensions

        metadata = {
            "grade": material_info.get("grade"),
            "coating": material_info.get("coating"),
            "finish_i18n": {"de": material_info.get("finish")},
            "description_i18n": description_i18n,
            "composition": {},  # Source 2 does not seem to have explicit composition data
            "supplier": "source2",
            "additional_info": {
                "additional": material_info.get("additional"),
                "article_id": row.get("Article ID "),
            },
        }

        metadata["material_id"] = generate_metadata_id(metadata)

        order_info = {
            "quantity": row.get("Quantity"),
            "weight": row.get("weight"),
            "unit": "count",  # Assuming unit as count, update if needed
            "supplier": "source2",
            "material_id": metadata["material_id"],
            "thickness_mm": material_info.get("height"),
            "width_mm": material_info.get("width"),
            "length_mm": material_info.get("length"),  # Only if length is relevant
        }

        ORDER_INFO.append(order_info)
        METADATA.append(metadata)

# Now ORDER_INFO and METADATA contain parsed data from Source 2

# %%


df = RAW_DFS["source3"]["Feuil1"][0]
ORDER_INFO = []
METADATA = []

for index, row in df.iterrows():
    material_info = extract_material_info(row["Matériel Desc#"])

    # Construct the metadata dictionary
    metadata = {
        "grade": material_info.get("grade"),
        "coating": material_info.get("coating"),
        "finish_i18n": {"fr": material_info.get("finish")},  # Assuming French
        "description_i18n": {"fr": row["Matériel Desc#"]},  # Full description in French
        "composition": {},  # Source 3 does not seem to have explicit composition data
        "supplier": "source3",
        "additional_info": {
            "additional": material_info.get("additional"),
            "supplier_article": row.get("Article"),
            "supplier_id": row.get("Numéro de"),
        },
    }

    metadata["material_id"] = generate_metadata_id(metadata)

    # Construct the order info dictionary
    order_info = {
        "weight": row.get("Libre"),  # Assuming 'Libre' is the weight in KG
        "unit": row.get("Unité"),
        "supplier": "source3",
        "material_id": metadata["material_id"],
        "thickness_mm": material_info.get("height"),
        "width_mm": material_info.get("width"),
        "length_mm": material_info.get("length"),
    }

    ORDER_INFO.append(order_info)
    METADATA.append(metadata)

# Now ORDER_INFO and METADATA contain parsed data from Source 3
