from manage_db.db_manager import DbManager


if __name__ == "__main__":
    db = DbManager("jp_realestate",None)

    db.close_conn()