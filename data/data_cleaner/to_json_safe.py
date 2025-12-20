import pandas as pd
import numpy as np
import math
def df_to_json_safe_records(df: pd.DataFrame):
    records = []

    for row in df.to_dict("records"):
        clean_row = {}

        for k, v in row.items():

            # numpy scalar → python scalar
            if isinstance(v, np.generic):
                v = v.item()

            # kill NaN / Inf
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                v = None

            clean_row[k] = v

        records.append(clean_row)

    return records