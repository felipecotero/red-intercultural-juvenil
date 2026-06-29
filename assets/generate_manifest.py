import os
import json
import re

base_dir = "/Volumes/TRITERA 2025/03 GITHUB/red-intercultural-juvenil"
photos_dir = os.path.join(base_dir, "assets/photos_enc_cali_2026")

photos_list = []

# Map folders to day numbers and display labels
day_mappings = {
    "24_06_2026": {"day": "24", "label": "24 de Junio: Hotel y Presentaciones"},
    "25_06_2026": {"day": "25", "label": "25 de Junio: Jornada 1 (Cali/Monumento)"},
    "26_06_2026": {"day": "26", "label": "26 de Junio: Jornada 2 (IUIPC)"},
    "27_06_2026": {"day": "27", "label": "27 de Junio: Jornada 3 (Cierre)"}
}

# Subfolder labels for 25th
subfolder_labels = {
    "01_AM": "Sesión Mañana (AM)",
    "02_PM": "Sesión Tarde (PM)",
    "03_PR": "Monumento y Presentaciones (PR)"
}

for root, dirs, files in os.walk(photos_dir):
    # Find relative directory path from photos_dir
    rel_path = os.path.relpath(root, photos_dir)
    
    # Skip root directory itself if it has no files
    parts = rel_path.split(os.sep)
    day_folder = parts[0]
    sub_folder = parts[1] if len(parts) > 1 else None
    
    if day_folder not in day_mappings:
        continue
        
    day_info = day_mappings[day_folder]
    day_num = day_info["day"]
    day_label = day_info["label"]
    
    # Subcategory
    subcategory = "General"
    if day_num == "25" and sub_folder:
        subcategory = subfolder_labels.get(sub_folder, sub_folder)
        
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')) and not file.startswith('.'):
            # Calculate file paths
            # The HTML will load relative to the project root
            full_path = os.path.join(root, file)
            html_rel_path = os.path.relpath(full_path, base_dir)
            
            # Clean filename to generate a readable title
            # Filename is e.g. "01_rij_cali_boicop_iuipc_24_06_2026.jpg"
            # We want to remove the index prefix (e.g. 01_rij_) and date suffix (e.g. _24_06_2026.jpg)
            clean_name = file
            # Remove index prefix
            clean_name = re.sub(r'^\d+_rij_', '', clean_name, flags=re.IGNORECASE)
            # Remove date suffix
            clean_name = re.sub(r'_\d{2}_\d{2}_\d{4}\.(jpg|jpeg|png)$', '', clean_name, flags=re.IGNORECASE)
            # Remove subfolder keys in name if any
            clean_name = re.sub(r'_(am|pm|pr)$', '', clean_name, flags=re.IGNORECASE)
            # Replace underscores with spaces
            clean_name = clean_name.replace('_', ' ')
            # Title case
            title = clean_name.title().strip()
            
            # Add photo object
            photos_list.append({
                "path": html_rel_path,
                "filename": file,
                "day": day_num,
                "dayLabel": day_label,
                "subcategory": subcategory,
                "title": title
            })

# Sort photos list: first by day, then by subfolder/subcategory, then by filename/index
def get_sort_key(p):
    # Day order: 24, 25, 26, 27
    day_val = int(p["day"])
    # Subfolder order for day 25
    sub_val = 0
    if p["subcategory"] == "Sesión Mañana (AM)":
        sub_val = 1
    elif p["subcategory"] == "Sesión Tarde (PM)":
        sub_val = 2
    elif p["subcategory"] == "Monumento y Presentaciones (PR)":
        sub_val = 3
    # Try to extract the number prefix from the filename (e.g. "01_rij..." -> 1)
    num_match = re.match(r'^(\d+)_', p["filename"])
    num_val = int(num_match.group(1)) if num_match else 999
    
    return (day_val, sub_val, num_val)

photos_list.sort(key=get_sort_key)

# Write output to JS file as a global variable
manifest_js_path = os.path.join(base_dir, "assets/cali_photos_data.js")
with open(manifest_js_path, "w", encoding="utf-8") as f:
    f.write("// Manifest file listing all photos from the Cali 2026 Encounter.\n")
    f.write("// Generated automatically by assets/generate_manifest.py\n\n")
    f.write("const CALI_PHOTOS_DATA = ")
    json.dump(photos_list, f, indent=2, ensure_ascii=False)
    f.write(";\n")

print(f"Successfully generated manifest at {manifest_js_path} with {len(photos_list)} photos.")
