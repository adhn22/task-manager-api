# API Design

## Base URL

## Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | User registration |
| POST | `/api/auth/login/` | Login, returns JWT token |
| POST | `/api/auth/logout/` | Logout |
| GET | `/api/auth/profile/` | View authenticated user data |
| PATCH | `/api/auth/profile/` | Update email |
| POST | `/api/auth/change-password/` | Change password |

## Tasks

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tasks/` | List all user tasks |
| POST | `/api/tasks/` | Create a task |
| GET | `/api/tasks/{id}/` | View task detail |
| PUT | `/api/tasks/{id}/` | Full task update |
| PATCH | `/api/tasks/{id}/` | Partial task update |
| DELETE | `/api/tasks/{id}/` | Delete a task |

## Notes

- All task endpoints require authentication
- A user can only access their own tasks
- Task listing supports filtering by status and priority