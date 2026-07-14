# Smart Task Platform

A lightweight Flask-based task management platform with built-in analytics, feature flagging, and experiment support.

## What it does
- User registration and login
- Task creation, update, completion, and deletion for the authenticated user
- Basic analytics endpoints: DAU, tasks created, completion rate, task counts by priority and status
- Feature flag endpoints for enabling/disabling runtime features
- Experiment assignment and results tracking

## Setup
1. Create or activate Python environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python run.py
   ```
4. Open the browser at `http://127.0.0.1:5000`

## Database
- Uses SQLite via `database.db`
- Tables are created automatically on startup:
  - `users`
  - `tasks`
  - `events`
  - `experiments`
  - `feature_flags`
  - `backlog_items`

## Main pages
- `/` : Dashboard UI (`templates/index.html`)

## API endpoints
### Authentication
- `POST /signup` : register a new user
- `POST /login` : authenticate a user
- `POST /logout` : clear session

### Task management
- `POST /task` : create a task
- `PUT /task/<task_id>` : update a task
- `PUT /task/<task_id>/complete` : mark a task completed
- `PUT /task/<task_id>/status` : update task status
- `DELETE /task/<task_id>` : delete a task
- `GET /tasks` : list tasks for the logged-in user

### Analytics
- `GET /analytics/dau` : daily active users
- `GET /analytics/tasks-created` : total tasks created
- `GET /analytics/completion-rate` : completion rate
- `GET /analytics/tasks-by-priority` : tasks grouped by priority
- `GET /analytics/tasks-by-status` : tasks grouped by status

### Experiments
- `GET /experiment/<experiment_name>/<user_id>` : assign or return variant
- `GET /experiment/<experiment_name>/results` : experiment results

### Feature flags
- `GET /feature/<feature_name>` : check feature status
- `POST /feature/<feature_name>/enable` : enable feature
- `POST /feature/<feature_name>/disable` : disable feature

## Notes
- The app uses Flask sessions and `SECRET_KEY` can be set via environment variable.
- The dashboard is served from `templates/index.html` and `static/js/dashboard.js`.
- Basic project structure is in `app/` and tests are in `tests/`.
