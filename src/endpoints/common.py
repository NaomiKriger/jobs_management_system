from src.models.event import Event


def get_event_names_from_db(event_names):
    return Event.query.filter(Event.event_name.in_(event_names)).all()


def add_entry(entry, db_instance):
    db_instance.session.add(entry)
    db_instance.session.commit()
