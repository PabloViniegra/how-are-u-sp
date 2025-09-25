# 🎯 Facial Analysis API

A secure, comprehensive facial analysis API powered by Google's Gemini AI that evaluates facial attractiveness with scientific precision and detailed scoring metrics.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Endpoints](#-endpoints)
- [Response Examples](#-response-examples)
- [Project Structure](#-project-structure)
- [Development](#-development)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

- **🔍 Advanced Facial Analysis**: Comprehensive evaluation using Google Gemini AI
- **📊 Detailed Scoring System**: 10+ different facial metrics and scores
- **🔐 Secure Authentication**: API key-based security with multiple auth methods
- **📈 Analytics & Statistics**: Complete analysis history and statistical insights
- **🏗️ Modern Architecture**: Built with FastAPI following best practices
- **📝 Auto-Generated Documentation**: Interactive API docs with Swagger UI
- **🎨 Quality Assessment**: Image quality evaluation (denied/improvable/feasible)
- **💾 Persistent Storage**: SQLite database with comprehensive data models
- **🌐 CORS Support**: Configurable cross-origin resource sharing
- **📋 Comprehensive Logging**: Structured logging with detailed error tracking

## 🏗️ Architecture

```
Facial Analysis API
├── FastAPI Application (main.py)
├── Modular Routers
│   ├── Analysis Router (CRUD operations)
│   ├── Statistics Router (analytics)
│   └── Health Router (monitoring)
├── AI Services
│   ├── Google Gemini Integration
│   └── Image Processing Pipeline
├── Security Layer
│   ├── API Key Authentication
│   └── Request Validation
└── Data Layer
    ├── SQLAlchemy Models
    └── SQLite Database
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google AI API Key
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd facial-analysis-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start the server**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/health

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# Google AI Configuration
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./facial_analysis.db

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# File Upload Configuration
MAX_FILE_SIZE=10485760
ALLOWED_IMAGE_TYPES=["image/jpeg","image/jpg","image/png","image/webp"]

# AI Model Configuration
AI_MODEL_NAME=gemini-1.5-flash
AI_MAX_TOKENS=2048
AI_TEMPERATURE=0.1

# Application Configuration
DEBUG=True

# API Security (comma-separated API keys)
VALID_API_KEYS=key_123456789,key_abcdefghijk,key_facial_analysis_2024
```

## 📚 API Documentation

The API provides interactive documentation powered by FastAPI:

- **Swagger UI**: `/docs` - Interactive API explorer
- **ReDoc**: `/redoc` - Alternative documentation interface

## 🔐 Authentication

All endpoints (except `/health`) require API key authentication. Two methods are supported:

### Method 1: X-API-Key Header
```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:8000/api/analysis/
```

### Method 2: Bearer Token
```bash
curl -H "Authorization: Bearer your_api_key_here" http://localhost:8000/api/analysis/
```

## 🛣️ Endpoints

### Core Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | API information | ❌ |
| `GET` | `/api/health/` | Health check | ❌ |
| `POST` | `/api/analysis/` | Create facial analysis | ✅ |
| `GET` | `/api/analysis/` | List all analyses | ✅ |
| `GET` | `/api/analysis/{id}` | Get specific analysis | ✅ |
| `DELETE` | `/api/analysis/{id}` | Delete analysis | ✅ |
| `GET` | `/api/stats/` | Get analysis statistics | ✅ |

### Analysis Endpoint Details

#### POST `/api/analysis/`
Upload and analyze a facial image.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Image file (JPEG, PNG, WebP)
- Max file size: 10MB

**Response:**
```json
{
  "id": "uuid-string",
  "status": "feasible|improvable|denied",
  "overall_score": 7.5,
  "detailed_scores": {
    "symmetry": 8.0,
    "proportions": 7.2,
    "skin_quality": 7.8,
    "features_harmony": 7.0
  },
  "additional_scores": {
    "eye_appeal": 8.2,
    "nose_harmony": 7.5,
    "lip_aesthetics": 7.1,
    "jawline_definition": 6.8,
    "cheekbone_prominence": 7.3,
    "facial_composition": 7.6
  },
  "scientific_explanation": "Detailed analysis explanation...",
  "recommendations": "Improvement suggestions...",
  "analysis_date": "2024-01-15T10:30:00"
}
```

#### GET `/api/analysis/`
List all analyses with basic information.

**Response:**
```json
[
  {
    "id": "uuid-string",
    "overall_score": 7.5,
    "analysis_date": "2024-01-15T10:30:00"
  }
]
```

#### GET `/api/stats/`
Get comprehensive analysis statistics.

**Response:**
```json
{
  "total_analyses": 150,
  "average_score": 6.8,
  "score_distribution": {
    "0-2": 5,
    "2-4": 15,
    "4-6": 45,
    "6-8": 65,
    "8-10": 20
  }
}
```

## 📋 Response Examples

### Successful Analysis
```json
{
  "id": "f897553c-12aa-41d2-a7ef-4b8a34dd7c77",
  "status": "feasible",
  "overall_score": 7.2,
  "detailed_scores": {
    "symmetry": 8.1,
    "proportions": 7.5,
    "skin_quality": 6.8,
    "features_harmony": 6.9
  },
  "additional_scores": {
    "eye_appeal": 8.0,
    "nose_harmony": 7.2,
    "lip_aesthetics": 6.8,
    "jawline_definition": 7.1,
    "cheekbone_prominence": 7.5,
    "facial_composition": 7.3
  },
  "scientific_explanation": "The facial analysis reveals well-balanced proportions...",
  "recommendations": "Consider highlighting natural features...",
  "analysis_date": "2024-01-15T10:30:00.123456"
}
```

### Error Responses
```json
{
  "detail": {
    "error": "Invalid API key",
    "message": "The provided API key is not valid",
    "code": "INVALID_API_KEY"
  }
}
```

## 📁 Project Structure

```
facial-analysis-api/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration management
├── dependencies.py        # Common dependencies
├── database.py           # Database configuration
├── models.py             # SQLAlchemy models
├── schemas.py            # Pydantic schemas
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not in repo)
├── .gitignore           # Git ignore rules
│
├── routers/             # API route modules
│   ├── __init__.py
│   ├── analysis.py      # Analysis CRUD operations
│   ├── stats.py         # Statistics endpoints
│   └── health.py        # Health check endpoints
│
├── services/            # Business logic services
│   ├── __init__.py
│   ├── ai_service.py    # AI analysis service
│   └── image_service.py # Image processing service
│
├── middleware/          # Custom middleware
│   ├── __init__.py
│   └── api_key_auth.py  # API key authentication
│
└── tests/              # Test files (optional)
    ├── __init__.py
    ├── test_main.py
    ├── test_analysis.py
    └── test_auth.py
```

## 🛠️ Development

### Setting Up Development Environment

1. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run with auto-reload**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Environment variables for development**
   ```bash
   export DEBUG=True
   export DATABASE_URL=sqlite:///./dev_facial_analysis.db
   ```

### Code Quality

The project follows Python best practices:

- **PEP 8** code formatting
- **Type hints** for better code documentation
- **Docstrings** for all functions and classes
- **Error handling** with proper HTTP status codes
- **Logging** for debugging and monitoring

### Database Management

The application uses SQLAlchemy with SQLite:

```python
# Create tables
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine)"

# Access database
sqlite3 facial_analysis.db
```

## 🧪 Testing

### Manual Testing

1. **Health Check**
   ```bash
   curl http://localhost:8000/api/health/
   ```

2. **Authentication Test**
   ```bash
   curl -H "X-API-Key: your_key" http://localhost:8000/api/analysis/
   ```

3. **File Upload Test**
   ```bash
   curl -X POST \
     -H "X-API-Key: your_key" \
     -F "file=@test_image.jpg" \
     http://localhost:8000/api/analysis/
   ```

### Automated Testing

```bash
# Run tests (if test suite is available)
pytest tests/

# Run with coverage
pytest --cov=. tests/
```

## 🚀 Deployment

### Production Configuration

1. **Environment Setup**
   ```bash
   export DEBUG=False
   export DATABASE_URL=postgresql://user:pass@localhost/dbname  # Optional
   ```

2. **Using Gunicorn**
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Using Docker**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

### Security Considerations

- Use strong, unique API keys in production
- Enable HTTPS/TLS encryption
- Configure proper CORS settings
- Monitor and log API usage
- Implement rate limiting if needed
- Keep dependencies updated

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful facial analysis capabilities
- **FastAPI** for the excellent web framework
- **SQLAlchemy** for robust database management
- **Pydantic** for data validation and serialization

## 📞 Support

For support, questions, or feature requests:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the configuration section above

---

**Facial Analysis API v2.0.0** - Secure, accurate, and comprehensive facial analysis powered by AI.