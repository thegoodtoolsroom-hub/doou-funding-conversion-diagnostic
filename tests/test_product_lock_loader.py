from pathlib import Path
import shutil

import pandas as pd
import pytest

from engine.product_lock_loader import ProductLockValidationError, load_product_lock


ROOT = Path("product_lock")


def _find_column_containing(df: pd.DataFrame, word: str) -> str:
    matches = [c for c in df.columns if word.lower() in c.lower()]
    if not matches:
        raise AssertionError(f"No column containing '{word}' found. Columns: {list(df.columns)}")
    return matches[0]


def test_product_lock_loads_required_files():
    lock = load_product_lock(ROOT)
    assert len(lock.variables) == 12
    assert len(lock.assessment_areas) == 24
    assert len(lock.metrics) == 121


def test_variable_weights_total_100_percent():
    lock = load_product_lock(ROOT)
    total = sum(v.weight_percent for v in lock.variables)
    assert round(total, 2) == 100.00


def test_every_driver_maps_to_existing_variable():
    lock = load_product_lock(ROOT)
    variable_codes = {v.code for v in lock.variables}
    for driver in lock.assessment_areas:
        assert driver.variable_code in variable_codes


def test_every_metric_maps_to_existing_driver_and_variable():
    lock = load_product_lock(ROOT)
    driver_codes = {d.code for d in lock.assessment_areas}
    variable_codes = {v.code for v in lock.variables}
    for metric in lock.metrics:
        assert metric.driver_code in driver_codes
        assert metric.variable_code in variable_codes


def test_bad_weight_total_fails(tmp_path):
    copied = tmp_path / "product_lock"
    shutil.copytree(ROOT, copied)

    variable_file = next(copied.rglob("*12_Variable_Lock*.csv"))
    df = pd.read_csv(variable_file)

    weight_col = _find_column_containing(df, "weight")

    # Use a numeric value so Pandas allows the edit even when the column is numeric.
    # The loader should then reject the total because weights no longer add to 100%.
    df.loc[0, weight_col] = 999
    df.to_csv(variable_file, index=False)

    with pytest.raises(ProductLockValidationError):
        load_product_lock(copied)


def test_bad_driver_mapping_fails(tmp_path):
    copied = tmp_path / "product_lock"
    shutil.copytree(ROOT, copied)

    driver_file = next(copied.rglob("*24_Assessment_Area_Lock*.csv"))
    df = pd.read_csv(driver_file)

    variable_col = _find_column_containing(df, "variable")

    # Force the first driver to map to a variable that does not exist.
    df.loc[0, variable_col] = "R99"
    df.to_csv(driver_file, index=False)

    with pytest.raises(ProductLockValidationError):
        load_product_lock(copied)
