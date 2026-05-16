from manage_db.db_manager_v1 import DbManagerV1


if __name__ == "__main__":
    db = DbManagerV1("jp_realestate_v1",None)
    df = db.create_table()
