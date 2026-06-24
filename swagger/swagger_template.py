
from swagger.definitions.auth import auth_definitions
swagger_template={
    "info":{
        "title":"Wild life conservation app API v1.0",
        "version":"1.0.0",
        "description":"""
        Local Development

        - http://localhost:4800

        Development

        - https://wild-life-conserv-2.onrender.com
        """
    
    },
    "definitions":{
        **auth_definitions
    },
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Paste: Bearer <access_token>"
        },
    },
    "swagger":"2.0.0"
}