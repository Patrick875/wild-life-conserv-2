from app import create_app
from extensions import db
from auth.models import Role,Permission

app = create_app()

ROLE_PERMISSIONS = {
    "ADMIN": {
        "description": "Full system administrator with access to all platform features.",
        "permissions": [
            ("role:manage", "Allows managing roles."),
            ("permission:manage", "Allows managing permissions."),
            ("user:manage", "Allows managing users."),

            ("warning:create", "Allows creating warning submissions."),
            ("warning:view:any", "Allows viewing all warning submissions."),
            ("warning:view:own", "Allows viewing own warning submissions."),
            ("warning:update:any", "Allows updating any warning submission."),
            ("warning:update:own", "Allows updating own warning submissions."),
            ("warning:delete:any", "Allows deleting any warning submission."),

            ("warning_feedback:create", "Allows creating feedback on warning submissions."),
            ("warning_feedback:view:any", "Allows viewing all warning feedback."),
            ("warning_feedback:update:any", "Allows updating any warning feedback."),
            ("warning_feedback:delete:any", "Allows deleting warning feedback."),

            ("area_warning_feed:view", "Allows viewing active warnings in the user's area."),
            ("dashboard:view", "Allows viewing dashboard information."),
            ("reports:view", "Allows viewing reports and analytics."),
        ],
    },

    "PARK_GUARD": {
        "description": "Park guard responsible for monitoring warnings and responding to farmer reports.",
        "permissions": [
            ("warning:create", "Allows creating warning submissions."),
            ("warning:view:any", "Allows viewing all warning submissions."),
            ("warning:view:own", "Allows viewing own warning submissions."),
            ("warning:update:any", "Allows updating any warning submission."),

            ("warning_feedback:create", "Allows creating feedback on warning submissions."),
            ("warning_feedback:view:any", "Allows viewing all warning feedback."),
            ("warning_feedback:update:own", "Allows updating own warning feedback."),

            ("area_warning_feed:view", "Allows viewing active warnings in the user's area."),
            ("dashboard:view", "Allows viewing dashboard information."),
        ],
    },

    "FARMER": {
        "description": "Farmer who can submit wildlife warnings, manage own submissions, and view feedback.",
        "permissions": [
            ("warning:create", "Allows creating warning submissions."),
            ("warning:view:own", "Allows viewing own warning submissions."),
            ("warning:update:own", "Allows updating own warning submissions."),
            ("warning_feedback:view:own", "Allows viewing feedback on own warning submissions."),
            ("area_warning_feed:view", "Allows viewing active warnings in the user's area."),
        ],
    },
}


def seed_roles_and_permissions():
    with app.app_context():
        for role_name, role_data in ROLE_PERMISSIONS.items():
            role = Role.query.filter_by(name=role_name).first()

            if not role:
                role = Role(
                    name=role_name,
                    description=role_data["description"]
                )
                db.session.add(role)
            else:
                role.description = role_data["description"]

            for permission_name, permission_description in role_data["permissions"]:
                permission = Permission.query.filter_by(name=permission_name).first()

                if not permission:
                    permission = Permission(
                        name=permission_name,
                        description=permission_description
                    )
                    db.session.add(permission)
                else:
                    permission.description = permission_description

                if permission not in role.permissions:
                    role.permissions.append(permission)

        db.session.commit()
        print("Roles and permissions seeded successfully.")


if __name__ == "__main__":
    seed_roles_and_permissions()