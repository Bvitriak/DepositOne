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
            {
                "name": "Country List",
                "type": "GET",
                "path": "/api/countries",
                "description": "Return the list of countries for depositor forms",
                "auth": "JWT",
            },
            {
                "name": "Depositor List",
                "type": "GET",
                "path": "/api/depositors",
                "description": "Search, sort and page through depositors",
                "auth": "JWT",
            },
            {
                "name": "Depositor Create",
                "type": "POST",
                "path": "/api/depositors",
                "description": "Create a new depositor card",
                "auth": "JWT",
            },
            {
                "name": "Depositor Read",
                "type": "GET",
                "path": "/api/depositors/",
                "description": "Return a single depositor by identifier",
                "auth": "JWT",
            },
            {
                "name": "Depositor Update",
                "type": "PUT",
                "path": "/api/depositors/",
                "description": "Save changes to an existing depositor",
                "auth": "JWT",
            },
            {
                "name": "Depositor Delete",
                "type": "DELETE",
                "path": "/api/depositors/",
                "description": "Delete a depositor without active deposits",
                "auth": "JWT",
            },
        ]
    }
