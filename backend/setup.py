from setuptools import setup, find_packages

setup(
    name="stock-astrology-app",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "Werkzeug==2.3.7", 
        "Flask-SQLAlchemy==3.0.5",
        "Flask-CORS==4.0.0",
        "gunicorn==20.1.0",
        "python-dotenv==0.19.2",
    ],
    python_requires=">=3.7",
)
