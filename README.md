# Django Generic API

A reusable Django app for generic CRUD operations based on dynamic payloads.
This package allows you to dynamically fetch and save data for any Django model
via a REST API.

## Features

- Dynamic fetch operation based on filters, fields, and models.
- Dynamic save operation (create or update records) for any Django model.
- Supports relationships and complex data.
- Enabled with pagination and order by features.
- Includes Login, Registration, Logout , Forgot Password for user.

## Installation

```bash
pip install django_generic_api
```

## Integration

### Django Installation

- In settings.py file, integrate the following

```bash
# Set allowed hosts to all cross origin references
ALLOWED_HOSTS = ["*"]

# Adding CORS headers allows your resources to be accessed on other domains
# This allows in-browser requests to your Django application from other origins.

# A list of origins that are authorized to make cross-site HTTP requests.
CORS_ALLOWED_ORIGINS = ["*"]  # ex: "https://example.com","http://localhost:8080"

# If True, all origins will be allowed.
CORS_ALLOW_ALL_ORIGINS = True

# Additional apps to be added in your INSTALLED_APPS
INSTALLED_APPS =[
      ...
  "django_generic_api", # Package
  "rest_framework", # API framework package
  "rest_framework_simplejwt", # Token based authorization package
  "corsheaders", # CORS package
] 

# Cross origin middleware settings,add middleware class to listen in on responses:
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
          ...
]

# Rest framework settings

# Session authentication is for on form based submission
# Non Session authentication is for token based submission

# Add the settings as per your requirement 
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        #This is for form submission based authentication
        "rest_framework.authentication.SessionAuthentication",
        #This is for Token based authentication
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

from datetime import timedelta
# Customize your token validity time
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=5),
}

```

---

### URL Integrations

- Include the "django_generic_api" URLConfig in your project urls.py like this:
- 
```bash
path("<url prefix>", include('django_generic_api.urls'))
```

---

# Model APIs

## Access Token API

- To log a user in , post data on url '/< prefix >/login/' and set the
  header as well and prepare payload as following

### Header:

```header
header["X-CSRFToken"]=csrfvalue
```

### Login Payload:

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

### Response:

```json
{
    "data": {
        "refresh": ".....",
        "access": "......"
    }
}
```
---

## Log Out

- To log out a user, post data on the url '/< url prefix >/logout/' and set
  the header as

### Header

```header
header["X-CSRFToken"]=csrfvalue
```

### Response:

```json
{
    "message": "Successfully logged out."
}
```
---

## Save data

- This api supports saving 1 to 10 records at once.
- To save data, post data on the url '/< url prefix >/save/' and set header as
  well prepare payload as following

### Header:

```header
header["Content-Type"]=application/json,
header["X-CSRFToken"]=csrfvalue,
header["Authorization"]=Bearer <access token>
```

### Payload for single record:

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
### Response for single payload :

```json
{
    "data": [
        {
            "id": [
                {
                    "id": id
                }
            ]
        }
    ],
    "message": [
        "Record created successfully."
    ]
}
```

### Payload for multiple records:

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
### Response for multiple payload :

```json
{
    "data": [
        {
            "id": [
                {
                    "id": id
                },
                {
                    "id": id
                },
                ...
            ]
        }
    ],
    "message": [
        "Record created successfully."
    ]
}
```


### Description for Fields

| Field Name | Datatype           | Description                                         | Example                                   | Required |
|------------|--------------------|-----------------------------------------------------|-------------------------------------------|----------|
| modelName  | String             | Name of Django Model to Save                        | Employees                                 | True     |
| id         | String / Int       | ID of the record to be updated                      | null                                      | --       |
| SaveInput  | List( Dictionary ) | Contains list of fields and their values            | [{ "field1": "emp_id","field2": "789 " }] | True     |
| field      | String             | Name of field in table in Database , ex:field1      | "emp_id"                                  | True     |
| value      | Any                | Value of corresponding column in table , ex: value1 | "789"                                     | True     |

---
## Fetch data

- To fetch the data, post on the url '/< url prefix >/fetch/' and set
  header as well prepare payload as following

### Header:

```bash
header["Content-Type"]=application/json,
header["X-CSRFToken"]=csrfvalue,
header["Authorization"]=Bearer <access token>
```

### Payload:

```json
{
  "payload": {
    "variables": {
      "modelName": "Model name",
      "fields": ["field1", "field2", "field3"],
      "filters": [
        {
          "operator": "eq / in / not / gt",
          "name": "field",
          "value": ["field-value"]  
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
### Response for fetch payload :

```json
{
    "total": 1,
    "data": [
        {
            "id": id,
            "field1": "abc",
            "field2": "def",
            "field3": "ghi",
            
        }
    ]
}
```

### Description of Fields

| Field Name | Datatype | Description                                                                                       | Example                                             | Required |
|------------|----------|---------------------------------------------------------------------------------------------------|-----------------------------------------------------|----------|
| modelName  | String   | Name of Django model to fetch                                                                     | Employees                                           | True     |
| fields     | List     | List of database field names, ex: field1, field2,                                                 | ["name","age","emp_id"]                             | True     |
| filters    | List     | Consists 3 filter objects (operator, name, value)                                                 | [{ "operator": "eq","name": "age","value": ["25"] }]| --       |
| operator   | Enum     | Specifies the comparison operation to be applied, Only considers one of ('eq', 'in', 'not', 'gt') | eq                                                  | True     |
| name       | String   | Name of Database field to perform fetch from                                                      | age                                                 | True     |
| value      | Any      | Value of field to perform fetch                                                                   | ["25"]                                              | True     |
| pageNumber | Int      | Page number of filtered data after pagination is applied                                          | 4                                                   | --       |  
| pageSize   | Int      | Number of records displayed in a page after pagination                                            | 10                                                  | True     |
| Sort       | Dict     | Consists of 2 sort options (field, order_by)                                                      | { "field":"id","order_by":"asc" }                   | True     |
| Field      | String   | Name of filter to orderby                                                                         | id                                                  | True     |
| order_by   | Enum     | Specifies order_by options ( asc: Ascending order, desc: Descending order)                        | asc                                                 | True     |

---
## Update data

- To update data, post data on the url '/< url prefix >/save/' and set
  header as well prepare payload as following

### Header:

```header
Key 1 : Content-Type
Value 1 : application/json,
Key 2 : Authorization
Value 2 : Bearer <access token>
```

### Payload:

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
### Response for update payload :

```json
{
    "data": [
        {
            "id": [
                {
                    "id": id
                }
            ]
        }
    ],
    "message": [
        "Record updated successfully."
    ]
}
```

### Description for Fields

| Field Name | Datatype   | Description                                         | Example                                 | Required |
|------------|------------|-----------------------------------------------------|-----------------------------------------|----------|
| modelName  | String     | Name of Django Model to Save                        | Employees                               | True     |
| id         | Int        | id value of record to update, ex: 1                 | 5                                       | True     |
| SaveInput  | Dictionary | Contains list of fields and their values            | [{ "field1": "emp_id","field2": "963" }]| True     |
| field      | String     | Name of field in table in Database , ex:field1      | emp_id                                  | True     |
| value      | Any        | Value of corresponding column in table , ex: value1 | 963                                     | True     |
---