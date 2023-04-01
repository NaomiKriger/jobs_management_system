def add_entry(entry, db):
    db.session.add(entry)
    db.session.commit()


def read_table(model):
    return model.query.all()
