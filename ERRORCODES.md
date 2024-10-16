# ERROR CODES

| ERROR CODE    | MEANING                                                                             |
|---------------|-------------------------------------------------------------------------------------|
| DGA-0A        | User is trying to insert more than 10 records at once                               |
| DGA-0B        | User's save payload structure does not match predefined save payload                |
| DGA-0C        | User is trying to insert into a non existing model / table                          |
| DGA-0D        | User doesnt have permission to save or update data                                  |
| DGA-0E        | User gives invalid data to save or update                                           |
| DGA-0F        | User's fetch payload structure does not match predefined fetch payload              |
| DGA-0G        | User is trying to fetch from a non existing table / model                           |
| DGA-0H        | User does not have permissions to fetch data                                        |
| DGA-0I        | User is giving invalid data to fetch                                                |
| DGA-0J        | User's login payload structure does not match the predefined login payload          |
| DGA-0K        | User has given wrong login credentials                                              |
| DGA-0L        | User's register payload structure does not match the predefined register payload    |
| DGA-0M        | User's passwords does not match while registering themselves                        |
| DGA-0N        | User is registering with a email account which was registered before                |
| DGA-0O        | Error while sending Email confirmation mail                                         |
| DGA-0P        | User forgot password payload does not match with predefined forgot password payload |
| DGA-0Q        | User email activation link is clicked after 24 hours                                |
| DGA-0R        | User is trying to re-activate a active user                                         |
| DGA-0S        | User's token is faulty                                                              |
| DGA-0T        | Error at activating a user's email                                                  |
| DGA-0U        | User is trying to fetch with being logged in or having a access token               |
| DGA-0V        | User is trying to save or update with being logged in or having a access token      |                                                                                                                        |
| TOKENAUTH     | Access token authentication has failed                                              |
| FIELD_VAL     | User is trying to fetch with invalid data                                           |
| ONE_UPDATE    | User is trying to update from than 1 record at once                                 |
| BAD_INPUT     | User's save input does not match against table / model fields configuration         |
| NO_RECORD     | User is trying to update a record which does not exist                              |
| SAVE_ERROR    | User is trying to pass invalid id type                                              |
| UNKNOWN_FIELD | User is search a non existing field in table / model                                |
