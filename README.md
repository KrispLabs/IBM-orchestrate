# IBM Orchestrate

IBM Orchestrate is an innovative system designed to automate the creation and maintenance of tests for your codebase. By leveraging IBM Bob as a smart assistant, it ensures that your code is always reliable and up-to-date without the manual effort of writing and updating tests.

## Key Features
- **Automated Test Generation**: Reads your code, understands its functionality, and generates tests automatically.
- **Test Maintenance**: Automatically updates tests whenever the code changes.
- **Focus on Development**: Allows developers to concentrate on building features while ensuring reliability in the background.

## Why IBM Orchestrate?
Writing and maintaining tests can be time-consuming and error-prone. IBM Orchestrate eliminates this hassle, reducing bugs and improving the overall development workflow.

## Headstart Guide

### Prerequisites
Ensure the following tools are installed on your system:
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Quick Start with Docker
1. Clone the repository:
   ```bash
   git clone https://github.com/Syrthax/IBM-orchestrate.git
   cd IBM-orchestrate
   ```
2. Start all services:
   ```bash
   docker-compose up -d
   ```
3. Run migrations:
   ```bash
   docker-compose exec backend python manage.py migrate
   ```
4. Create a superuser:
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```
5. Access the application:
   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - Admin: [http://localhost:8000/admin](http://localhost:8000/admin)

### Manual Setup

#### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

#### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## Contributing
We welcome contributions! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.