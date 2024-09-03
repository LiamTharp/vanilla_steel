# %%
import os
import pandas as pd
from vanilla_steel.utils import parse_xlsx_file

# Define the file paths
file_paths = {
    "source1": "./resources/source1.xlsx",
    "source2": "./resources/source2.xlsx",
    "source3": "./resources/source3.xlsx",
}

# %%


def summarize_data(file_path: str | os.PathLike):

    df = parse_xlsx_file(file_path, threshold=2)

    print("**File Path:**", file_path)

    for sheet_name, dfs in df.items():
        print("Number of tables:", len(dfs))

        print(f"\n--- {sheet_name} ---")
        # Number of tables per sheet

        # Number of rows per table
        for i, df in enumerate(dfs):
            print(f"Table {i+1}: {df.shape[0]} rows")
            print(df.head(2))

    return df


# %%

source_data = {
    name: summarize_data(file_path) for name, file_path in file_paths.items()
}

# %%
