import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import building_energy_benchmark as benchmark


class BuildingBenchmarkTests(unittest.TestCase):
    def test_generation_is_deterministic_and_normalization_removes_weather_multiplier(self):
        first = benchmark.build_rows()
        self.assertEqual(first, benchmark.build_rows())
        self.assertEqual(len(first), 8)
        for row in first:
            factor = 1 + (row["weather_index"] - 1) * row["weather_sensitive_share"]
            expected = row["annual_energy_kwh"] / row["floor_area_m2"] / factor
            self.assertEqual(row["weather_normalized_eui_kwh_m2"], round(expected, 3))

    def test_ranked_index_is_ordered_and_median_is_about_one_hundred(self):
        rows = benchmark.build_rows()
        indices = [row["benchmark_index"] for row in rows]
        self.assertEqual(indices, sorted(indices))
        self.assertLessEqual(abs(indices[len(indices) // 2] - 100), 2)

    def test_output_files_can_be_reproduced(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir)
            benchmark.write_outputs(out, benchmark.build_rows())
            with (out / "data" / "simulated_buildings.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 8)
            self.assertTrue((out / "results" / "benchmark.json").is_file())


if __name__ == "__main__":
    unittest.main()
