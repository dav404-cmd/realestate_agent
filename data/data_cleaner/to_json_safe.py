import pandas as pd
import numpy as np
import math
import json
from datetime import datetime

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



class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # e.g. "2026-05-19T14:31:00"
        return super().default(obj)

