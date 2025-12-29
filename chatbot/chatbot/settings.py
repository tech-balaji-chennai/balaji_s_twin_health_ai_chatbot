# chatbot/chatbot/settings.py

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file for local development
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR is three levels up: chatbot/ -> chatbot/ -> root
# This path adjustment is CRITICAL for your structure (one level up for each folder).
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# --- Security and Environment ---
SECRET_KEY = os.getenv('SECRET_KEY', 'default-insecure-key-for-local-use-change-in-prod')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost').split(',')

# --- Gemini Configuration ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

# --- Application Definition ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',

    # Local apps
    'chat',  # The application where your AI logic resides
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST be near the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# The URL resolver name must match the project folder name:
ROOT_URLCONF = 'chatbot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'chatbot.wsgi.application'

# --- Database ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # Database file location is relative to the root (BASE_DIR)
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Static Files ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- CORS Settings (Crucial for the Frontend) ---
CORS_ALLOW_ALL_ORIGINS = True
# For production: set CORS_ALLOW_ALL_ORIGINS = False and use CORS_ALLOWED_ORIGINS
