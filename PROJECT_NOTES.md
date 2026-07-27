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

## frontend user flow fixes

-Story input clears only after a successful POST, so failed posts keep the user's text.
-CSRF token retrieval and story POST now share one promise chain so every failure shows an error and restores the Submit button.
-New stories use the beginning of storiesList so search and reset keep newest-first order.
-Story loading errors display in the page error message and remain logged in the console.
-Registration and login preserve passwords exactly as entered while names and usernames remain trimmed.

Testing:
-JavaScript syntax checks passed for auth.js, login.js, and stories.js.
-Offline CSRF failure check confirmed story text remains, a visible error appears, and the Submit button resets.
-Backend pytest regression suite: 42 passed in 3.39 seconds.

## login rate limiting

-Login attempts use shared PostgreSQL counters so limits apply across Gunicorn workers and restarts without Redis or another service.
-Each normalized username is limited to 10 attempts per 15 minutes, and each client IP is limited to 30 attempts per 15 minutes.
-Usernames and normalized IP addresses are stored only as SECRET_KEY-backed HMAC digests.
-Expired counters are removed automatically during login, and successful login clears the account counter without clearing the shared IP counter.
-Limited requests return the same generic 429 JSON response for existing and nonexistent usernames, with Retry-After and Cache-Control: no-store headers.
-Nonexistent usernames run a dummy password-hash check so failed-login behavior does not reveal whether an account exists.
-The login page displays the rate-limit error to the user.
-Production requires TRUSTED_PROXY_COUNT=1 for the direct Azure App Service proxy. Local development uses TRUSTED_PROXY_COUNT=0 and ignores forwarded client-IP headers.
-Migration 002_login_rate_limits.sql creates the rate-limit table and expiration index.
-GitHub Actions uses its existing PostgreSQL service, sets TRUSTED_PROXY_COUNT=0, checks login.js syntax, and runs the complete pytest suite.

Testing:
-Python syntax checks passed for the backend application, migration runner, and affected tests.
-JavaScript syntax check passed for login.js.
-Migration creation and idempotency passed.
-Rate-limit tests covered account and IP limits, generic 429 headers, username normalization, successful-login reset, expiration cleanup, shared database connections, dummy password hashing, and trusted/untrusted proxy behavior.
-Backend pytest regression suite: 56 passed in 5.62 seconds using the isolated PostgreSQL test database.
