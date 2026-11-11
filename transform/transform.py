import asyncio
from polars import LazyFrame, Series, struct, List, lit
from polars.datatypes import Struct, String
from datetime import date
from .async_tr import async_scrape
from re import sub, match
from datetime import time

def create_url(type_vol: str = "depart", express: bool = False, d: date = date.today()):
    return "https://www.aeroport-de-tunis-carthage.com/tunisie-aeroport-de-tunis-carthage-vol-{0}-compagnie-{1}+-date-{2}".format(
        type_vol,"TUNISAIR" + ("+EXPRESS" if express else ""), d.strftime('%Y-%m-%d')
    )

def fetch_all(s: Series) -> Series:
    return s.map_elements(
        function=lambda x: print(x) or x,
        return_dtype=String
    )

VOL_STRUCT = Struct({
    "heure_locale": String,
    "origine": String,
    "dest": String,
    "num_vol": String,
    "statut": String
})


def add_url_to_frame(lf: LazyFrame) -> LazyFrame:
    return lf.with_columns(
        url = struct("d", "express", "type_vol").map_elements(lambda de: create_url(**de), return_dtype=String)
    ).drop("express")


def transform_data(lf: LazyFrame) -> LazyFrame:
    lf2 = add_url_to_frame(lf)
    urls = lf2.select("url").collect().to_series().to_list()
    raws = asyncio.run(async_scrape(urls))
    s = Series(name="raws", values=raws, dtype=List(VOL_STRUCT))
    return (lf2
        .drop("url")
        .with_columns(lit(s))
        .rename({"d": "planned_date"})
        .explode("raws")
        .unnest("raws")
    )
    

def purify_statut(s: str) -> str:
    return sub(string=s, pattern=r"(\s\d{2}(:\d{2}){1,2})?", repl="")

def get_time_from_statut(s: str) -> time:
    t = match(string=s, pattern=r"(?:.+) (\d{2}:\d{2}(?::\d{2})?)")
    try:
        return time.strptime(t.group(1), "%H:%M:%S")
    except Exception as e:
        try:
            return time.strptime(t.group(1), "%H:%M").replace(second=0)
        except Exception as e:
            return None

