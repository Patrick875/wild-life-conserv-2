from marshmallow import Schema,fields,validate

class LoginSchema(Schema):
    identifier=fields.String(required=True,validate=validate.Length(min=3,max=50))
    password=fields.String(required=True,validate=validate.Length(min=8,max=16))

class SignupSchema(Schema):
     fullName=fields.String(required=True,validate=validate.Length(min=3,max=50))
     email=fields.Email()
     phoneNumber=fields.String(required=True,validate=validate.Regexp(
            r"^\d{8,14}$",
            error="Phone number must consist only of numbers and be between 8 and 14 digits long."
        ))
     occupation=fields.String(required=True)
     organization=fields.String(required=True)
     role=fields.String(required=True)
     password=fields.String(required=True, 
                            validate=validate.Regexp(
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{6,}$",
            error="Password must be at least 6 characters long and contain at least one letter, one number, and one special character."
        ))
     
class ForgotPasswordSchema(Schema):
    email=fields.Email(required=True)

class PasswordResetSchema(Schema):
    reset_token=fields.String(required=True)
    new_password=fields.String(required=True, 
                            validate=validate.Regexp(
            r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{6,}$",
            error="Password must be at least 6 characters long and contain at least one letter, one number, and one special character."
        ))

class PasswordResetVerifySchema(Schema):
    identifier=fields.String(required=True)
    otp=fields.String(required=True,validate=validate.Length(equal=6))
