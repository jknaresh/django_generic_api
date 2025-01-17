# Django Generic API

<!-- TOC -->

* [Django Generic API](#django-generic-api)
    * [Overview](#overview)
    * [Features](#features)
    * [Installation](#installation)
* [Integration](#integration)
    * [CORS Setup](#cors-setup)
    * [Token based authentication settings](#token-based-authentication-settings)
    * [Configuation settings](#configuation-settings)
    * [Email settings](#email-settings)
    * [Captcha Configuration](#captcha-configuration)
    * [URL Configuration](#url-configuration)
    * [Limiting User Requests](#limiting-user-requests)
* [Parameters for requests](#parameters-for-requests)
    * [Fetching and Saving Data](#fetching-and-saving-data)
* [Model APIs](#model-apis)
    * [Captcha API](#captcha-api)
        * [Method:](#method)
        * [URL construction:](#url-construction)
        * [<span style="color: green;">Success response for Captcha:</span>](#span-stylecolor-greensuccess-response-for-captchaspan)
        * [<span style="color: red;">Error response for Captcha:</span>](#span-stylecolor-rederror-response-for-captchaspan)
    * [Register API](#register-api)
        * [Method:](#method-1)
        * [URL construction:](#url-construction-1)
        * [<span style="color: orange;">Payload for Register:</span>](#span-stylecolor-orangepayload-for-registerspan)
        * [<span style="color: green;">Success response for Register:</span>](#span-stylecolor-greensuccess-response-for-registerspan)
        * [<span style="color: red;">Error response for Register:</span>](#span-stylecolor-rederror-response-for-registerspan)
    * [Account activation API](#account-activation-api)
        * [Method:](#method-2)
        * [URL construction:](#url-construction-2)
        * [<span style="color: green;">Success response for account activation:</span>](#span-stylecolor-greensuccess-response-for-account-activationspan)
        * [<span style="color: red;">Error response for account activation:</span>](#span-stylecolor-rederror-response-for-account-activationspan)
    * [Forgot Password API](#forgot-password-api)
        * [Method:](#method-3)
        * [URL construction:](#url-construction-3)
        * [<span style="color: orange;">Payload for Forgot Password:</span>](#span-stylecolor-orangepayload-for-forgot-passwordspan)
        * [<span style="color: green;">Success response for Forgot Password:</span>](#span-stylecolor-greensuccess-response-for-forgot-passwordspan)
        * [<span style="color: red;">Error response for Forgot Password:</span>](#span-stylecolor-rederror-response-for-forgot-passwordspan)
    * [New Password API](#new-password-api)
        * [Method:](#method-4)
        * [URL construction:](#url-construction-4)
        * [<span style="color: orange;">Payload for New Password:</span>](#span-stylecolor-orangepayload-for-new-passwordspan)
        * [<span style="color: green;">Success response for New Password:</span>](#span-stylecolor-greensuccess-response-for-new-passwordspan)
        * [<span style="color: red;">Error response for New Password:</span>](#span-stylecolor-rederror-response-for-new-passwordspan)
    * [Login API](#login-api)
        * [Method:](#method-5)
        * [URL construction:](#url-construction-5)
        * [Header:](#header)
        * [<span style="color: orange;">Payload for Login:</span>](#span-stylecolor-orangepayload-for-loginspan)
        * [<span style="color: green;">Success response for Login:</span>](#span-stylecolor-greensuccess-response-for-loginspan)
        * [<span style="color: red;">Error response for Login:</span>](#span-stylecolor-rederror-response-for-loginspan)
    * [Refresh Token API](#refresh-token-api)
        * [Method:](#method-6)
        * [URL construction:](#url-construction-6)
        * [Header](#header-1)
        * [<span style="color: orange;">Payload for Refresh:</span>](#span-stylecolor-orangepayload-for-refreshspan)
        * [<span style="color: green;">Success response for Refresh:</span>](#span-stylecolor-greensuccess-response-for-refreshspan)
    * [Fetch data](#fetch-data)
        * [Method:](#method-7)
        * [URL construction:](#url-construction-7)
        * [Header:](#header-2)
        * [<span style="color: orange;">Payload for Fetch Data:</span>](#span-stylecolor-orangepayload-for-fetch-dataspan)
        * [<span style="color: green;">Success response for Fetch Data:</span>](#span-stylecolor-greensuccess-response-for-fetch-dataspan)
        * [<span style="color: red;">Error response for Fetch Data:</span>](#span-stylecolor-rederror-response-for-fetch-dataspan)
        * [Description of Fields](#description-of-fields)
    * [Save data](#save-data)
        * [Method:](#method-8)
        * [URL construction:](#url-construction-8)
        * [Header:](#header-3)
        * [<span style="color: orange;">Payload for single record:</span>](#span-stylecolor-orangepayload-for-single-recordspan)
        * [<span style="color: green;">Success response for single record:</span>](#span-stylecolor-greensuccess-response-for-single-recordspan)
        * [<span style="color: red;">Error response for single record:</span>](#span-stylecolor-rederror-response-for-single-recordspan)
        * [<span style="color: orange;">Payload for multiple record:</span>](#span-stylecolor-orangepayload-for-multiple-recordspan)
        * [<span style="color: green;">Success response for multiple record:</span>](#span-stylecolor-greensuccess-response-for-multiple-recordspan)
        * [<span style="color: red;">Error response for multiple record:</span>](#span-stylecolor-rederror-response-for-multiple-recordspan)
        * [Description for Fields](#description-for-fields)
    * [Update data](#update-data)
        * [Method:](#method-9)
        * [URL construction:](#url-construction-9)
        * [Header:](#header-4)
        * [<span style="color: orange;">Payload for Update Record:</span>](#span-stylecolor-orangepayload-for-update-recordspan)
        * [<span style="color: green;">Success response for Update Record:</span>](#span-stylecolor-greensuccess-response-for-update-recordspan)
        * [<span style="color: red;">Error response for Update Record:</span>](#span-stylecolor-rederror-response-for-update-recordspan)
        * [Description for Fields](#description-for-fields-1)
    * [Fetch User Info API](#fetch-user-info-api)
        * [Method:](#method-10)
        * [URL construction:](#url-construction-10)
        * [Header:](#header-5)
        * [<span style="color: green;">Success response for User Info:</span>](#span-stylecolor-greensuccess-response-for-user-infospan)
        * [<span style="color: red;">Error response for User Info:</span>](#span-stylecolor-rederror-response-for-user-infospan)
    * [Update User Info API](#update-user-info-api)
        * [Method:](#method-11)
        * [URL construction:](#url-construction-11)
        * [Header:](#header-6)
        * [<span style="color: orange;">Payload for User Info Update:</span>](#span-stylecolor-orangepayload-for-user-info-updatespan)
        * [<span style="color: green;">Success response for User Info Update:</span>](#span-stylecolor-greensuccess-response-for-user-info-updatespan)
        * [<span style="color: red;">Error response for User Info Update:</span>](#span-stylecolor-rederror-response-for-user-info-updatespan)

<!-- TOC -->

## Overview

- Django Generic API is a reusable Django app designed to perform dynamic CRUD
  operations based on payloads.
- It provides a flexible way to handle database operations for any Django model
  through REST API endpoints.

## Features

- Perform dynamic fetch and save operations seamlessly.
- Handle dynamic save operations, including creating or updating records,
  excluding Django internal models.
- Integrated pagination and sorting features for efficient data handling.
- Comprehensive user authentication and management, including Login,
  Registration, Logout, and Forgot Password.
- Supports both session and token based authentication, supports custom
  authentication classes.
- Provides optional CAPTCHA validation for login, registration and Forgot
  Password.
- Includes APIs to retrieve user information.
- Features rate limiting to manage access for both authenticated and anonymous
  users.
- Versioning of URL, moving forward we will maintain versioning, as of now v1
  is alive version.

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
        
        # Supports custom / user-defined authentication classes as per DRF.
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

- Captcha validation can be optionally enabled for Login, Registration and
  Forgot Password APIs.

**Enabling Captcha Validation**

- To enable captcha validation, add this to settings.py .

```bash
CAPTCHA_REQUIRED = True  # Defaults to False
```

- If `CAPTCHA_REQUIRED` is set to True, both `captcha_key` and `captcha_value`
  must be included in the request payload for the Registration and Forgot
  Password APIs.
- If `CAPTCHA_REQUIRED` is set to False, these fields must not be provided.

**Configuring Captcha Settings**

- Include the `captcha` app in your `INSTALLED_APPS` list:

```bash
# Captcha Settings
INSTALLED_APPS = [
  "captcha",
]
```

- You can customize the captcha appearance and functionality using the
  following settings.

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

- You can configure the content of captcha
  by [your own generator.](https://django-simple-captcha.readthedocs.io/en/latest/advanced.html#roll-your-own)
- After configuring the generator, simply point your `CAPTCHA_CHALLENGE_FUNCT`
  to the function.

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

## Captcha API

- This API provides users with a CAPTCHA image and its associated ID for
  verification purposes.
- The CAPTCHA verification is optional and can be used with the Login,
  Registration, and Forgot Password APIs.
- To generate a CAPTCHA, send a POST request to the URL
  `/<prefix>/v1/captcha/`.
- To use the CAPTCHA in the mentioned APIs:
    - Include the CAPTCHA ID as `captcha_key` in the API payload.
    - Include the CAPTCHA value as `captcha_value`, extracted from the CAPTCHA
      image URL.
- This service is optional. To disable CAPTCHA verification, set the
  `CAPTCHA_REQUIRED`
  variable to `False` in the settings.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/generate-captcha/",
```

### <span style="color: green;">Success response for Captcha:</span>

```bash
# HTTP STATUS CODE = 200
{
    "data": {
        "captcha_key": <captcha_key>,
        "captcha_url": <image_url>
    },
    "message": "Captcha Generated."
}
```

### <span style="color: red;">Error response for Captcha:</span>

```bash
# HTTP STATUS CODE = 400
{
    "error": <errro_message>,
    "code": <error_code>
}
```

---

## Register API

- To register a user, submit the data to the URL `/<prefix>/v1/register/`.
- When a user sends a registration request, an activation link is sent to their
  email.
- Once the user clicks the activation link, their account is activated.
- For security purposes, this API includes an optional CAPTCHA service.
- To disable CAPTCHA, set `CAPTCHA_REQUIRED` to `False` in the settings.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/register/",
```

### <span style="color: orange;">Payload for Register:</span>

```bash
{
    "payload":{
        "variables":{
            "email":"user@example.com",
            "password":"123456",
            "password1":"123456",
            "captcha_key": "<captcha_key>", # If CAPTCHA_REQUIRED is set True in settings.py
            "captcha_value": "<captcha_value>" # If CAPTCHA_REQUIRED is set True in settings.py
        }
    }
}
```

### <span style="color: green;">Success response for Register:</span>

```bash
# HTTP STATUS CODE = 200
{ 
    "data": "Registration initiated.",
    "message": "Email sent successfully."
}
```

### <span style="color: red;">Error response for Register:</span>

```bash
# HTTP STATUS CODE = 400
{
    "error": "passwords does not match",
    "code": "DGA-V018"
}
```

---

## Account Activation API

- After completing the registration, the user receives an activation link via
  email.
- To activate the account, the user must click on the link, which will finalize
  the activation process.

### Method:

```bash
HTTP METHOD: "GET"
```

### URL construction:

```bash
url : "<BASE_URL>/api/activate/<encoded_token>/"
```

### <span style="color: green;">Success response for account activation:</span>

```bash
# HTTP STATUS CODE = 201
{
    "data": "Registration completed.",
    "message": "Your account has been activated successfully."
}
```

### <span style="color: red;">Error response for account activation:</span>

```bash
# HTTP STATUS CODE = 400
{
    "error": "<error_message>", 
    "code": "<error_code>"
}
```

---

## Forgot Password API

- This API allows users to initiate the password recovery process.
- If a user forgets their password, they can submit a request to receive a
  password reset link via email.
- For security purposes, an optional CAPTCHA verification is included.
- To disable CAPTCHA, set `CAPTCHA_REQUIRED` to `False` in the settings.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/forgotPassword/",
```

### <span style="color: orange;">Payload for Forgot Password:</span>

```bash
{
    "payload":{
        "variables":{
            "email":"user@example.com",
            "captcha_key": "<captcha_key>", # If CAPTCHA_REQUIRED is set True in settings.py
            "captcha_value": "<captcha_value>"  # If CAPTCHA_REQUIRED is set True in settings.py
        }
    }
}
```

### <span style="color: green;">Success response for Forgot Password:</span>

```bash
# HTTP STATUS CODE = 200
{
    "data": "Password reset initiated.",
    "message": "Email sent successfully."
}
```

### <span style="color: red;">Error response for Forgot Password:</span>

```bash
# HTTP STATUS CODE = 400
{
    "error": "User not found",
    "code": "DGA-V026"
}
```

---

## New Password API

- This API allows users to securely reset their password.
- To begin the process, users must initiate a password reset request through
  the Forgot Password API.
- A password reset link will be sent to the user's registered email address.
- After receiving the link, users can update their password by sending a POST
  request as detailed below.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/newpassword/<encoded_token>",
```

### <span style="color: orange;">Payload for New Password:</span>

```bash
{
    "payload":{
        "variables":{
            "password": "123456",
            "password1" : "123456"
        }
    }
}
```

### <span style="color: green;">Success response for New Password:</span>

```bash
# HTTP STATUS CODE = 200
{
    "data": "Password reset success",
    "message": "Your password has been reset."
}
```

### <span style="color: red;">Error response for New Password:</span>

```bash
# HTTP STATUS CODE = 400
{
    "error": <error_message>,
    "code": <error_code>
}
```

---

## Login API

- This API generates a pair of access and refresh tokens for user
  authentication.
- To log in, send a POST request to the URL `/ <prefix> /v1/login/`.
- For enhanced security, optional CAPTCHA verification is included.
- To disable CAPTCHA, set `CAPTCHA_REQUIRED` to `False` in the settings.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/login/",
```

### Header:

```header
header["X-CSRFToken"]=csrfvalue
```

### <span style="color: orange;">Payload for Login:</span>

```bash

{
  "payload": {
      "variables": {
          "email": "user.username",
          "password": "****",
          "captcha_key": "<captcha_key>", // If CAPTCHA_REQUIRED is set True in settings.py
          "captcha_value": "<captcha_value>" // If CAPTCHA_REQUIRED is set True in settings.py
      }
  }
}
```

### <span style="color: green;">Success response for Login:</span>

```bash
# HTTP STATUS CODE = 200 OK
{
    "data": [
        {
            "refresh": <refresh_token> 
            "access":  <access_token>
        }
    ],
    "message": "Tokens are generated."
}
```

### <span style="color: red;">Error response for Login:</span>

```bash
# HTTP STATUS CODE = 400 / 401/ 404
{
    "error": <error message>,
    "code": <error code>
}
```

---

## Refresh Token API

- To obtain a new access token, send a POST request to the URL
  `/ <prefix> /v1/refresh/`.
- As the access token expires after a certain time, use the refresh token to
  get a new access token.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/refresh/",
```

### Header

```header
header["Content-Type"]="application/json"
```

### <span style="color: orange;">Payload for Refresh:</span>

```bash
{
    "refresh":"..."
} 
```

### <span style="color: green;">Success response for Refresh:</span>

```bash
# HTTP STATUS CODE = 200
{
    "access": "..."
}
```

---

## Fetch data

- To fetch the data, post on the url '/< url prefix >/v1/fetch/' and set
  header as well prepare payload as following.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/fetch/",
```

### Header:

```bash
header["Content-Type"]="application/json"
header["Authorization"]="Bearer <access token>"
```

### <span style="color: orange;">Payload for Fetch Data:</span>

```bash
{
  "payload": {
    "variables": {
      "modelName": "Model name",
      "fields": ["field1", "field2", "field3"],
      "filters": [
        {
          "operator": "eq / in / gt / like / ilike",
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

### <span style="color: green;">Success response for Fetch Data:</span>

```bash
{
    "data": {
        "total": 10,
        "data": [
            {
                "field1": "abc",
                "field1": "def",
                "field3": "ghi"
            },
            .
            .
            .
            .
        ]
    },
    "message": "Completed."
}
```

### <span style="color: red;">Error response for Fetch Data:</span>

```bash
{
    "error":<error_message>,
    "code": <error_code>
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

## Save Data API

- This API supports saving records, from 1 up to a customizable limit.
- The maximum number of records is defined by the `CREATE_BATCH_SIZE` setting.
- By default, `CREATE_BATCH_SIZE` is set to 10 if not specified.
- To customize, set `CREATE_BATCH_SIZE` in the `django-generic-api.ini` file in
  the `manage.py` directory:
  ```
  [SAVE_SETTINGS]
  CREATE_BATCH_SIZE = 10
  ```
- Send a POST request to `/ <url prefix> /v1/save/` with the appropriate
  headers.
- Prepare the payload as required.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/save/",
```

### Header:

```bash
header["Content-Type"]="application/json"
header["Authorization"]="Bearer <access token>"
```

### <span style="color: orange;">Payload for single record:</span>

```bash
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

### <span style="color: green;">Success response for single record:</span>

```bash
# HTTP SUCCESS CODE = 200
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

### <span style="color: red;">Error response for single record:</span>

```bash
# HTTP SUCCESS CODE = 400
{
    "error": <error_message>,
    "code": <error_code>
}
```

### <span style="color: orange;">Payload for multiple record:</span>

```bash
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

### <span style="color: green;">Success response for multiple record:</span>

```bash
# HTTP SUCCESS CODE = 200
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

### <span style="color: red;">Error response for multiple record:</span>

```bash
# HTTP SUCCESS CODE = 400
{
    "error": <error_message>,
    "code": <error_code>
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

---

## Update data

- To update data, post data on the url '/< url prefix >v1/save/' and set
  header as well prepare payload as following.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/save/",
```

### Header:

```bash
header["Content-Type"]="application/json"
header["Authorization"]="Bearer <access token>"
```

### <span style="color: orange;">Payload for Update Record:</span>

```bash
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

### <span style="color: green;">Success response for Update Record:</span>

```bash
# HTTP STATUS CODE = 201
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

### <span style="color: red;">Error response for Update Record:</span>

```bash
# HTTP STATUS CODE = 400
{
    "error": <error_message>,
    "code": <error_code>
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

## Fetch User Info API

- Fetch or update fields in the `auth_user` table defined by the system.
- Use the `USER_INFO_FIELDS` setting to define a tuple of database table
  fields.
- Authentication is required.

```bash
# ex: USER_INFO_FIELDS = (first_name, last_name)
```

- The listed attributes are fetched.

### Method:

```bash
HTTP Method: "POST"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/user-info/"
```

### Header:

```bash
header["Content-Type"]="application/json"
header["Authorization"]="Bearer <access token>"
```

### <span style="color: green;">Success response for User Info:</span>

```bash
# HTTP STATUS CODE = 200
{
    "data": [
        {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
    ]
}
```

### <span style="color: red;">Error response for User Info:</span>

```bash
# HTTP STATUS CODE = 400
{
    "error": <error_message>,
    "code": <error_code>
}
```

---

## Update User Info API

- Fetch or update fields in the `auth_user` table defined by the system.
- Use the `USER_INFO_FIELDS` setting to define a tuple of database table
  fields.
- Authentication is required.

```bash
# Example: USER_INFO_FIELDS = ('first_name', 'last_name')
```

- Only the listed attributes can be updated.

### Method:

```bash
HTTP Method: "PUT"
```

### URL construction:

```bash
url: "http://domain-name/api/v1/user-info/"
```

### Header:

```bash
header["Content-Type"]="application/json"
header["Authorization"]="Bearer <access token>"
```

### <span style="color: orange;">Payload for User Info Update:</span>

```bash
{
    "payload":{
        "variables":{
            "saveInput":[{
                "field1": "value1",
                "field2": "value2"
            }]
        }
    }
}

```

### <span style="color: green;">Success response for User Info Update:</span>

```bash
# HTTP STATUS CODE = 200
{
    "data": [
        {
            "id": <user.id>
        }
    ],
    "message": "<user.username>'s info is updated"
}
```

### <span style="color: red;">Error response for User Info Update:</span>

```bash
# HTTP STATUS CODE = 400
{
    "error": <error_message>,
    "code": <error_code>
}
```

---