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

| ERROR CODE | Action              | DESCRIPTION                                                                               |
|------------|---------------------|-------------------------------------------------------------------------------------------|
| DGA-V001   | Save                | User Error! Too many records attempted to save at once.                                   |
| DGA-V002   | Save                | User Error! The user payload and predefined save payload do not match.                    |
| DGA-V004   | Save                | User Error! The user does not have permission to save or update data.                     |
| DGA-V005   | Fetch               | User Error! The user payload and predefined fetch payload do not match.                   |
| DGA-V007   | Fetch               | User Error! The user does not have permission to fetch data.                              |
| DGA-V008   | Login               | User Error! The user payload and predefined login payload do not match.                   |
| DGA-V009   | Login               | User Error! The user has entered invalid captcha value.                                   |
| DGA-V010   | Login               | User Error! The user has set invalid captcha key.                                         |
| DGA-V011   | Login               | User Error! The username does not exist.                                                  |
| DGA-V012   | Login               | User Error! The user has entered an incorrect password.                                   |
| DGA-V013   | Login               | User Error! The user is generating a token while with session management.                 |
| DGA-V014   | Register            | User Error! The user payload and predefined register payload do not match.                |
| DGA-V015   | Register            | User Error! The user has entered invalid captcha value.                                   |
| DGA-V016   | Register            | User Error! The user has set invalid captcha key.                                         |
| DGA-V017   | Register            | User Error! The email already exists.                                                     |
| DGA-V018   | Register            | User Error! The user has entered two different passwords for registration.                |
| DGA-V019   | Register            | User Error! The user entered passwords are too weak to be validated.                      |
| DGA-V020   | Register            | User Error! The user has entered a invalid domain name.                                   |
| DGA-V021   | Register            | User Error! The user has not set a `BASE_URL` for registration.                           |
| DGA-V022   | Register            | Server Error! User activation failed.                                                     |
| DGA-V023   | Forgot password     | User Error! The user payload and predefined forgot password payload do not match.         |
| DGA-V024   | Forgot password     | User Error! The user has entered a invalid captcha value.                                 |
| DGA-V025   | Forgot password     | User Error! The user has set a invalid captcha key.                                       |
| DGA-V026   | Forgot password     | User Error! The user with given username does not exist.                                  |
| DGA-V027   | Forgot password     | Server Error! Password reset failed.                                                      |
| DGA-V028   | User activate       | Server Error! The activation link has expired.                                            |
| DGA-V029   | User activate       | User Error! The user ID does not exist.                                                   |
| DGA-V030   | User activate       | Server Error! User is not activated.                                                      |
| DGA-V031   | Captcha service     | Server Error! Error while generating captcha.                                             |
| DGA-V032   | Password reset      | User Error! The encoded token is invalid.                                                 |
| DGA-V033   | Password reset      | User Error! The password reset link has expired.                                          |
| DGA-V034   | Password reset      | User Error! The password reset payload and predefined payload do not match.               |
| DGA-V035   | Password reset      | User Error! The user has entered two different passwords for forgot password.             |
| DGA-V036   | Password reset      | User Error! The user entered passwords are too weak to be validated.                      |
| DGA-V037   | User Info           | User Error! The user is not authenticated.                                                |
| DGA-V038   | User Info update    | User Error! The user is not authenticated.                                                |
| DGA-V039   | User Info update    | User Error! The user info update payload and predefined payload do not match.             |
| DGA-V040   | Password reset      | User Error! The user ID does not exist.                                                   |
| DGA-V041   | Password reset      | User Error! Error occurred while resetting the password.                                  |
| DGA-V042   | 1-1 Fetch           | User Error! The 1-1 fetch payload and predefined payload do not match.                    |
| DGA-V043   | 1-1 Fetch           | User Error! The user is not authenticated.                                                |
| DGA-V044   | 1-1 Save            | User Error! The user is not authenticated.                                                |
| DGA-V045   | 1-1 Save            | User Error! The user is sending multiple records in payload.                              |
| DGA-V046   | 1-1 Save            | User Error! The 1-1 Save payload and user payload does not match.                         |
| DGA-S001   | Pydantic model      | User Error! The field type mapping is not found.                                          |
| DGA-S002   | Fetch Filter        | User Error! Invalid data in fetch filter.                                                 |
| DGA-S003   | Save(Update)        | User Error! The user is trying to update more than one record.                            |
| DGA-S004   | Save                | User Error! The user's save input does not match the table or model fields configuration. |
| DGA-S005   | Save                | User Error! The value if not suitable for the field.                                      |
| DGA-S006   | Save(update)        | User Error! The ID does not exist.                                                        |
| DGA-S007   | Save(Update)        | User Error! The ID is invalid.                                                            |
| DGA-S008   | User info update    | User Error! `USER_INFO_FIELDS` is not configured in settings.                             |
| DGA-S009   | User info update    | User Error! The user's save input does not match the table or model fields configuration. |
| DGA-S010   | User info update    | User Error! The value if not suitable for field.                                          |
| DGA-S011   | User info fetch     | User Error! `USER_INFO_FIELDS` is not configured in settings.                             |
| DGA-S012   | Get model by name   | User Error! The model does not exist.                                                     |
| DGA-S013   | Get model by name   | User Error! The model does not exist.                                                     |
| DGA-S014   | User info save      | User Error! Invalid foreign key value.                                                    |
| DGA-S015   | User info save      | User Error! Error while saving input.                                                     |
| DGA-S016   | User info save      | User Error! The value if not suitable for the field.                                      |
| DGA-S017   | 1-1 Save            | User Error! The user's save input does not match the table or model fields configuration. |
| DGA-S018   | User related config | System Error! `user_related_field` is not set in system configuration.                    |
| DGA-S019   | User related config | System Error! Settings for User related model is not configured.                          |
| DGA-S020   | User related config | System Error! Given model is not configured in system configurations.                     |
| DGA-S021   | User related config | System Error! Fields are not configured in settings.                                      |
| DGA-S022   | 1-1 Save            | User Error! Invalid foreign key value.                                                    |
| DGA-S023   | User related config | System Error! The `user_related_field` is not a foreign key model.                        |
| DGA-S024   | User related config | System Error! The `user_related_field` is not user model.                                 |
| DGA-S025   | 1-1 Save            | User Error! Error while saving input.                                                     |
| DGA-S026   | 1-1 Save            | User Error! User has included `user_related_field` in `save_fields`.                      |
| DGA-S027   | 1-1 Fetch           | User Error! Extra fields in the payload are not allowed beyond fetch_fields.              |
| DGA-S028   | 1-1 Fetch           | User Error! Error while fetching data.                                                    |
| DGA-S029   | 1-1 Fetch           | User Error! User does not have access to fetch the model.                                 |
| DGA-S030   | 1-1 Save            | User Error! User does not have access to fetch the model.                                 |
| DGA-U001   | Field search        | User Error! Foreign key Field not found.                                                  |
| DGA-U002   | Field search        | User Error! User has passed an extra field.                                               |
| DGA-U003   | Request Rate        | User Error! The user has exceeded the request rate.                                       |
| DGA-U004   | Token               | User Error! The token is invalid or expired.                                              |
| DGA-U005   | User authentication | User Error! The user authentication has failed.                                           |
| DGA-U006   | Str to field model  | User Error! The field (str) is not found in model.                                        |
| DGA-U007   | Model is accessible | User Error! Access is denied to User related model.                                       |
