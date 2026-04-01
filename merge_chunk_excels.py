#!/usr/bin/env python

# ==============================
# Import librerie
# ==============================

import pandas as pd
from pathlib import Path


# ==============================
# Header
# ==============================

print("\n==============================")
print("Merge Chunk Excel Files")
print("==============================\n")


# ==============================
# Default directories
# ==============================

default_input = "./annotations"
default_output = "./merged"


# ==============================
# Input utente
# ==============================

input_dir = input(
    f"Directory with annotation Excel files [{default_input}]: "
).strip('"')

if input_dir == "":
    input_dir = default_input


output_dir = input(
    f"Output directory [{default_output}]: "
).strip('"')

if output_dir == "":
    output_dir = default_output


output_name = input(
    "Output file name [beluga_merged.xlsx]: "
)

if output_name == "":
    output_name = "beluga_merged.xlsx"


# ==============================
# Costruzione path
# ==============================

input_path = Path(input_dir)
output_path = Path(output_dir)


# ==============================
# Controllo directory
# ==============================

if not input_path.exists():
    print("Input directory not found")
    exit()

output_path.mkdir(
    parents=True,
    exist_ok=True
)


# ==============================
# Trova file Excel
# ==============================

excel_files = sorted(
    input_path.glob("*.xlsx")
)

if len(excel_files) == 0:
    print("No Excel files found")
    exit()

print(f"\nFound {len(excel_files)} Excel files")


# ==============================
# Lista dataframe
# ==============================

dfs = []


# ==============================
# Loop file
# ==============================

for file in excel_files:

    print(f"Loading: {file.name}")

    df = pd.read_excel(file)

    dfs.append(df)


# ==============================
# Merge dataframe
# ==============================

print("\nMerging files...")

merged_df = pd.concat(
    dfs,
    ignore_index=True
)


# ==============================
# Sorting
# ==============================

sort_columns = [
    col for col in [
        "year",
        "recording",
        "level",
        "chunk_id"
    ]
    if col in merged_df.columns
]

if sort_columns:
    merged_df = merged_df.sort_values(sort_columns)


merged_df = merged_df.reset_index(drop=True)


# ==============================
# Save
# ==============================

final_output = output_path / output_name

merged_df.to_excel(
    final_output,
    index=False
)


# ==============================
# Done
# ==============================

print("\n==============================")
print("Merge completed")
print(f"Saved: {final_output}")
print("==============================")
