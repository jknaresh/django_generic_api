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

- In settings.py file, add the following

```bash
from datetime import timedelta

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        #This is for form submission based authentication
        "rest_framework.authentication.SessionAuthentication",
        #This is for Token based authentication
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=5),
}

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS =[
      ...
  "django_generic_api",
  "rest_framework",
  "rest_framework_simplejwt",
  "corsheaders",
] 

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
          ...
]

CORS_ALLOWED_ORIGINS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True
```

---

### URL settings

- Add the app url to urls.py file

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
Header["X-CSRFToken"]=csrfvalue
```

### Payload:

```json
{
  "username": "name",
  "password": "****"
}
```

### Response:

```json
{
    "token": {
        "refresh": ".....",
        "access": "......"
    }
}
```

## Log Out

- To log out a user, post data on the url '/< url prefix >/logout/' and set
  the header as

### Header

```header
Key 1 : X-CSRFToken
Value 1 : csrf token value
```

## Save data

- To save data, post data on the url '/< url prefix >/save/' and set header as
  well prepare payload as following

### Header:

```header
Key 1 : Content-Type
Value 1 : application/json,
Key 2 : Authorization
Value 2 : Bearer <access token>
```

### Body:

```json
{
    "payload":{
        "variables":{
            "modelName":"Model name",
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

### Description for Fields

| Field Name | Datatype   | Description                                         |
|------------|------------|-----------------------------------------------------|
| modelName  | String     | Name of Django Model to Save                        |
| SaveInput  | Dictionary | Contains list of fields and their values            |
| field      | String     | Name of field in table in Database , ex:field1      |
| value      | Any        | Value of corresponding column in table , ex: value1 |

## Fetch data

- To fetch the data, post on the url '/< url prefix >/fetch/' and set
  header as well prepare payload as following

### Header:

```bash
Key 1 : Content-Type
Value 1 : application/json,
Key 2 : Authorization
Value 2 : Bearer <access token>
```

### Body:

```json
{
  "payload": {
    "variables": {
      "modelName": "Model name",
      "fields": ["field1", "field2", "field3"],
      "filters": [
        {
          "operator": "eq / in",
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

### Description of Fields

| Field Name | Datatype | Description                                                                    |
|------------|----------|--------------------------------------------------------------------------------|
| modelName  | String   | Name of Django model to fetch                                                  |
| fields     | List     | List of database field names, ex: field1, field2, field3                       |
| filters    | List     | Consists 3 filter objects (operator, name, value)                              |
| operator   | Enum     | Specifies the comparison operation to be applied, Only considers 'eq' and 'in' |
| name       | String   | Name of Database field to perform fetch from                                   |
| value      | Any      | Value of field to perform fetch                                                |
| pageNumber | Int      | Page number of filtered data after pagination is applied                       |  
| pageSize   | Int      | Number of records displayed in a page after pagination                         |
| Sort       | Dict     | Consists of 2 sort options (field, order_by)                                   |
| Field      | String   | Name of filter to orderby                                                      |
| order_by   | Enum     | Specifies order_by options ( asc: Ascending order, desc: Descending order)     |

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

### Body:

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

### Description for Fields

| Field Name | Datatype   | Description                                         |
|------------|------------|-----------------------------------------------------|
| modelName  | String     | Name of Django Model to Save                        |
| id         | Int        | id value of record to update, ex: 1                 |
| SaveInput  | Dictionary | Contains list of fields and their values            |
| field      | String     | Name of field in table in Database , ex:field1      |
| value      | Any        | Value of corresponding column in table , ex: value1 |