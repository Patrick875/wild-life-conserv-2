from app import create_app
from dotenv import load_dotenv
import os 
from flask.cli import with_appcontext

load_dotenv()
#seeders 
from database.seeders.rbac import seed_roles_and_permissions
from database.seeders.users import seed_admin_user
from database.seeders.seed import run_seeders


app=create_app()
if __name__=="__main__":
    port= os.getenv('PORT')
    debug=os.getenv('FLASK_DEBUG')
    app.run(port=port,debug=True)

@app.cli.command("seed-rbac")
@with_appcontext
def seed_rbac():
    seed_roles_and_permissions()

@app.cli.command("seed-users")
@with_appcontext
def seed_users():
    seed_admin_user()

@app.cli.command("seed-all")
@with_appcontext
def seed_all():
    run_seeders()