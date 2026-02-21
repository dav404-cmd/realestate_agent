from manage_db.db_manager import DbManager


if __name__ == "__main__":
    db = DbManager("jp_realestate",None)
    df = db.load_data()
    print(df.columns)
    print(df.info)