# Build/Run Django Website

For more documentation, see [Writing your first Django app](https://docs.djangoproject.com/en/4.1/intro/tutorial01/)

## Create Project

```bash
django-admin startproject identity_website
```

```bash
cd identity_website
```

## Create App

```bash
python manage.py startapp identity
```

## Migration

Note `0001` increments with each migration.

```bash
python manage.py makemigrations identity
python manage.py sqlmigrate identity 0001
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

## Testing

```bash
manage.py test animals.tests.AnimalTestCase.test_animals_can_speak
```
