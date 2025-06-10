# Garmin Strength Data Extractor

This project parses and extracts structured data from exported Garmin Connect `.fit` files specifically for **strength training activities**. It outputs a clean `.csv` file (or optionally `.xlsx`) with key metrics per set, including reps, weight, and training volume.

## 🏋️‍♂️ Purpose

Garmin Connect does not offer detailed trend views per exercise. This tool lets you:

* Aggregate all your strength workouts
* Analyze your reps, weights, and volume per exercise
* Feed the data into Excel or another dashboard tool for visualization

## ✅ Features

* Filters for only **strength training** `.fit` files
* Extracts:

  * Date of activity
  * Exercise category (e.g., "bench\_press")
  * Exercise name (e.g., "incline\_bench\_press")
  * Reps, weight (kg), and calculated volume (kg)
* Automatically maps Garmin's internal codes to human-readable exercise names
* CLI progress bar while processing
* Multiprocessing support for fast batch execution

## 🛠 Requirements

* Python 3.8+
* `pandas`
* `fitparse`
* `tqdm`

Install with:

```bash
pip install pandas fitparse tqdm
```

## 📂 Usage

Place all your `.fit` files in a `fit/` folder and run:

```bash
python main.py
```

This creates `strength_training_log.csv` with your parsed data.

## 🗃 Output Example

| date       | exercise\_category | exercise\_specific    | reps | weight\_kg | volume\_kg |
| ---------- | ------------------ | --------------------- | ---- | ---------- | ---------- |
| 2024-06-10 | bench\_press       | incline\_bench\_press | 10   | 60         | 600        |

## 📌 Notes

* If an exercise subtype is missing, it falls back to the category.
* Invalid `.fit` files or unsupported activity types are skipped.

## 📜 License

MIT License