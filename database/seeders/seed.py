from database.seeders.users import seed_admin_user
from database.seeders.rbac import seed_roles_and_permissions

def run_seeders():
    seed_roles_and_permissions()
    seed_admin_user()

if __name__ == "__main__":
    run_seeders()