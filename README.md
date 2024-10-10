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

## Adding CORS headers allows your resources to be accessed on other domains
## This allows in-browser requests to your Django application from other origins.

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

# cross origin middleware settings,add middleware class to listen in on responses:
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
          ...
]

# Rest framework settings

## Session authentication is for on form based submission
## Non Session authentication is for token based submission

#add the settings as per your requirement 
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        #This is for form submission based authentication
        "rest_framework.authentication.SessionAuthentication",
        #This is for Token based authentication
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

from datetime import timedelta
#customize your token validity time
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
          "username": "name",
          "password": "****"
      }
  }
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
header["X-CSRFToken"]=csrfvalue
```

## Save data

- This api supports saving multiple(upto 10) records at once.
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
              "field_fk_id": "fk value"
            }
            ]
        }
    }
}

```


### Description for Fields

| Field Name | Datatype     | Description                                         | Required / Optional |
|------------|--------------|-----------------------------------------------------|---------------------|
| modelName  | String       | Name of Django Model to Save                        | Required            |
| id         | String / Int | ID of the record to be updated                      | Optional            |
| SaveInput  | Dictionary   | Contains list of fields and their values            | Required            |
| field      | String       | Name of field in table in Database , ex:field1      | Required            |
| value      | Any          | Value of corresponding column in table , ex: value1 | Required            |

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

| Field Name | Datatype | Description                                                                    | Required / Optional |
|------------|----------|--------------------------------------------------------------------------------|---------------------|
| modelName  | String   | Name of Django model to fetch                                                  | Required            |
| fields     | List     | List of database field names, ex: field1, field2, field3                       | Required            |
| filters    | List     | Consists 3 filter objects (operator, name, value)                              | Optional            |
| operator   | Enum     | Specifies the comparison operation to be applied, Only considers 'eq' and 'in' | Required            |
| name       | String   | Name of Database field to perform fetch from                                   | Required            |
| value      | Any      | Value of field to perform fetch                                                | Required            |
| pageNumber | Int      | Page number of filtered data after pagination is applied                       | Optional            |  
| pageSize   | Int      | Number of records displayed in a page after pagination                         | Optional            |
| Sort       | Dict     | Consists of 2 sort options (field, order_by)                                   | Optional            |
| Field      | String   | Name of filter to orderby                                                      | Required            |
| order_by   | Enum     | Specifies order_by options ( asc: Ascending order, desc: Descending order)     | Required            |

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

### Description for Fields

| Field Name | Datatype   | Description                                         | Required / Optional |
|------------|------------|-----------------------------------------------------|---------------------|
| modelName  | String     | Name of Django Model to Save                        | Required            |
| id         | Int        | id value of record to update, ex: 1                 | Required            |
| SaveInput  | Dictionary | Contains list of fields and their values            | Required            |
| field      | String     | Name of field in table in Database , ex:field1      | Required            |
| value      | Any        | Value of corresponding column in table , ex: value1 | Required            |