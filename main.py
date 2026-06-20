from sqlalchemy import create_engine, inspect
import json

db_url = "sqlite:///company.db"


def getSchema(db_url):
    schema = {}

    engine = create_engine(db_url)
    inspector = inspect(engine)

    for table_names in inspector.get_table_names():
        colums = inspector.get_columns(table_names)
        schema[table_names] = [col["name"] for col in colums]
    return json.dumps(schema)


print(getSchema(db_url))
