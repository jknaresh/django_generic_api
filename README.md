# Django Generic API

A reusable Django app for generic CRUD operations based on dynamic payloads.
This package allows you to dynamically fetch and save data for any Django model
via a REST API.

## Features

- Dynamic fetch operation based on filters, fields, and models.
- Dynamic save operation (create or update records) for any Django model.
- Supports relationships and complex data.

## Installation

```bash
pip install django_generic_api
```

## Integration

### Django Installation

- Add 'django_generic_api' to INSTALLED_APPS in the settings.py file.

### URL settings

- Add the app url to urls.py file

```bash
path("<url prefix>", include('django_generic_api.urls'))
```

# Example APIs

## Save data

- To save data, post data on the url '/<prefix>/save/' and set header as well
  prepare payload as following

### Header:

```header
Key: Content-Type
Value: application/json
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

## Fetch data

- To fetch the data, post on the url '/<prefix>/fetch/' and set header as well
  prepare payload as following

### Header:

```bash
Key: Content-Type
Value: application/json
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
      ]
    }
  }
}
```

