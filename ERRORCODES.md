# ERROR CODES

- In this project, error codes are defined to indicate the level at which an error is raised. 
- The format of the error codes is as follows:

```bash
DGA-V: Errors raised at the views level (views.py)
DGA-S: Errors raised at the services level (services.py)
DGA-U: Errors raised at the utilities level (utils.py)
```
## Error code description table 

| ERROR CODE | Action          | MEANING                                                                       | FileName |
|------------|-----------------|-------------------------------------------------------------------------------|----------|
| DGA-V001   | Save            | The user is trying to insert more than 10 records at once.                    |          |
| DGA-V002   | Save            | The user payload and predefined save payload do not match.                    |          |
| DGA-V003   | Save            | The user is trying to insert data into a non-existing model or table.         |          |
| DGA-V004   | Save            | The user does not have permission to save or update data.                     |          |
| DGA-V005   | Save            | The user is providing invalid data to save or update.                         |          |
| DGA-V006   | Fetch           | The user payload and predefined fetch payload do not match.                   |          |
| DGA-V007   | Fetch           | The user is trying to fetch data from a non-existing table or model.          |          |
| DGA-V008   | Fetch           | The user does not have permission to fetch data.                              |          |
| DGA-V009   | Fetch           | The user is providing invalid data to fetch.                                  |          |
| DGA-V010   | Login           | The user payload and predefined login payload do not match.                   |          |
| DGA-V011   | Login           | The username does not exist.                                                  |          |
| DGA-V012   | Login           | The user has entered an incorrect password.                                   |          |
| DGA-V013   | Register        | The user payload and predefined register payload do not match.                |          |
| DGA-V014   | Register        | The confirm password does not match the password.                             |          |
| DGA-V015   | Register        | The email already exists.                                                     |          |
| DGA-V016   | Register        | Error! User activation failed.                                                |          |
| DGA-V017   | Forgot password | The user payload and predefined forgot password payload do not match.         |          |
| DGA-V018   | User activate   | The activation link has expired.                                              |          |
| DGA-V019   | User activate   | The user ID does not exist.                                                   |          |
| DGA-V020   | User activate   | Error! User is not activated.                                                 |          |
| DGA-S001   | Access Token    | The user is not logged in by session and does not have an access token.       |          |
| DGA-S002   | Access Token    | The token format is invalid.                                                  |          |                                                                                                                        |
| DGA-S003   | Access Token    | Access token authentication failed.                                           |          |
| DGA-S004   | Fetch Filter    | Invalid data in fetch filter.                                                 |          |
| DGA-S005   | Save(Update)    | The user is trying to update more than one record.                            |          |
| DGA-S006   | Save            | The user's save input does not match the table or model fields configuration. |          |
| DGA-S007   | Save(Update)    | The ID does not exist.                                                        |          |
| DGA-S008   | Save(Update)    | The ID is invalid.                                                            |          |
| DGA-U001   | Field search    | Field not found.                                                              |          |
