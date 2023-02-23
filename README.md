# Quick-Notes
**A RESTFUL API that allows for the creation, retrieval, updating, searching and deleting of notes.**

## API Endpoints

__BASE_URL__: [https://quicknotesapi.pythonanywhere.com/api/](https://quicknotesapi.pythonanywhere.com/api/)

### END POINTS

- **User related endpoints --> "api/accounts/"**
  - `GET` 'accounts/'
  - `POST` 'accounts/create/'
  - `POST` 'accounts/authenticate/'
  - `GET` 'accounts/find/?q='
  - `GET` 'accounts/<str:username>/'
  - `PUT` 'accounts/<str:username>/update/'
  - `DELETE` 'accounts/<str:username>/delete/'
 
 
- **Notes related endpoints --> "api/notes/"**
  - `GET` `POST` 'notes/'
  - `GET` 'notes/find/'
  - `GET` 'notes/starred/'
  - `GET` 'notes/<str:slug>/'
  - `PUT` 'notes/<str:slug>/edit/'
  - `DELETE` 'notes/<str:slug>/delete/'
  
  
### 1. User related endpoints ---> `api/accounts/`

- ### `GET` **"accounts/"** 

    > Returns all user accounts. Only accesible by admin users.
    
    _Example `GET` response data_
    
    <code>
    {
      "count": 2,
      "next": null,
      "previous": null,
      "results": [
              {
                  "edit_url": "http://127.0.0.1:8000/api/accounts/Tolu/update/",
                  "username": "Tolu",
                  "fullname": "Daniel Afolayan",
                  "email": "toltol@gmail.com",
                  "firstname": "Daniel",
                  "lastname": "Afolayan",
                  "number_of_notes": 1,
                  "last_active": "2023-02-22 at 14:45:43.953321",
                  "date_joined": "2023-02-22 at 14:45:43.953321"
              },
              {
                  "edit_url": "http://127.0.0.1:8000/api/accounts/Test%20user/update/",
                  "username": "Test user",
                  "fullname": "Tester Alimony",
                  "email": "testsing@yahoo.com",
                  "firstname": "Tester",
                  "lastname": "Alimony",
                  "number_of_notes": 0,
                  "last_active": "2023-02-22 at 23:32:21.624681",
                  "date_joined": "2023-02-22 at 23:32:21.624681"
              },
              ...,
          ]
      }
      </code>
      
##

- ### `POST` **"accounts/create/"** 

    > Send account creation details. Returns the user object created and related details.
    
    _Example `POST` request data_
    
    <code>
    {
        "username": "Jane",
        "firstname": "Jane",
        "lastname": "Doe",
        "other_name": "Alice",
        "email": "janedoe@outlook.com",
        "password": "testing321",
        "confirm_password": "testing321"
    }
    </code>
    
    _Response data_
    
    <code>
    {
        "username": "Jane",
        "fullname": "Jane Alice Doe",
        "firstname": "Jane",
        "lastname": "Doe",
        "other_name": "Alice",
        "email": "janedoe@outlook.com",
        "url": "http://127.0.0.1:8000/api/accounts/Jane/",
        "edit_url": "http://127.0.0.1:8000/api/accounts/Jane/update/",
        "last_active": "2023-02-22 at 23:52:50.660249",
        "number_of_notes": 0,
        "number_of_starred_notes": 0,
        "last_created_note": null,
        "last_edited_note": null
    }
    </code>
    
##

> ### NOTE: ContentType for `POST` requests should `application/json`

##
    
- ### `POST` **"accounts/authenticate/"** 

    > Send user details "username" and "password" for authentication/login. Returns a authorization token
    
    _Example `POST` request data_
    
    `{"username": username, "password": user_password}`
    
    _Response data_
    
    `{"token": "12345678901234567890"}`
    
    ### Going forward, all requests must be made with this authorization token in the request headers
    
    _For example_
    
    <code>
    import requests
    auth_endpoint = "http://127.0.0.1:8000/api/authenticate/"
    auth_response = requests.post(auth_endpoint, json={"username": username, "password": user_password})
    print(auth_response.json()) # To see response
    </code>
    <code>
    if auth_response.status_code == 200:
        token = auth_response.json().get('token', '')
        headers = {
            "Authorization": f"Bearer {token}",
        }
        endpoint = "http://127.0.0.1:8000/api/notes/"
        response = requests.get(endpoint, headers=headers)
    </code>
    
  ##
  
- ### `GET` **"accounts/find/"** 

  > Search user accounts. Takes one query parameter `?q=<query>`. Only accesible by admin users.

  _Example `GET` request_
  
  <code>
  endpoint = http://127.0.0.1:8000/api/accounts/find/?q=Dan
  response = request.get(endpoint)
  </code>

  _Response_

  <code>
  {
      "count": 1,
      "next": null,
      "previous": null,
      "results": [
          {
              "username": "Tolu",
              "fullname": "Daniel Afolayan",
              "email": "toltol@gmail.com",
              "firstname": "Daniel",
              "lastname": "Afolayan",
              "edit_url": "http://127.0.0.1:8000/api/accounts/Tolu/update/",
              "number_of_notes": 1,
              "last_active": "2023-02-22 at 14:45:43.953321",
              "date_joined": "2023-02-22 at 14:45:43.953321"
          }
      ]
  }
  </code>
  
  ##
  
  - ### `GET` **"accounts/<str:username>/"** 

  > Get user account detail. Only accesible to the account owner and admin.

  _Example response_

  <code>
  {
      "username": "Tolu",
      "fullname": "Daniel Afolayan",
      "firstname": "Daniel",
      "lastname": "Afolayan",
      "other_name": "",
      "email": "toltol@gmail.com",
      "url": "http://127.0.0.1:8000/api/accounts/Tolu/",
      "edit_url": "http://127.0.0.1:8000/api/accounts/Tolu/update/",
      "last_active": "2023-02-22 at 14:45:43.953321",
      "number_of_notes": 1,
      "number_of_starred_notes": 0,
      "last_created_note": "http://127.0.0.1:8000/api/notes/new-note/",
      "last_edited_note": "http://127.0.0.1:8000/api/notes/new-note/"
  }
  </code>
  
  ##
  
  - ### `POST` **"accounts/<str:username>/update/"** 

  > Update user account detail. Only accesible to the account owner and admin.

  _Example POST request_

  <code>
  {
      "username": "Tolu",
      "firstname": "Toluwalase",
      "lastname": "Adeyemi",
      "other_name": "",
      "email": "testing@yahoo.com"
  }
  </code>
  
  _Example response_
  
  
  
  

