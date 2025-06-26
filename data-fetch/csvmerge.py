import pandas as pd
import os

# File paths for uploaded CSVs
file_paths = [
    "/mnt/data/worli,-mumbai-air-quality.csv",
    "/mnt/data/vile-parle west, mumbai-air-quality.csv",
    "/mnt/data/sion,-mumbai-air-quality.csv",
    "/mnt/data/kurla,-mumbai, india-air-quality.csv",
    "/mnt/data/chhatrapati-shivaji intl. airport (t2), mumbai-air-quality.csv",
    "/mnt/data/chakala-andheri-east, mumbai-air-quality.csv"
]

# Read and clean all files
cleaned_data = []
for path in file_paths:
    try:
        df = pd.read_csv(path)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        df['location'] = os.path.basename(path).split("-air-quality")[0].replace(",", "").strip()
        cleaned_data.append(df)
    except Exception as e:
        print(f"Failed to read {path}: {e}")

# Concatenate all dataframes
merged_df = pd.concat(cleaned_data, ignore_index=True)
merged_df.head()