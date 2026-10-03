from app.database import SessionLocal
from app import models, utils


def create_admin():
    db = SessionLocal()

    try:
        email = input("Admin email: ")
        username = input("Admin username: ")
        password = input("Admin password: ")

        existing_user = (
            db.query(models.User)
            .filter(
                (models.User.email == email)
                | (models.User.username == username)
            )
            .first()
        )

        if existing_user:
            print("A user with that email or username already exists.")
            return

        admin = models.User(
            email=email,
            username=username,
            password=utils.hash_password(password),
            role=models.UserRole.ADMIN,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"Admin created successfully with id={admin.id}")

    finally:
        db.close()


if __name__ == "__main__":
    create_admin()