Version12
## Version 12.1 - Live Story Search

Features:
- Added search input above Recent Stories.
- Search updates live while the user types.
- Search is case-insensitive.
- Stories are filtered using JavaScript.
- Original stories array remains unchanged.
- Clearing the search restores all stories.

Concepts Learned:
- input event
- Array.filter()
- String.includes()
- DOM re-rendering
- Separating data from UI

"Version 13.2 - Add registration frontend"

## DELETE AND EDIT AUTHORIZARION

-Adding edit and delete authroization
-updating the ui to display delete and edit when currentuser.id matches storyownerid
prior currentUser route exsited to display the user's name; it has now envolved to authorized edit and delete

current_user() route returns the id and name of the user logged in
CHANGES
UPDATE get_story route to return the stories.user_id

the frontend loadstories() function recieves the object return from the get_story route
loadstories() calls the displayStory(storyObject)=>calls createStoryElement(storyObject, isOWner)

if owner is true i should see a delete and edit button next to their story if false no delete and edit button

login route creates the session amd stores the id
current user uses sessions id to identify the current user
create_story uses session id to verify a current user and return tha users name and storyOBject
delete and PATCH utilzes session id to authorize the right person to delete and edit story

get_story uses the session id to comfrimed a authenticate user before fetching all stories

stories.html
      ↓
initializePage()
      ↓
loadCurrentUser()
      ↓
currentUser exists?
     /        \
   Yes         No
    ↓           ↓
loadStories()   Redirect to login.html

## verify is behavior:

Owner sees Edit/Delete.
Non-owner does not see Edit/Delete.
Logged-out user is redirected.
Manually sending PATCH/DELETE as a non-owner still gets 403 from Flask.

## deployment
1. REFRACTOR URL FROM JUST LOCAL TO LOCAL AND DEPLOYMENT READY

2. CONFIGUGE CORS FOR GLOBAL URL

3. prepare Flask to run on Render with Gunicorn

## deployment testing

-Added a pytest backend test suite using a dedicated PostgreSQL test database.
-Covered registration, login/logout, malformed requests, CSRF, story creation and 1-500 limits, ownership authorization, 400/401/403/404 responses, and migration creation/idempotency.
-TEST_DATABASE_URL is required. Tests stop before database cleanup when it is missing or points to the same database as DATABASE_URL, including localhost and 127.0.0.1 equivalents.
-GitHub Actions runs pytest for pull requests and branch pushes with a PostgreSQL service database named community_app_test.

Run locally from backend:

python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
createdb community_app_test
TEST_DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/community_app_test SECRET_KEY=test-secret pytest

Final result:
-pytest: 42 passed in 3.31 seconds using an isolated PostgreSQL 17.10 test database.
-Safety checks confirmed pytest refuses to start when TEST_DATABASE_URL is missing or matches DATABASE_URL.
