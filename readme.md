# Task Manager API

A simple RESTful API for managing tasks, built with FastAPI.

## Technologies
- Python 3.7+
- FastAPI
- SQLAlchemy
- SQLite (for testing; update to PostgreSQL in production)
- Pydantic

## Setup Instructions

### 1. Create a virtual environment
Choose the command based on your operating system:

- **Linux/macOS:**
  ```bash
  python3 -m venv venv
  ```
- **Windows:**
  ```bash
  python -m venv venv
  ```

### 2. Activate the virtual environment

- **Linux/macOS:**
  ```bash
  source venv/bin/activate
  ```
- **Windows:**
  ```bash
  venv\Scripts\activate
  ```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
uvicorn main:app --reload
```

## API Endpoints

- **Create Task**: `POST /tasks/`  
  Request Body: `title`, `description` (optional), `status` (default "to do"), `due_date`

- **List Tasks**: `GET /tasks/`  
  Optional Query Parameters:  
  - `status` (filter by status)
  - `sort_by` ("created_at" or "due_date")
  - `limit` (number of tasks to return)
  - `offset` (offset for pagination)

- **Get Task by ID**: `GET /tasks/{task_id}`

- **Update Task**: `PUT /tasks/{task_id}`  
  Request Body: `title`, `description`, `status`, `due_date`

- **Delete Task**: `DELETE /tasks/{task_id}`

## Docker

(Optional) To run the application using Docker:

1. **Build the Docker image:**
   ```bash
   docker build -t task-manager-api .
   ```

2. **Run the Docker container:**
   ```bash
   docker run -p 8000:8000 task-manager-api
   ```

## Notes
- This project uses SQLite for testing purposes. For production, update the `DATABASE_URL` in `main.py` to use PostgreSQL.
- The project is kept simple to demonstrate core functionality while following best practices.