# clean_data.py
with open("input.txt", "r") as f:
    lines = f.readlines()

# Filter out lines that are just Timestamps
clean_lines = [line for line in lines if "Timestamp:" not in line]

with open("input.txt", "w") as f:
    f.writelines(clean_lines)

print("🧹 Data Scrubbed. Timestamps removed.")