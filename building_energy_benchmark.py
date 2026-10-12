"""Compare simulated building energy intensity with a simple weather adjustment."""

import argparse
import csv
import json
import random
from pathlib import Path


SEED = 20261012
BUILDINGS = (
    ("North Hall", 8200, 0.76, 132, 1.10),
    ("Library", 6100, 0.52, 158, 1.06),
    ("Science Block", 9400, 0.68, 174, 1.14),
    ("Arts Center", 5300, 0.43, 119, 1.02),
    ("Dormitory A", 12500, 0.81, 146, 1.12),
    ("Sports Hall", 7200, 0.61, 191, 1.08),
    ("Admin Building", 4800, 0.57, 127, 1.04),
    ("Teaching Block", 10300, 0.71, 151, 1.09),
)


def build_rows(seed: int = SEED) -> list[dict[str, float | str]]:
    """Create synthetic annual meter totals and weather-normalized indicators."""
    rng = random.Random(seed)
    rows = []
    for name, area, weather_share, reference_eui, weather_index in BUILDINGS:
        noise = rng.uniform(0.97, 1.03)
        adjustment = 1 + (weather_index - 1) * weather_share
        annual_kwh = round(area * reference_eui * adjustment * noise, 2)
        raw_eui = annual_kwh / area
        normalized_eui = raw_eui / adjustment
        rows.append({
            "building": name,
            "floor_area_m2": area,
            "weather_index": weather_index,
            "weather_sensitive_share": weather_share,
            "annual_energy_kwh": round(annual_kwh, 2),
            "raw_eui_kwh_m2": round(raw_eui, 3),
            "weather_normalized_eui_kwh_m2": round(normalized_eui, 3),
        })

    median_eui = sorted(row["weather_normalized_eui_kwh_m2"] for row in rows)[len(rows) // 2]
    for row in rows:
        row["benchmark_index"] = round(row["weather_normalized_eui_kwh_m2"] / median_eui * 100, 1)
    return sorted(rows, key=lambda row: row["benchmark_index"])


def write_outputs(output_dir: Path, rows: list[dict[str, float | str]]) -> None:
    data_dir = output_dir / "data"
    results_dir = output_dir / "results"
    data_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with (data_dir / "simulated_buildings.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "data_type": "deterministic synthetic teaching data",
        "seed": SEED,
        "building_count": len(rows),
        "weather_adjustment": "normalized_eui = raw_eui / (1 + (weather_index - 1) * weather_sensitive_share)",
        "lower_index_means": "lower weather-normalized energy intensity than the simulated group median",
        "ranking": rows,
    }
    (results_dir / "benchmark.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main(output_dir: Path | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compare simulated buildings by weather-normalized energy intensity.")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    target = output_dir or args.output_dir
    rows = build_rows()
    write_outputs(target, rows)
    print(f"Wrote {len(rows)} simulated buildings to {target / 'results' / 'benchmark.json'}")
    for row in rows:
        print(f"{row['building']:<18} normalized EUI {row['weather_normalized_eui_kwh_m2']:>6} kWh/m2  index {row['benchmark_index']}")


if __name__ == "__main__":
    main()
