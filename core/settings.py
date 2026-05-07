import os
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# 1. Carrega as variáveis do arquivo .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Configurações Básicas
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-substitua-isso-se-necessario')

# MELHORIA: DEBUG False em produção evita que mostre seu código em erros
DEBUG = os.environ.get('DEBUG', 'True').lower() in {'1', 'true', 'yes'}

# MELHORIA: Liste seu domínio da Vercel aqui para segurança
ALLOWED_HOSTS = ['*', 'sistema-vacina.vercel.app'] 

# MELHORIA: Resolve o erro 403 do seu amigo
CSRF_TRUSTED_ORIGINS = [
    'https://sistema-vacina.vercel.app',
    'https://*.vercel.app'
]

LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'index_escolha'

# 3. Apps e Middlewares
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'vacinas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Mantém o WhiteNoise aqui
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Caso você crie pastas de templates globais
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# 4. Banco de Dados (Supabase)
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600, # MELHORIA: Mantém a conexão aberta por mais tempo (mais rápido)
        ssl_require=True
    )
}

# 5. Configurações de Segurança e Idioma
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# 6. Arquivos Estáticos (Configuração Robusta para Vercel)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'vacinas', 'static'),
]

# MELHORIA: WhiteNoise com compressão (deixa o site mais rápido no celular)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'