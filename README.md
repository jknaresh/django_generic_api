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

### Configuation settings

- Users can customize the configurations.
- To customize as per your needs, create a config file named as "
  django_generic_api.ini".
- Place this file in same directory as your manage.py file within your Django
  project.

```bash
[REST_FRAMEWORK]

# Allowed request rate for authenticated users.
USER_RATE = int   # default value = 1000 
# Allowed request rate for anonymous user.
ANON_RATE = int   # default value = 30

[SAVE_SETTINGS]
# Number of records allowed to save at once.
CREATE_BATCH_SIZE = int   # default value = 10

[EMAIL_SETTINGS]
# Expiry time for email activation link (in hours).
EMAIL_ACTIVATION_LINK_EXPIRY_HOURS = int    # default value = 24
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

### Captcha Configuration

- Captcha validation can be optionally enabled for Login, Registration and Forgot Password APIs.

**Enabling Captcha Validation**
- To enable captcha validation, add this to settings.py .
```bash
CAPTCHA_REQUIRED = True  # Defaults to False
```
- If `CAPTCHA_REQUIRED` is set to True, both `captcha_key` and `captcha_value` must be included in the request payload for the Registration and Forgot Password APIs.
- If `CAPTCHA_REQUIRED` is set to False, these fields must not be provided.

**Configuring Captcha Settings**
- Include the `captcha` app in your `INSTALLED_APPS` list:

```bash
# Captcha Settings
INSTALLED_APPS = [
  "captcha",
]
```
- You can customize the captcha appearance and functionality using the following settings.
```bash
CAPTCHA_BACKGROUND_COLOR = hex code # Defaults to: '#ffffff'
CAPTCHA_FOREGROUND_COLOR = hex code # Defaults to: '#001100'
CAPTCHA_IMAGE_SIZE = tuple (width, height) # Defaults to: None
CAPTCHA_FONT_SIZE = int # Defaults to: 22
CAPTCHA_LENGTH = int # Defaults to: 4
```
**Customizing Captcha Content**
- To customize the content of captcha, add this settings.
- Chose any one of the following functions.
- If not used, defaults to upper case characters only.

```bash
CAPTCHA_CHALLENGE_FUNCT = 'django_generic_api.utils.random_digit_challenge'
# example: 9876
CAPTCHA_CHALLENGE_FUNCT = 'django_generic_api.utils.random_lowercase_challenge'
# example: abcd
CAPTCHA_CHALLENGE_FUNCT = 'django_generic_api.utils.random_uppercase_challenge'
# example: ABCD
CAPTCHA_CHALLENGE_FUNCT = 'django_generic_api.utils.mixed_digit_lowercase_challenge'
# example: a1b2
CAPTCHA_CHALLENGE_FUNCT = 'django_generic_api.utils.mixed_digit_uppercase_challenge'
# example: A1B2
```
- You can configure the content of captcha by [your own generator.](https://django-simple-captcha.readthedocs.io/en/latest/advanced.html#roll-your-own)
- After configuring the generator, simply point your `CAPTCHA_CHALLENGE_FUNCT` to the function.
```bash
CAPTCHA_CHALLENGE_FUNCT = '<your_path.to.generator>'
# example = 'django_app.utils.generator_function'
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
          "password": "****",
          "captcha_key": "<captcha_key>",  // If CAPTCHA_REQUIRED is set True in settings.py
          "captcha_value": "<captcha_value>"  // If CAPTCHA_REQUIRED is set True in settings.py
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

## Captcha API

- This API allows users to obtain a CAPTCHA image and its id for verification
  purposes.
- This API supports both GET and POST methods.
- To get a captcha, perform the request as

### Method:

```bash
HTTP Method: "GET" / "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/generate_captcha/",
```

### <span style="color: green;">Response for Captcha:</span>

```bash
{
    "captcha_key" : <captcha_key>,
    "captcha_url" : <image_url>
    # example for image url = "http://127.0.0.1:8050/api/captcha/image/c3efb9d994299a54312e2bb864f93c7aff600c4c/"
}
```

