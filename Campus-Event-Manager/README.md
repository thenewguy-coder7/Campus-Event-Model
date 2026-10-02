# Campus Event Manager

A Django project that models how events are organised on a university campus.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (VS Code terminal)
# source .venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
python manage.py makemigrations events
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/admin/ to add venues, events and RSVPs.

## Models and relationships

| Relationship | How it is built |
|---|---|
| One user organises many events | `Event.organizer` -> `ForeignKey(User)` |
| One venue hosts many events | `Event.venue` -> `ForeignKey(Venue)` |
| Many users attend many events | `RSVP` through-model between `User` and `Event` |
| Event status | `Event.State` (`TextChoices`): draft, published, cancelled, completed |
| RSVP answer | `RSVP.Answer` (`TextChoices`): going, maybe, declined |

Extra safeguards: an event must end after it starts, and a user can RSVP to a given event only once.
