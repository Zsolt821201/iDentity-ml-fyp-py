# Django Command History

## Install Django Framework

### Pip

```bash
pip install django
pip install django-crispy-forms
pip3 install opencv
pip3 install opencv-contrib-python

pip install -r requirements.txt

```

#### Conda

```bash
conda install -c conda-forge django
conda install -c conda-forge django-crispy-forms
conda install  opencv-contrib-python 
conda install -c conda-forge pysqlite3
```

```bash
conda install -c conda-forge --file requirements.txt
```

## Create Website Project

```bash
django-admin startproject identity_website
```

## Create App

```bash
python manage.py startapp identity
```

## Create Superuser

```bash
python manage.py createsuperuser
```

## Migration

Note `0001` increments with each migration.

```bash
python manage.py makemigrations identity
python manage.py sqlmigrate identity 0001
python manage.py migrate

```bash
python manage.py migrate
```

## Run Server

```bash
python manage.py runserver
```

[https://docs.djangoproject.com/en/4.1/intro/tutorial01/](https://docs.djangoproject.com/en/4.1/intro/tutorial01/)

## Django Rest Command History

### Install Django Rest Framework

#### Pip Rest Framework

```bash
pip install djangorestframework
pip install markdown       # Markdown support for the browse-able API.
pip install django-filter  # Filtering support
```

#### Conda Rest Framework

```bash
conda install -c conda-forge djangorestframework
conda install -c conda-forge markdown
conda install -c conda-forge django-filter
```