---

## Register API

- Send a request to Captcha API to get "captcha_key" and "captcha_url".
- The captcha_url is an image containing a value. Extract this value and send
  it as captcha_value in the register API.
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
            "password1":"123456",
            "captcha_key": "<captcha_key>", // If CAPTCHA_REQUIRED is set True in settings.py
            "captcha_value": "<captcha_value>" // If CAPTCHA_REQUIRED is set True in settings.py
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

| Field Name    | Datatype   | Description                                                                                                 | Required | Default Value                                              | Example                                              |
|---------------|------------|-------------------------------------------------------------------------------------------------------------|----------|------------------------------------------------------------|------------------------------------------------------|
| modelName     | String     | Name of Django model to fetch                                                                               | True     | "model name"                                               | Employees                                            |
| fields        | List       | List of database field names, ex: field1,field2,                                                            | True     | ["field1","field2","field3 "]                              | ["name","age","emp_id"]                              |
| filters       | List[Dict] | Consists 3 filter properties (operator, name,value)                                                         | True     | [{"operator": "in", "name": "field1","value": ["value1"]}] | [{ "operator": "eq","name": "age","value": ["25"] }] |
| operator      | Enum       | Specifies the comparison operation to be applied, Only considers one of ('eq', 'in', 'gt', 'like', 'ilike') | True     | "eq"                                                       | eq                                                   |
| name          | String     | Name of the field on which the filter is to be applied                                                      | True     | "field1"                                                   | age                                                  |
| value         | List[Any]  | Values against which the field will be compared                                                             | True     | "value1"                                                   | ["25"]                                               |
| operation     | Enum       | Logical operation to chain filters. Options include 'and' or 'or'.                                          | --       | "or"                                                       | or                                                   |
| pageNumber    | Int        | Page number for paginated results                                                                           | --       | 1                                                          | 4                                                    |  
| pageSize      | Int        | Number of records displayed in a page after pagination                                                      | True     | 10                                                         | 10                                                   |
| Sort          | Dict       | Consists of 2 sort options (field, order_by)                                                                | True     | { "field":"field1","order_by":"asc" }                      | { "field":"id","order_by":"asc" }                    |
| Sort.Field    | String     | Field name by which the results should be sorted                                                            | True     | "field1"                                                   | id                                                   |
| Sort.order_by | Enum       | Sorting order ('asc' for ascending, 'desc' for descending)                                                  | True     | "asc"                                                      | asc                                                  |

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

## Forgot Password API

- Send a request to Captcha API to get "captcha_key" and "captcha_url".
- The captcha_url is an image containing a value. Extract this value and send
  it as captcha_value in the forgot password API.
- This API enables users to initiate the password recovery process.
- When a user forgets their password, they can submit a request to receive a
  password reset link via email.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/forgotPassword/",
```

### <span style="color: red;">Payload for Forgot Password:</span>

```json
{
    "payload":{
        "variables":{
            "email":"user@example.com",
            "captcha_key": "<captcha_key>", // If CAPTCHA_REQUIRED is set True in settings.py
            "captcha_value": "<captcha_value>"  // If CAPTCHA_REQUIRED is set True in settings.py
        }
    }
}
```

### <span style="color: green;">Response for Forgot Password:</span>

```json
{
    "message": "Email sent successfully."
}
```

---

## New Password API

- This API enables users to reset their password securely.
- Users must first initiate the password reset process by sending a POST
  request to the Forgot Password API.
- A password reset link will be sent to their registered email address.
- Once the link is received, users can use it to update their password by
  making a POST request as outlined below.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/newpassword/<encoded_token>",
```

### <span style="color: red;">Payload for New Password:</span>

```json
{
    "payload":{
        "variables":{
            "password": "123456",
            "password1" : "123456"
        }
    }
}
```

### <span style="color: green;">Response for New Password:</span>

```json
{
    "message": "Your password has been reset."
}
```