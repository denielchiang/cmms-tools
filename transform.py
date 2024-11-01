import pandas as pd
import re
import os
from datetime import datetime

def transform_csv(input_file, output_file):
    # Load the original CSV
    try:
        df = pd.read_csv(input_file, header=None)
    except Exception as e:
        print(f"Error loading {input_file}: {e}")
        return

    # Print 姓名 at the beginning of each file’s transformation
    name = df.iloc[1, 1] if len(df.columns) > 1 and pd.notna(df.iloc[1, 1]) else ""
    print(f"Starting transformation for: {name}")

    # Convert the traditional date format in 出生年月日 to YYYY-MM-DD
    def convert_traditional_date(traditional_date):
        match = re.match(r"民國(\d+)年(\d+)月(\d+)日", str(traditional_date))
        if match:
            year = int(match.group(1)) + 1911
            month = int(match.group(2))
            day = int(match.group(3))
            return f"{year}-{month:02d}-{day:02d}"
        return ""  # Return empty if date is missing or format doesn't match
    
    # Handle `建檔日期` conversion, checking if the column exists
    if len(df.columns) > 3 and pd.notna(df.iloc[0, 3]):
        date_value = pd.to_datetime(df.iloc[0, 3], format='%Y%m%d', errors='coerce')
        # Convert date_value to the format YYYY-MM-DD HH:MM:SSZ
        formatted_date = f"{date_value.strftime('%Y-%m-%d')} 00:00:00Z" if pd.notna(date_value) else ""
    else:
        formatted_date = ""  # Default if date is missing or invalid

    # Extract data into a dictionary, ensuring each field is correctly assigned
    data_dict = {
        "建檔日期": formatted_date,
        "姓名": name,
        "性別": df.iloc[1, 3] if len(df.columns) > 3 and pd.notna(df.iloc[1, 3]) else "未填寫",
        "出生年月日": convert_traditional_date(df.iloc[2, 1] if len(df.columns) > 1 else ""),
        "手機": str(df.iloc[3, 1]).replace("-", "") if len(df.columns) > 1 and pd.notna(df.iloc[3, 1]) else "",
        "TEL": str(df.iloc[3, 3]).replace("-", "") if len(df.columns) > 3 and pd.notna(df.iloc[3, 3]) else "",
        "市(縣)": df.iloc[5, 0] if len(df) > 5 and pd.notna(df.iloc[5, 0]) else "",
        "區(市鄉鎮)": df.iloc[5, 1] if len(df.columns) > 1 and pd.notna(df.iloc[5, 1]) else "",
        "地址": df.iloc[5, 2] if len(df.columns) > 2 and pd.notna(df.iloc[5, 2]) else "",
        "組別": df.iloc[6, 1] if len(df) > 6 and pd.notna(df.iloc[6, 1]) else ""
    }

    # Create DataFrame and save
    output_df = pd.DataFrame([data_dict], columns=["建檔日期", "姓名", "性別", "出生年月日", "手機", "TEL", "市(縣)", "區(市鄉鎮)", "地址", "組別"])
    output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"CSV transformed and saved to {output_file}")

def bulk_transform(input_directory, output_directory):
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # Process each CSV file in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith(".csv"):
            input_file = os.path.join(input_directory, filename)
            output_file = os.path.join(output_directory, f"transformed_{filename}")
            transform_csv(input_file, output_file)

# Example usage
input_directory = 'members/'         # Directory containing original CSV files
output_directory = 'transformed/'           # Updated directory to save transformed CSV files
bulk_transform(input_directory, output_directory)
