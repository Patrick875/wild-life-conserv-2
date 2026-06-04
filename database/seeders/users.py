from werkzeug.security import generate_password_hash

from app import create_app
from extensions import db
from users.models import User
from auth.models import Role

app = create_app()


def seed_admin_user():
    with app.app_context():
        admin_role = Role.query.filter_by(name="ADMIN").first()

        if not admin_role:
            raise Exception("ADMIN role not found. Seed RBAC first.")

        existing_admin = User.query.filter_by(email="admin@wildlife.com").first()

        if existing_admin:
            print("Initial admin user already exists.")
            return

        admin_user = User(
            full_name="System Administrator",
            username="admin",
            email="admin@wildlife.com",
            phone_number=None,
            occupation="Administrator",
            organization="Wildlife Conservation Platform",
            role_id=admin_role.id,
            passxword_hash=generate_password_hash("Admin@12345"),
            is_verified=True,
            is_active=True,
        )

        db.session.add(admin_user)
        db.session.commit()

        print("Initial admin user created successfully.")

if __name__ == "__main__":
    seed_admin_user()