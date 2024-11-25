# Django Generic API

## Overview

- Django Generic API is a reusable Django app designed to perform dynamic CRUD
  operations based on payloads.
- It provides a flexible way to handle database operations for any Django model
  through REST API endpoints.

## Features

- Dynamic fetch and save operations.
- Dynamic save operation (create or update records) for any Django model.
- Supports relationships and complex data.
- Enabled with pagination and order by features.
- User authentication and management (Login, Registration, Logout, Forgot
  Password).

## Installation

- Install the package

```bash
pip install django_generic_api
```

- Add the app in settings.py

```bash
INSTALLED_APPS = [
        ...
    "django_generic_api",
]

```

---

# Integration

- In settings.py file, integrate the following.

### CORS Setup

- To allow request from other domains, add these CORS settings.
- Adding CORS headers allows your resources to be accessed on other domains.
- This allows in-browser requests to your Django application from other
  origins.

```bash
# CORS Settings

INSTALLED_APPS =[
      ...
  "corsheaders", # CORS package
] 

# Cross origin middleware settings,add middleware class to listen in on responses:
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
          ...
]
# Set allowed hosts to all cross origin references
ALLOWED_HOSTS = ["*"]

# A list of origins that are authorized to make cross-site HTTP requests.
CORS_ALLOWED_ORIGINS = ["*"]  # ex: "https://example.com","http://localhost:8080"

# If True, all origins will be allowed.
CORS_ALLOW_ALL_ORIGINS = True



```

---

### Token based authentication settings

- This package uses rest_framework_simplejwt for token based authentication.
- To allow requests by token, add these settings.

```bash
# Rest framework settings

INSTALLED_APPS = [
    "rest_framework",
    "rest_framework_simplejwt"
]

# Session authentication is for on form based submission.
# Non Session authentication is for token based submission.

# Add the settings as per your requirement 
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        #This is for form submission based authentication.
        "rest_framework.authentication.SessionAuthentication",
        #This is for Token based authentication.
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

from datetime import timedelta
# Set token validity time.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
}
```

---

### Email settings

