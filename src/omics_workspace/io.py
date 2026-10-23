from pathlib import Path
from typing import IO

import pandas as pd


def read_table(file:IO[bytes],filename:str) -> pd.DataFrame:
    suffix = Path(filename).suffix.lower()
    separator = "\t" if suffix == ".tsv" else ","
    return pd.read_csv(file,sep=separator,index_col=0)