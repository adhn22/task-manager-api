# Requirements

## Features

- User registration with email and password
- Login and logout (JWT)
- Create a task
- View all tasks
- View task details
- Edit a task
- Delete a task
- Filter tasks by status and priority
- Mark a task as completed

## Business Rules

- A user can only view and modify their own tasks
- A task must have at least a title
- The due date cannot be a past date when creating a task
- A completed task cannot be edited

## Non-Functional Requirements

- JWT authentication
- Clear and consistent error responses
- Pagination on task listing
- Auto-generated API documentation (Swagger)