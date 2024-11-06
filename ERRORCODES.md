# ERROR CODES

- In this project, error codes are defined to indicate the level at which an
  error is raised.
- The format of the error codes is as follows:

```bash
DGA-V: Errors raised at the views level (views.py)
DGA-S: Errors raised at the services level (services.py)
DGA-U: Errors raised at the utilities level (utils.py)
```

## Error code description table

| ERROR CODE | Action          | DESCRIPTION                                                                         |
|------------|-----------------|-------------------------------------------------------------------------------------|
| DGA-V001   | Save            | User Error! The user is trying to insert more than 10 records at once.              |
| DGA-V002   | Save            | User Error! The user payload does not match the predefined save payload.            |
| DGA-V003   | Save            | User Error! The user does not have permission to save or update data.               | 
| DGA-V004   | Fetch           | User Error! The user payload does not match the predefined fetch payload.           |
| DGA-V005   | Fetch           | User Error! The user does not have permission to fetch data.                        |
| DGA-V006   | Login           | User Error! The user payload does not match the predefined login payload.           |
| DGA-V007   | Login           | User Error! The username does not exist.                                            |
| DGA-V008   | Login           | User Error! The user has entered an incorrect password.                             |
| DGA-V009   | Login           | User Error! The user cannot generate token using AJAX.                              |
| DGA-V010   | Register        | User Error! The user payload does not match the predefined register payload.        |
| DGA-V011   | Register        | User Error! The confirm password does not match the password.                       |
| DGA-V012   | Register        | User Error! User is using a invalid email domain.                                   |
| DGA-V013   | Register        | User Error! The email already exists.                                               |
| DGA-V014   | Register        | Server Error! User activation failed.                                               |
| DGA-V015   | Forgot password | User Error! The user payload does not match the predefined forgot password payload. |
| DGA-V016   | User activate   | Server Error! The activation link has expired.                                      |
| DGA-V017   | User activate   | User Error! The user ID does not exist.                                             |
| DGA-V018   | User activate   | Server Error! The user is not activated.                                            |
| DGA-S001   | Get Model       | User Error ! The model does not exist.                                              |
| DGA-S002   | Access Token    | User Error! The user is not authenticated by session or does not have a token.      |
| DGA-S003   | Access Token    | User Error! The token format is invalid.                                            |                                                                                                                        |
| DGA-S004   | Access Token    | User Error! Access token authentication failed.                                     |
| DGA-S005   | Fetch Filter    | User Error! Invalid data in the fetch filter.                                       |
| DGA-S006   | Save(Update)    | User Error! The user is trying to update more than one record.                      |
| DGA-S007   | Save            | User Error! User is passing an extra field in saveInput.                            |
| DGA-S008   | Save            | User Error! The user's save input does not match the model field configuration.     |
| DGA-S009   | Save(Update)    | User Error! The ID does not exist.                                                  |
| DGA-S010   | Save(Update)    | User Error! The ID is invalid.                                                      |
| DGA-S009   | Save            | User Error! The user has included an extra field in saveInput.                      |
| DGA-U001   | Field search    | User Error! Field not found.                                                        |
| DGA-U002   | Field search    | User Error! The user has passed an extra field.                                     |
| DGA-U003   | Request Rate    | User Error! The user has exceeded the request rate.                                 |
 