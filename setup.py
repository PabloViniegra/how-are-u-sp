from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()
                    and not line.startswith("#")]

setup(
    name="facial-analysis-api",
    version="1.0.0",
    author="Pablo Viniegra Picazo",
    author_email="pablovpmadrid@gmail.com",
    description="API para análisis de atractivo facial usando IA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
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
