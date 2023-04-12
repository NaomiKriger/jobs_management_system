from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def add_entry(entry, db_instance):
    db_instance.session.add(entry)
    db_instance.session.commit()


def read_table(table_name):
    return table_name.query.all()
