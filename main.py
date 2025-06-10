from fitparse import FitFile
import pandas as pd
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from garmin_fit_sdk.profile import Profile
from tqdm import tqdm

# -------------------------------
# Mappings from Garmin FIT SDK
# -------------------------------
category_map = {
    int(k): v for k, v in Profile['types']['exercise_category'].items()
}

nested_exercise_map = {
    cat.replace('_exercise_name', ''): {
        int(k): v for k, v in exercise_dict.items()
    }
    for cat, exercise_dict in Profile['types'].items()
    if cat.endswith('_exercise_name')
}

# -------------------------------
# Helpers
# -------------------------------
def get_subsport(fitfile):
    for msg in fitfile.get_messages("sport"):
        return msg.get_value("sport"), msg.get_value("sub_sport")
    return None, None

def extract_sets_data(file_path):
    sets = []
    date = None

    try:
        fitfile = FitFile(str(file_path), check_crc=False)  # Disable CRC for speed

        sport, sub_sport = get_subsport(fitfile)
        if sub_sport != "strength_training":
            return []

        for msg in fitfile.get_messages("session"):
            timestamp = msg.get_value("start_time")
            if timestamp:
                date = timestamp.date()

        for msg in fitfile.get_messages("set"):
            if msg.get_value("set_type") != "active":
                continue

            category_code = msg.get_raw_value("category")
            subtype_code = msg.get_raw_value("category_subtype")

            if isinstance(category_code, tuple):
                category_code = category_code[0]
            if isinstance(subtype_code, tuple):
                subtype_code = subtype_code[0]

            category_name = category_map.get(category_code, f"UnknownCategory({category_code})")

            # Default to category name if subtype is missing or not found
            exercise_name = category_name
            if category_name in nested_exercise_map and subtype_code is not None:
                exercise_name = nested_exercise_map[category_name].get(
                    subtype_code, category_name
                )

            reps = msg.get_value("repetitions")
            weight = msg.get_value("weight")
            volume = (reps or 0) * (weight or 0)

            sets.append({
                "date": date,
                "exercise_category": category_name,
                "exercise_specific": exercise_name,
                "reps": reps,
                "weight_kg": weight,
                "volume_kg": volume,
            })

    except Exception as e:
        print(f"Error reading {file_path.name}: {e}")

    return sets

# -------------------------------
# Main Batch Processor
# -------------------------------
def process_fit_files(folder_path, output_csv):
    all_data = []
    file_paths = list(Path(folder_path).glob("*.fit"))

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(extract_sets_data, path): path for path in file_paths}

        for future in tqdm(as_completed(futures), total=len(file_paths), desc="Processing files"):
            result = future.result()
            if result:
                all_data.extend(result)

    print(f"Total sets to save: {len(all_data)}")

    if all_data:
        df = pd.DataFrame(all_data)
        print(f"Saving CSV to: {output_csv}")
        df.to_csv(output_csv, mode='w', header=True, index=False)
    else:
        print("No data extracted.")

# -------------------------------
# Run
# -------------------------------
if __name__ == "__main__":
    process_fit_files("fit_files", "garmin_strength_export.csv")