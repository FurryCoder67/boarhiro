import os

# Get the folder where THIS script is saved
base_path = os.path.dirname(os.path.abspath(__file__))

# UPDATE: Point it to the data folder
file_path = os.path.join(base_path, "data", "input.txt")

if os.path.exists(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    # The filter
    clean_lines = [line for line in lines if "Timestamp:" not in line]

    with open(file_path, "w") as f:
        f.writelines(clean_lines)

    print(f"🧹 Scrubbed: {file_path}")
    print(f"✅ Remaining lines: {len(clean_lines)}")
else:
    print(f"❌ Still missing! I checked: {file_path}")
    # Let's see what IS in data just in case
    data_folder = os.path.join(base_path, "data")
    if os.path.exists(data_folder):
        print(f"Files inside 'data' folder: {os.listdir(data_folder)}")