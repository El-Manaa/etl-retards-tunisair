from polars.datatypes import Time, Utf8
from extract.extract import create_initial_frame, use_parquet_file
from transform.transform import transform_data, get_time_from_statut
from polars import col
from load.load import load_to_parquet, load_to_sqlite

def create_data_to_parquet() -> None:
    lf = create_initial_frame()
    lf2 = transform_data(lf)
    load_to_parquet(lf2.collect(), "checkpoint_data.parquet")

def get_data_from_parquet() -> None:
    lf = use_parquet_file("checkpoint_data.parquet")
    lf2 = lf.filter(col.heure_locale.str.contains(r"\d{2}:\d{2}:\d{2}")).with_columns(
        heure_reelle = col.statut.map_elements(get_time_from_statut, return_dtype=Time).cast(Utf8),
        heure_locale = col.heure_locale.cast(Utf8),
    )
    df = lf2.collect()
    load_to_sqlite(df, "viz/data/retard_tunisair.db")


def main():
    ...
    get_data_from_parquet()

if __name__ == "__main__":
    main()
