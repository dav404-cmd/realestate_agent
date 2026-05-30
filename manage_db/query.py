import pandas as pd
from pydantic import BaseModel
from typing import Optional, List

from psycopg2 import sql

from manage_db.db_manager_v1 import DbManagerV1
from psycopg2.extras import RealDictCursor

def build_db_profile(df:pd.DataFrame):
    profile = {}
    ignore = ["url","building_description","id"]
    for col in df.columns:
        if col in ignore:
            continue

        series = df[col].dropna()

        if series.empty:
            continue

        if pd.api.types.is_numeric_dtype(series):
            profile[col] = {
                "type":"numeric",
                "min" : float(series.min()),
                "max" : float(series.max()),
                "avg" : float(series.mean())
            }
        else:
            profile[col] = {
                "type" : "categorical",
                "unique_samples" : list(series.unique()[:20])
            }
    return profile

class PropertyQuery(BaseModel):
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    target_price : Optional[int] = None
    min_size: Optional[float] = None
    max_size: Optional[float] = None
    zoning: Optional[str] = None
    structure: Optional[str] = None
    occupancy: Optional[str] = None
    prefecture : Optional[str] = None
    city : Optional[str] = None
    district : Optional[str] = None
    limit: int = 20
    sort_by: str = "price_yen"
    sort_order: str = "asc"

def build_property_query(q : PropertyQuery,table_name : str ):
    query  = sql.SQL("""
    SELECT * 
    FROM {table}
    WHERE status = 'active'
    """).format(table = sql.Identifier(table_name))

    params = {}
    order_clauses = []

    if q.min_price is not None:
        query += sql.SQL(" AND price_yen >= %(min_price)s")
        params["min_price"] = q.min_price

    if q.max_price is not None:
        query += sql.SQL(" AND price_yen <= %(max_price)s")
        params["max_price"] = q.max_price

    if q.target_price is not None:
        order_clauses.append(
            sql.SQL("ABS(price_yen - %(target_price)s)")
        )
        params["target_price"] = q.target_price

    if q.min_size is not None:
        query += sql.SQL(" AND NULLIF(data ->> 'size','')::numeric >= %(min_size)s")
        params["min_size"] = q.min_size

    if q.max_size is not None:
        query += sql.SQL(" AND NULLIF(data ->> 'size','')::numeric <= %(max_size)s")
        params["max_size"] = q.max_size

    if q.prefecture is not None:
        query += sql.SQL(" AND (data ->> 'prefecture') = %(prefecture)s")
        params["prefecture"] = q.prefecture

    if q.city is not None:
        query += sql.SQL(" AND (data ->> 'city') = %(city)s")
        params["city"] = q.city

    if q.district is not None:
        query += sql.SQL(" AND (data ->> 'district') = %(district)s")
        params["district"] = q.district

    if q.zoning is not None:
        query += sql.SQL(" AND (data ->> 'zoning') = %(zoning)s")
        params["zoning"] = q.zoning

    if q.structure is not None:
        query += sql.SQL(" AND (data ->> 'structure') = %(structure)s")
        params["structure"] = q.structure

    if q.occupancy is not None:
        query += sql.SQL(" AND (data ->> 'occupancy') = %(occupancy)s")
        params["occupancy"] = q.occupancy

    allowed_sorts = { #todo:map and use sql to apply null protection
        "price_yen",
        "size",
        "year_built",
        "last_update"
    }

    sort_by = q.sort_by if q.sort_by in allowed_sorts else "last_update"
    order = "ASC" if q.sort_order == "asc" else "DESC"

    order_clauses.append(
        sql.SQL("{} {}").format(
        sql.Identifier(sort_by),
        sql.SQL(order)
    )
    )

    query += sql.SQL(" ORDER BY ")
    query += sql.SQL(",").join(order_clauses)
    query += sql.SQL(" LIMIT %(limit)s")

    params["limit"] = q.limit

    return query,params

def query_property(q:PropertyQuery,table_name:str , conn):

    query,params  = build_property_query(q , table_name)
    with conn.cursor(cursor_factory=RealDictCursor) as cur :
        cur.execute(query,params)
        data = cur.fetchall()

    return data



if __name__ == "__main__":
    db = DbManagerV1(table_name="jp_realestate_v1")
    conn = db.conn

    q = PropertyQuery(
        max_price=400_000_000,
        min_size=80,
        zoning="Residential"
    )

    results = query_property(q,"jp_realestate_v1",conn)

    print(results)
