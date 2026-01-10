from manage_db.db_manager import DbManager


if __name__ == "__main__":
    db = DbManager("jp_realestate",None)
    tables = db.list_tables()
    print(tables)
    db.close_conn()