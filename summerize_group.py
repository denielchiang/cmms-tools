import csv
import glob
import os

# Specify the path to your directory containing the CSV files
directory_path = 'transformed'  # Replace with your directory path

# List to hold all the records
records = []

# Iterate over all CSV files in the directory
for file_name in glob.glob(os.path.join(directory_path, '*.csv')):
    with open(file_name, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        # Flag to determine if the file should be processed
        skip_file = False
        for row in reader:
            group = row.get('組別', '').strip()
            name = row.get('姓名', '').strip()
            # Check if '組別' is blank
            if not group:
                skip_file = True
                print(f"Skipping file '{file_name}' because '組別' is blank.")
                break  # Exit the loop since we don't need to process this file
            # Add the record if we're not skipping the file
            records.append({'組別': group, '姓名': name})
        if skip_file:
            continue  # Skip to the next file

# Sort the records by '組別'
records.sort(key=lambda x: x['組別'])

# Write the records to the summary CSV file
with open('group_summary.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
    fieldnames = ['組別', '姓名']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for record in records:
        writer.writerow(record)

print("Summary file 'group_summary.csv' has been created successfully.")
