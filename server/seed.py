from random import randint, choice as rc

from faker import Faker

from app import app
from models import db, Tasks, User

fake = Faker()

with app.app_context():
    print("Deleting all records...")
    Tasks.query.delete()
    User.query.delete()

    fake = Faker()

    print("Creating users...")
    # make sure users have unique usernames
    users = []
    usernames = []
    for i in range(20):
        username=fake.first_name()
        while username in usernames:
            username=fake.first_name()
        
        usernames.append(username)
        user=User(username=username)
        user.password_hash = 'password123'

        users.append(user)

    db.session.add_all(users)

    print("Creating tasks...")
    tasks=[]
    for i in range(100):

        task=Tasks(
            title=fake.sentence(),
            details=fake.paragraph(nb_sentences=2),
            completed=rc([True, False]),
            due_date=str(fake.future_date())
        )
        task.user=rc(users)
        tasks.append(task)
    db.session.add_all(tasks)
    db.session.commit()
    print("Complete")
