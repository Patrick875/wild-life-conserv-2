from extensions import db
from database.baseModel import BaseModel

roles_permissions=db.Table(
    'roles_permissions',
    db.Column('role_id',db.Integer,db.ForeignKey('roles.id'),primary_key=True),
    db.Column('permission_id',db.Integer,db.ForeignKey('permissions.id'),primary_key=True)
)


class Role(BaseModel):
    __tablename__="roles"

    name=db.Column(db.String(50),nullable=False)
    description=db.Column(db.String(255))
    users=db.relationship("User",back_populates='role')
    permissions=db.relationship(
        "Permission",
        secondary=roles_permissions,
        back_populates="role"
    )

class Permission(BaseModel):
    __tablename__="permissions"
    name=db.Column(db.String(255),nullable=False)
    description=db.Column(db.String(255))
    roles=db.relationship(
        "Role",
        secondary=roles_permissions,
        back_populates='permissions'

    )
