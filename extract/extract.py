from pathlib import Path
from polars import LazyFrame, date_range, Series, scan_parquet
from datetime import date

def create_initial_frame(
    start: date = date(year=2020, month=1, day=1),
    end: date = date.today()
) -> LazyFrame:
    return LazyFrame(
        date_range(start=start, end=end, eager=True).alias('d')
    ).join(
        Series("express", (True, False)).to_frame().lazy(),
        how="cross"
    ).join(
        Series("type_vol", ("arrivee", "depart")).to_frame().lazy(),
        how="cross"
    )

def use_parquet_file(file: Path) -> LazyFrame:
    return scan_parquet(file)
