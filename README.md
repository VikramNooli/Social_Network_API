# Social Networking API

## Installation Steps

### Prerequisites

Make sure you have Docker and Docker Compose installed on your system. If not, you can download and install them from the official Docker website.

### Clone the Repository

1. Clone the repository using the following command:
    ```bash
    
    git clone https://github.com/VikramNooli/Social_Network_API.git
    
    ```

2. Change the directory to the project folder:
    ```bash
    
    cd Social_Network_API
    
    ```

### Setup and Run the Project

1. Build and start the Docker containers:
    ```bash
    docker-compose up --build
    ```

2. If you encounter unapplied migrations errors while running the above command, open a new terminal window and run the following command to apply migrations:
    ```bash
    docker-compose exec web python manage.py migrate
    ```

### Testing the API

You can now test the API endpoints using the POSTMAN tool or any other API testing tool of your choice.

## API Endpoints

Here are some key endpoints you can test:

### User Signup
- Endpoint: `/api/signup/`
- Method: `POST`
- Request Body:
  ```json
  {
    "email": "user@example.com",
    "password": "password123",
    "username":"test"
  }

### User Login
- Endpoint:  '/api/login/'
- Method: `POST`
- Request Body:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
