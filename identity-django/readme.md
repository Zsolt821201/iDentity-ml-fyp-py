# Run Django Website

## Migration

```bash
python manage.py migrate
```

## Create Superuser

```bash
python manage.py createsuperuser
```

## Run Server

```bash
python manage.py runserver
```

### Command History

[https://docs.djangoproject.com/en/4.1/intro/tutorial01/](https://docs.djangoproject.com/en/4.1/intro/tutorial01/)

```bash
django-admin startproject 
```

```bash
identity_website
rename identity_website identity_django
cd identity_django
python manage.py startapp identity
python manage.py makemigrations identity
python manage.py sqlmigrate identity 0001
python manage.py migrate

python manage.py createsuperuser


```
