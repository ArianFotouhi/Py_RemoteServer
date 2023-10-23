from db_manager import Database

def db_connector(fetch, name, email, lounge ):
    database = Database()
    database.create_table()
    database.commit_table(name=name, email=email, lounge=lounge)

    if fetch:
        db_info = database.fetch_table()
        database.close_db()
        return db_info
    else:
        database.close_db()