from app import app, db
from models import User, Task
from faker import Faker

fake = Faker()

with app.app_context():
    print("Seeding database...")

    Task.query.delete()
    User.query.delete()

    user = User(username="demo")
    user.password_hash = "password"  # this hashes to a real bcrypt string

    db.session.add(user)
    db.session.commit()

    for _ in range(10):
        task = Task(
            title=fake.sentence(nb_words=4),
            description=fake.paragraph(nb_sentences=2),
            user_id=user.id
        )
        db.session.add(task)

    db.session.commit()
    print("Done seeding!")