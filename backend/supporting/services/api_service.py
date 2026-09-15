def get_apis():
    return {
        "apis": [
            {
                "name": "Register",
                "type": "POST",
                "path": "/api/register",
                "description": "Create a new user account",
                "auth": "None",
            },
            {
                "name": "Login",
                "type": "POST",
                "path": "/api/login",
                "description": "Sign in and receive an access token",
                "auth": "None",
            },
            {
                "name": "Reset Check",
                "type": "POST",
                "path": "/api/reset-password/check",
                "description": "Check an account before a password reset",
                "auth": "None",
            },
            {
                "name": "Reset Confirm",
                "type": "POST",
                "path": "/api/reset-password/confirm",
                "description": "Save a new password for an account",
                "auth": "None",
            },
            {
                "name": "Dashboard",
                "type": "GET",
                "path": "/api/dashboard",
                "description": "Return dashboard analytics data",
                "auth": "JWT",
            },
            {
                "name": "Api List",
                "type": "GET",
                "path": "/api/apis",
                "description": "Return the list of available endpoints",
                "auth": "JWT",
            },
        ]
    }
