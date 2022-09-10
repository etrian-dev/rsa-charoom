# Application
- Chat page design (two-sided columns)
- Left header for navigation
- index page on route '/'
- User detail page
- randomize user id at user registration
- Add header with login info in all user views
- Encryption/decryption of message data with RSA
- logout function and proper authentication (maybe sessions)
  + issue in @login_required decorator with args from variable routes
  + repetitiveness of checking for authorization with Auth.authorized(uid)
- Fix timestamp for message viewing order in messages.html
 + Needs revision on Chat.py:display_chat
- In msg.py all function that modify a chat (adding a message, deleting one) should update the
last_mod_tm field of the Chat object in the db
- Edit db schema to have a timestamp for the last two attributes
- Develop & testing of query maker (in db.py)
# Container
- Add volume to make source changes shared between host and container