- When a user registers themselves, a user activation link is sent to them.
- To integrate the email activation, add these seetings.
- [Get your EMAIL_HOST_PASSWORD](https://saurabh-nakoti.medium.com/how-to-set-up-smtp-in-gmail-using-an-app-password-96adffa164b3)

```bash
# These settings configure Django to send emails using Gmail's SMTP server with TLS encryption.

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "user@example.com"  # Your Gmail address
EMAIL_HOST_PASSWORD = "**** **** **** ****"  # Your Gmail password
```

- Set you BASE_URL which includes http protocol and domain name

```bash
BASE_URL = "..."

#example : "http://127.0.0.1:8050", "http://www.abc.com"
```

---

### URL Configuration

- Include the "django_generic_api"  URLs in your project's urls.py:

```bash
path("<url prefix>", include('django_generic_api.urls'))

# example : path("api/", include("django_generic_api.urls")),
```

---

### Limiting User Requests

- This package allows you to limit the number of requests that can be sent
  within a specified time period.
- The default request limits are set as follows:

```bash
  Authenticated users: 2000 requests per 1 hour
  Anonymous users: 20 requests per 1 hour
```

- To customize these default settings, add the following to settings.py:

```bash
# Set 'user' for authenticated users
# Set 'anon' for unauthenticated users

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '.../day',
        'user': '.../day'
    }
}
```

---

# Parameters for requests

- This API supports both session-based and token-based authentication.
- Token generation is not supported via AJAX requests.

## Fetching and Saving Data

- To fetch or save data, the user must be authenticated with either a session
  or a token.
- If the user is making a request via AJAX (page submission), they must be
  logged in using a session.
- If the user is fetching or saving data using a non-session method (not via
  AJAX), they must provide an access token.

---

# Model APIs

## Access Token API

- To log a user in , post data on url '/< prefix >/login/' and set the
  header as well and prepare payload as following.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/login/",
```

### Header:

```header
header["X-CSRFToken"]=csrfvalue
```

### <span style="color: red;">Payload for Login:</span>

```json

{
  "payload": {
      "variables": {
          "email": "user.username",
          "password": "****"
      }
  }
}
```

### <span style="color: green;">Response for Login:</span>

```json
{
    "data": [{
        "refresh": ".....",
        "access": "......"
    }]
}
```

---

## Refresh Token API

- To get a efresh token, post data on url '/< prefix >/refresh/' .
- As the access token expires after given time, use refresh token to get
  new access token.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/refresh/",
```

### Header

```header
header["Content-Type"]="application/json"
```

### <span style="color: red;">Payload for Logout:</span>

```json
{
    "refresh":"..."
} 
```

### <span style="color: green;">Response for Logout:</span>

```json
{
    "access": "..."
}
```

---

## Register API

- To register a user, post the data on url '/< prefix >/register/'.
- As user sends registration request, a user activation link is sent to their
  email, as user clicks on
  that link user is activated.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/register/",
```

### <span style="color: red;">Payload for Register:</span>

```json
{
    "payload":{
        "variables":{
            "email":"user@example.com",
            "password":"123456",
            "password1":"123456"
        }
    }
}
```

### <span style="color: green;">Response for Register:</span>

```json
{
    "message": "Email sent successfully."
}
```

---

## Log Out

- To log out a user, post data on the url '/< url prefix >/logout/'.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/logout/",
```

### Header

```header
header["X-CSRFToken"]=csrfvalue
```

### <span style="color: green;">Response for Logout:</span>

```json
{
    "message": "Successfully logged out."
}
```

---

## Save data

- This api supports saving 1 to 10 records at once.
- To save data, post data on the url '/< url prefix >/save/' and set header as
  well prepare payload as following.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/save/",
```

### Header:

```bash
header["Content-Type"]="application/json"
header["X-CSRFToken"]=csrfvalue
header["Authorization"]="Bearer <access token>"
```

### <span style="color: red;">Payload for single record:</span>

```json
{
    "payload":{
        "variables":{
            "modelName":"Model name",
            "id": null,
            "saveInput":[{
                "field1": "value1",
                "field2": "value2",
                "field3": "value3",
                "field4": "value4",
                "field5": "value5",
                "field6": "value6",
                "field7": "value7",
                "field_fk_id": "fk value"
            }]
        }
    }
}

```

### <span style="color: green;">Response for single record:</span>

```json
{
    "data": [
        {
            "id": [
                1
            ]
        }
    ],
    "message": [
        "Record created successfully."
    ]
}
```

### <span style="color: red;">Payload for multiple record:</span>

```json
{
    "payload":{
        "variables":{
            "modelName":"Model name",
            "id": null,
            "saveInput":[{
                "field1": "value1",
                "field2": "value2",
                "field3": "value3",
                "field4": "value4",
                "field5": "value5",
                "field6": "value6",
                "field7": "value7",
                "field_fk_id": "fk value"
            },
            {
              "field1": "value1",
              "field2": "value2",
              "field3": "value3",
              "field4": "value4",
              "field5": "value5",
              "field6": "value6",
              "field7": "value7",
              "field_fk_name": "fk value"
            }
            ]
        }
    }
}

```

### <span style="color: green;">Response for multiple record:</span>

```json
{
    "data": [
        {
            "id": [
                1,
                2
            ]
        }
    ],
    "message": [
        "Record created successfully."
    ]
}
```

### Description for Fields

| Field Name      | Datatype           | Description                                         | Required | Default Value                                 | Example                                   |
|-----------------|--------------------|-----------------------------------------------------|----------|-----------------------------------------------|-------------------------------------------|
| modelName       | String             | Name of Django Model to Save                        | True     | "model name"                                  | Employees                                 |
| id              | None               | ID of the record to be updated                      | --       | null                                          | null                                      |
| SaveInput       | List( Dictionary ) | Contains list of fields and their values            | True     | [{ "field1": "value1","field2": "value2  " }] | [{ "field1": "emp_id","field2": "789 " }] |
| SaveInput.field | String             | Name of field in table in Database , ex:field1      | True     | "default_field"                               | "emp_id"                                  |
| SaveInput.value | Any                | Value of corresponding column in table , ex: value1 | True     | "default_value"                               | "789"                                     |

---

## Fetch data

- To fetch the data, post on the url '/< url prefix >/fetch/' and set
  header as well prepare payload as following.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/fetch/",
```

### Header:

```bash
header["Content-Type"]="application/json"
header["X-CSRFToken"]=csrfvalue
header["Authorization"]="Bearer <access token>"
```

### <span style="color: red;">Payload for Fetch Data:</span>

```json
{
  "payload": {
    "variables": {
      "modelName": "Model name",
      "fields": ["field1", "field2", "field3"],
      "filters": [
        {
          "operator": "eq / in / gt",
          "name": "field",
          "value": ["field-value"]  ,
          "operation": "or / and"
        }
      ],
      "pageNumber":1,
      "pageSize":10,
      "sort":
        {
        "field":"field1",
        "order_by":"asc/desc"
        }
    }
  }
}
```

### <span style="color: green;">Response for Fetch Data:</span>

```json
{
    "total": 1,
    "data": [
        {
            "field1": "abc",
            "field2": "def",
            "field3": "ghi"
        }
    ]
}
```

### Description of Fields

| Field Name    | Datatype   | Description                                                                                       | Required | Default Value                                              | Example                                              |
|---------------|------------|---------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------|------------------------------------------------------|
| modelName     | String     | Name of Django model to fetch                                                                     | True     | "model name"                                               | Employees                                            |
| fields        | List       | List of database field names, ex: field1,field2,                                                  | True     | ["field1","field2","field3 "]                              | ["name","age","emp_id"]                              |
| filters       | List[Dict] | Consists 3 filter properties (operator, name,value)                                               | True     | [{"operator": "in", "name": "field1","value": ["value1"]}] | [{ "operator": "eq","name": "age","value": ["25"] }] |
| operator      | Enum       | Specifies the comparison operation to be applied, Only considers one of ('eq', 'in', 'not', 'gt') | True     | "eq"                                                       | eq                                                   |
| name          | String     | Name of the field on which the filter is to be applied                                            | True     | "field1"                                                   | age                                                  |
| value         | List[Any]  | Values against which the field will be compared                                                   | True     | "value1"                                                   | ["25"]                                               |
| operation     | Enum       | Logical operation to chain filters. Options include 'and' or 'or'.                                | --       | "or"                                                       | or                                                   |
| pageNumber    | Int        | Page number for paginated results                                                                 | --       | 1                                                          | 4                                                    |  
| pageSize      | Int        | Number of records displayed in a page after pagination                                            | True     | 10                                                         | 10                                                   |
| Sort          | Dict       | Consists of 2 sort options (field, order_by)                                                      | True     | { "field":"field1","order_by":"asc" }                      | { "field":"id","order_by":"asc" }                    |
| Sort.Field    | String     | Field name by which the results should be sorted                                                  | True     | "field1"                                                   | id                                                   |
| Sort.order_by | Enum       | Sorting order ('asc' for ascending, 'desc' for descending)                                        | True     | "asc"                                                      | asc                                                  |

---

## Update data

- To update data, post data on the url '/< url prefix >/save/' and set
  header as well prepare payload as following.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/save/",
```

### Header:

```bash
header["Content-Type"]="application/json"
header["X-CSRFToken"]=csrfvalue
header["Authorization"]="Bearer <access token>"
```

### <span style="color: red;">Payload for Update Record:</span>

```json
{
    "payload":{
        "variables":{
            "modelName":"Model name",
            "id": "value" ,
            "saveInput":{
                "field1": "value1",
                "field2": "value2",
                "field3": "value3",
                "field4": "value4",
                "field5": "value5",
                "field6": "value6",
                "field7": "value7",
                "field_fk_id": "fk value"
            }
        }
    }
}

```

### <span style="color: green;">Response for Update Record:</span>

```json
{
    "data": [
        {
            "id": [
                1
            ]
        }
    ],
    "message": [
        "Record updated successfully."
    ]
}
```

### Description for Fields

| Field Name      | Datatype         | Description                                         | Required | Default Value                               | Example                                  |
|-----------------|------------------|-----------------------------------------------------|----------|---------------------------------------------|------------------------------------------|
| modelName       | String           | Name of Django Model to Save                        | True     | "model name"                                | Employees                                |
| id              | Int              | id value of record to update, ex: 1                 | True     | 1                                           | 5                                        |
| SaveInput       | List[Dictionary] | Contains list of fields and their values            | True     | [{ "field1": "field1","field2": "value1" }] | [{ "field1": "emp_id","field2": "963" }] |
| SaveInput.field | String           | Name of field in table in Database , ex:field1      | True     | "field1"                                    | emp_id                                   |
| SaveInput.value | Any              | Value of corresponding column in table , ex: value1 | True     | "value1"                                    | 963                                      |

---