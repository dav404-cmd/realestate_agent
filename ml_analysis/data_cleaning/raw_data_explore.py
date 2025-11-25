from manage_db.db_manager import DbManager
import pandas as pd

pd.set_option("display.max_columns", None)



# show all columns
if __name__ == "__main__":
    db = DbManager(table_name="jp_realestate",source=None)
    df = db.load_data()
    print(df.dtypes)


