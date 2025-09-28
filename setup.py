from setuptools import setup
import os

# Obtener la versión desde las variables de entorno o usar un valor por defecto
version = os.getenv('APP_VERSION', '1.0.0')

# Requirements básicos para deployment
requirements = [
    "fastapi==0.104.1",
    "uvicorn[standard]==0.24.0",
    "sqlalchemy==2.0.23",
    "alembic==1.12.1",
    "python-multipart==0.0.6",
    "pillow==10.1.0",
    "opencv-python==4.8.1.78",
    "google-generativeai==0.3.2",
    "python-dotenv==1.0.0",
    "pydantic==2.5.0",
    "pydantic-settings==2.1.0",
    "python-jose[cryptography]==3.3.0",
    "passlib[bcrypt]==1.7.4",
    "aiofiles==23.2.1",
    "structlog==23.2.0",
    "python-magic==0.4.27",
    "redis==5.0.1",
    "aioredis==2.0.1",
]

# Definir packages manualmente para evitar problemas de importación durante build
packages = [
    '',
    'services',
    'utils',
    'routers',
    'middleware',
]

# Leer README.md de forma segura
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "API para análisis de atractivo facial usando IA"

setup(
    name="facial-analysis-api",
    version=version,
    author="Pablo Viniegra Picazo",
    author_email="pablovpmadrid@gmail.com",
    description="API para análisis de atractivo facial usando IA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=packages,
    package_dir={'': '.'},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
        ],
        "production": [
            "gunicorn>=20.0.0",
            "prometheus-client>=0.14.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "facial-analysis-server=run_server:main",
        ],
    },
)
