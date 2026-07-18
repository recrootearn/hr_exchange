from app import app, db
from sqlalchemy import create_engine, text

# SQLite database
sqlite_engine = create_engine("sqlite:///database.db")

with app.app_context():

    # MySQL database
    mysql_engine = db.engine

    sqlite_conn = sqlite_engine.connect()
    mysql_conn = mysql_engine.connect()

    # Disable foreign key checks
    mysql_conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))

    tables = db.metadata.sorted_tables

    for table in tables:
        table_name = table.name
        print(f"Migrating {table_name}...")

        try:
            rows = sqlite_conn.execute(
                text(f"SELECT * FROM {table_name}")
            ).mappings().all()
        except Exception as e:
            print(f"  -> Skipped ({e})")
            continue

        if not rows:
            print("  -> No data")
            continue

        for row in rows:
            mysql_conn.execute(
                table.insert().values(**dict(row))
            )

        mysql_conn.commit()
        print(f"  -> {len(rows)} rows copied")

    mysql_conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    mysql_conn.commit()

    sqlite_conn.close()
    mysql_conn.close()

    print("\n✅ Migration completed successfully!")