from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import pandas as pd


class ProductLockValidationError(Exception):
    """Raised when the DOO U product lock files are missing or inconsistent."""


@dataclass(frozen=True)
class Variable:
    code: str
    name: str
    weight_percent: float
    metric_count: int | None = None


@dataclass(frozen=True)
class AssessmentArea:
    code: str
    name: str
    variable_code: str
    result_area: str | None = None
    primary_stage_relevance: str | None = None


@dataclass(frozen=True)
class MetricSignal:
    metric_id: str
    driver_code: str
    variable_code: str
    raw: dict[str, Any]


@dataclass(frozen=True)
class ProductLock:
    variables: list[Variable]
    assessment_areas: list[AssessmentArea]
    metrics: list[MetricSignal]

    @property
    def variable_by_code(self) -> dict[str, Variable]:
        return {v.code: v for v in self.variables}

    @property
    def driver_by_code(self) -> dict[str, AssessmentArea]:
        return {d.code: d for d in self.assessment_areas}


def _normalise_col(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).strip().lower())


def _find_file(root: Path, contains: str) -> Path:
    matches = [p for p in root.rglob("*") if p.is_file() and contains.lower() in p.name.lower()]
    if not matches:
        raise ProductLockValidationError(f"Could not find product lock file containing: {contains}")
    return sorted(matches, key=lambda p: len(str(p)))[0]


def _read_table(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        raise ProductLockValidationError(f"Unsupported file type: {path}")

    df = df.dropna(how="all")
    if df.empty:
        raise ProductLockValidationError(f"Product lock file is empty: {path}")
    return df


def _col(df: pd.DataFrame, *candidates: str, required: bool = True) -> str | None:
    lookup = {_normalise_col(c): c for c in df.columns}
    for candidate in candidates:
        key = _normalise_col(candidate)
        if key in lookup:
            return lookup[key]

    # softer contains match
    for candidate in candidates:
        key = _normalise_col(candidate)
        for norm, original in lookup.items():
            if key in norm or norm in key:
                return original

    if required:
        raise ProductLockValidationError(
            f"Could not find required column. Tried: {', '.join(candidates)}. "
            f"Available: {list(df.columns)}"
        )
    return None


def _parse_percent(value: Any) -> float:
    if pd.isna(value):
        raise ProductLockValidationError("Blank weight value found.")
    text = str(value).strip().replace("%", "")
    number = float(text)
    if 0 < number <= 1:
        number *= 100
    return number


def _clean_code(value: Any, prefix: str) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    match = re.search(rf"{prefix}\d{{2,3}}", text)
    return match.group(0) if match else text


def load_product_lock(root: str | Path = "product_lock") -> ProductLock:
    root = Path(root)
    if not root.exists():
        raise ProductLockValidationError(f"Product lock folder does not exist: {root}")

    variable_file = _find_file(root, "12_Variable_Lock")
    driver_file = _find_file(root, "24_Assessment_Area_Lock")
    metric_file = _find_file(root, "121_Metric_Registry")

    variables_df = _read_table(variable_file)
    drivers_df = _read_table(driver_file)
    metrics_df = _read_table(metric_file)

    variable_code_col = _col(variables_df, "code", "variable", "variable_code")
    variable_name_col = _col(variables_df, "funding conversion variable", "variable name", "report name", "result area", "name")
    weight_col = _col(variables_df, "weight", "default weight")
    metric_count_col = _col(variables_df, "metrics", "metric count", required=False)

    variables: list[Variable] = []
    for _, row in variables_df.iterrows():
        code = _clean_code(row[variable_code_col], "R")
        if not code.startswith("R"):
            continue
        metric_count = None
        if metric_count_col and not pd.isna(row[metric_count_col]):
            metric_count = int(float(str(row[metric_count_col]).replace("%", "").strip()))
        variables.append(
            Variable(
                code=code,
                name=str(row[variable_name_col]).strip(),
                weight_percent=_parse_percent(row[weight_col]),
                metric_count=metric_count,
            )
        )

    if len(variables) != 12:
        raise ProductLockValidationError(f"Expected 12 variables, found {len(variables)}.")

    weight_total = round(sum(v.weight_percent for v in variables), 6)
    if abs(weight_total - 100.0) > 0.01:
        raise ProductLockValidationError(f"Variable weights must total 100%, found {weight_total}%.")

    variable_codes = {v.code for v in variables}

    driver_code_col = _col(drivers_df, "driver", "driver code", "assessment area", "assessment area code")
    driver_name_col = _col(drivers_df, "driver name", "assessment area name", "name")
    driver_variable_col = _col(drivers_df, "variable", "variable code")
    result_area_col = _col(drivers_df, "result area", required=False)
    stage_col = _col(drivers_df, "primary stage relevance", "stage", required=False)

    drivers: list[AssessmentArea] = []
    for _, row in drivers_df.iterrows():
        code = _clean_code(row[driver_code_col], "D")
        if not code.startswith("D"):
            continue
        variable_code = _clean_code(row[driver_variable_col], "R")
        if variable_code not in variable_codes:
            raise ProductLockValidationError(f"Driver {code} maps to unknown variable {variable_code}.")
        drivers.append(
            AssessmentArea(
                code=code,
                name=str(row[driver_name_col]).strip(),
                variable_code=variable_code,
                result_area=str(row[result_area_col]).strip() if result_area_col else None,
                primary_stage_relevance=str(row[stage_col]).strip() if stage_col else None,
            )
        )

    if len(drivers) != 24:
        raise ProductLockValidationError(f"Expected 24 assessment areas/drivers, found {len(drivers)}.")

    driver_codes = {d.code for d in drivers}

    metric_id_col = _col(metrics_df, "metric_id", "metric id", "metric", "code", required=False)
    metric_driver_col = _col(metrics_df, "driver_id", "driver", "driver code", "assessment area", required=False)
    metric_variable_col = _col(metrics_df, "variable_id", "variable", "variable code", required=False)

    metrics: list[MetricSignal] = []
    for i, row in metrics_df.iterrows():
        raw = {str(k): row[k] for k in metrics_df.columns}

        metric_id = ""
        if metric_id_col and not pd.isna(row[metric_id_col]):
            metric_id = str(row[metric_id_col]).strip()
        if not metric_id:
            metric_id = f"M{i + 1:03d}"

        driver_code = _clean_code(row[metric_driver_col], "D") if metric_driver_col else ""
        variable_code = _clean_code(row[metric_variable_col], "R") if metric_variable_col else ""

        if not driver_code:
            raise ProductLockValidationError(f"Metric {metric_id} has no driver mapping.")
        if not variable_code:
            raise ProductLockValidationError(f"Metric {metric_id} has no variable mapping.")
        if driver_code not in driver_codes:
            raise ProductLockValidationError(f"Metric {metric_id} maps to unknown driver {driver_code}.")
        if variable_code not in variable_codes:
            raise ProductLockValidationError(f"Metric {metric_id} maps to unknown variable {variable_code}.")

        expected_variable = next(d.variable_code for d in drivers if d.code == driver_code)
        if variable_code != expected_variable:
            raise ProductLockValidationError(
                f"Metric {metric_id} maps to driver {driver_code} under {expected_variable}, "
                f"but metric variable is {variable_code}."
            )

        metrics.append(
            MetricSignal(
                metric_id=metric_id,
                driver_code=driver_code,
                variable_code=variable_code,
                raw=raw,
            )
        )

    if len(metrics) != 121:
        raise ProductLockValidationError(f"Expected 121 metric signals, found {len(metrics)}.")

    return ProductLock(variables=variables, assessment_areas=drivers, metrics=metrics)
