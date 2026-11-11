from pathlib import Path
from polars import DataFrame

def load_to_parquet(df: DataFrame, path: str | Path) -> None:
    df.write_parquet(file=path)

def load_to_sqlite(df: DataFrame, path: str | Path) -> None:
    df.write_database(
        table_name="tunisair_retards20",
        connection="sqlite:///{0}".format(path),
        engine="adbc",
        if_table_exists="replace"
    )


