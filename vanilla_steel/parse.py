import os
import pandas as pd
from vanilla_steel.utils import (
    parse_xlsx_file,
    generate_metadata_id,
    extract_material_info,
)

# Define constants
INPUT_DATA_FILE_NAMES: dict[str, str | os.PathLike] = {
    "source1": "./resources/source1.xlsx",
    "source2": "./resources/source2.xlsx",
    "source3": "./resources/source3.xlsx",
}

STANDARD_ORDER_INFO = [
    "material_id",
    "quantity",
    "unit",
    "supplier",
    "weight",
]

STANDARD_METADATA = [
    "quality",
    "grade",
    "finish_i18n",
    "description_i18n",
    "composition",
    "additional_info",
    "thickness_mm",
    "width_mm",
]

COMPOSITION_ELEMENTS = [
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


def load_data(file_paths: dict) -> dict:
    return {name: parse_xlsx_file(path) for name, path in file_paths.items()}


def parse_source1(df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    order_info_map = {
        "Gross weight (kg)": "weight",
    }

    metadata_map = {
        "Width (mm)": "width_mm",
        "Thickness (mm)": "thickness_mm",
        "Description": "description_i18n",
        "Quality/Choice": "quality",
        "Grade": "grade",
        "Finish": "finish_i18n",
    }

    order_info, metadata = [], []

    for _, row in df.iterrows():
        metadata_entry = {
            metadata_map[k]: v for k, v in row.items() if k in metadata_map
        }
        metadata_entry["description_i18n"] = {
            "de": metadata_entry.pop("description_i18n")
        }
        metadata_entry["finish_i18n"] = {"de": metadata_entry.pop("finish_i18n")}

        composition = {k: v for k, v in row.items() if k in COMPOSITION_ELEMENTS}
        metadata_entry.update(
            {
                "composition": composition,
                "supplier": "source1",
                "additional_info": {"RP02": row["RP02"], "RM": row["RM"]},
            }
        )
        metadata_entry["material_id"] = generate_metadata_id(metadata_entry)

        order_info_entry = {
            order_info_map[k]: v for k, v in row.items() if k in order_info_map
        }
        order_info_entry.update(
            {
                "quantity": None,
                "unit": "KG",
                "supplier": "source1",
                "material_id": metadata_entry["material_id"],
            }
        )

        order_info.append(order_info_entry)
        metadata.append(metadata_entry)

    return order_info, metadata


def parse_source2(dfs: list[pd.DataFrame]) -> tuple[list[dict], list[dict]]:

    order_info, metadata = [], []

    for df in dfs:
        for _, row in df.iterrows():
            material_info = extract_material_info(row["Material"])

            description_i18n = {}
            if "Description" in row:
                description_i18n["en"] = row["Description"]
            if "Opmerking" in row:
                description_i18n["de"] = row["Opmerking"]
            if "Defect description" in row:
                ...
                if "/" in str(row["Defect description"]):
                    nl_entry, en_entry = row["Defect description"].split("/")
                    description_i18n["nl"] = nl_entry
                    description_i18n["en"] = en_entry
                else:
                    description_i18n["en"] = row["Defect description"]

            metadata_entry = {
                "grade": material_info.get("grade"),
                "coating": material_info.get("coating"),
                "finish_i18n": {"de": material_info.get("finish")},
                "description_i18n": description_i18n,
                "composition": {},  # Source 2 does not have explicit composition data
                "supplier": "source2",
                "thickness_mm": material_info.get("height"),
                "width_mm": material_info.get("width"),
                "length_mm": material_info.get("length"),
                "additional_info": {
                    "additional": material_info.get("additional"),
                    "article_id": row.get("Article ID "),
                },
            }

            metadata_entry["material_id"] = generate_metadata_id(metadata_entry)

            order_info_entry = {
                "weight": row.get("weight") or row.get("Weight"),
                "unit": "KG",
                "quantity": row.get("Quantity"),
                "supplier": "source2",
                "material_id": metadata_entry["material_id"],
            }

            order_info.append(order_info_entry)
            metadata.append(metadata_entry)

    return order_info, metadata


def parse_source3(df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    order_info, metadata = [], []

    for _, row in df.iterrows():
        material_info = extract_material_info(row["Matériel Desc#"])

        metadata_entry = {
            "grade": material_info.get("grade"),
            "coating": material_info.get("coating"),
            "finish_i18n": {"fr": material_info.get("finish")},
            "description_i18n": {"fr": row["Matériel Desc#"]},
            "composition": {},  # Source 3 does not have explicit composition data
            "supplier": "source3",
            "thickness_mm": material_info.get("height"),
            "width_mm": material_info.get("width"),
            "length_mm": material_info.get("length"),
            "additional_info": {
                "additional": material_info.get("additional"),
                "supplier_article": row.get("Article"),
                "supplier_id": row.get("Numéro de"),
            },
        }

        metadata_entry["material_id"] = generate_metadata_id(metadata_entry)

        order_info_entry = {
            "weight": row.get("Libre"),  # Assuming 'Libre' is the weight in KG
            "unit": "KG",
            "quantity": None,
            "supplier": "source3",
            "material_id": metadata_entry["material_id"],
        }

        order_info.append(order_info_entry)
        metadata.append(metadata_entry)

    return order_info, metadata


def process_sources(data: dict) -> dict[str, dict[str, list[dict]]]:

    order_info_1, metadata_1 = parse_source1(data["source1"]["Sheet1"][0])
    order_info_2, metadata_2 = parse_source2(data["source2"]["First choice "])
    order_info_22, metadata_22 = parse_source2(data["source2"]["2nd choice "])
    order_info_3, metadata_3 = parse_source3(data["source3"]["Feuil1"][0])

    order_info = [*order_info_1, *order_info_2, *order_info_22, *order_info_3]
    metadata = [*metadata_1, *metadata_2, *metadata_22, *metadata_3]

    return order_info, metadata


def write_output(order_info: list, metadata: list) -> None:

    os.makedirs("output", exist_ok=True)

    pd.DataFrame(order_info).to_csv(
        os.path.join("output", "order_info.csv"), index=False
    )
    pd.DataFrame(metadata).to_csv(os.path.join("output", "metadata.csv"), index=False)

    # Add them joined by metadata_id
    joined = pd.merge(
        pd.DataFrame(order_info),
        pd.DataFrame(metadata),
        on=["material_id", "supplier"],
        how="outer",
    )
    joined.to_csv(os.path.join("output", "joined.csv"), index=False)


def main():
    raw_dfs = load_data(INPUT_DATA_FILE_NAMES)
    order_info, metadata = process_sources(raw_dfs)

    write_output(order_info, metadata)


if __name__ == "__main__":
    main()
