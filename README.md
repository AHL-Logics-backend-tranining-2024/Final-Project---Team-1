
# Final-Project---Team-1  

## Setup Instructions  

### 1. Set up a Virtual Environment  
Create a virtual environment using Python’s `venv` module.  

```bash
python3 -m venv venv
```

### 2. Activate the Virtual Environment  
Activate the virtual environment:  

- **On macOS/Linux:**  
  ```bash
  source venv/bin/activate
  ```

- **On Windows:**  
  ```bash
  .\venv\Scripts\activate
  ```

### 3. Install Dependencies  
Install the required Python packages from the `requirements.txt` file.  

```bash
pip install -r requirements.txt
```

---

## How to Run the App  

### Option 1: Run the App Locally  

You can run the FastAPI app locally with:  
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Option 2: Run the App with Docker  

#### 1. Create a `.env` file  
Create a `.env` file in the project’s root directory with the following variables:

```env
POSTGRES_USER=your_postgres_user  
POSTGRES_PASSWORD=your_postgres_password  
POSTGRES_DB=your_database_name  
PGADMIN_DEFAULT_EMAIL=your_pgadmin_email@example.com  
PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password  
```

#### 2. Build and Run the Docker Containers  
Make sure Docker is installed and running on your machine. Use the following command to build and start the services:  

```bash
docker-compose up --build
```

#### 3. Verify the Containers  

- **FastAPI App**: Accessible at [http://localhost:8000](http://localhost:8000)  
- **PgAdmin**: Accessible at [http://localhost:8080](http://localhost:8080)  

Use the credentials from your `.env` file to log in to PgAdmin.  

---

## Database Management  

- **PostgreSQL**: Running on port `5432`.  
- **PgAdmin**: Available on port `8080`.  

The PostgreSQL data is persisted in the Docker volume named `postgres_data`.  

---

## Restarting Services  

To restart the containers, run:  
```bash
docker-compose restart
```

To stop the services, use:  
```bash
docker-compose down
```

