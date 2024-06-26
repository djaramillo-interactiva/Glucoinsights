# Novo Glucoinsights

### Requirements

Python: 3.9.0

Django: 3.1.6

Svelte: 3.0.0

### Activate virtualenv

    pyenv activate product-gluco-3.9.16

### Install requirements.txt (Python)

    pip install -r requirements.txt

### Install package.json (JS)

    npm i

### Compile Svelte

    npm run-script build

### Database

Create db glucoinsights_db in Postgress or in Mysql for Cpanel

If database = mysql

In settings.py add

    import pymysql

    pymysql.install_as_MySQLdb()


### Update or create .env file

    DEBUG=True

    SECRET_KEY="eUMGE6qYGZFUmRuREUEDfMERUdcv81OIk84xypq3QCzksT2AkBGJhnO2NeyUyRYv"
    ALLOWED_HOSTS=*
    SECURE_SSL_REDIRECT=False

    ENGINE=django.db.backends.mysql
    DATABASE_NAME=name_db
    DATABASE_USER=name_user
    DATABASE_HOST=localhost
    DATABASE_PASSWORD=password_db
    DATABASE_PORT=port

### Run migrations

    python manage.py makemigrations

    python manage.py migrate

### Create superuser

    python manage.py createsuperuser

### Run server

    python manage.py runserver

[Go http:127.0.0.1:8000](http://127.0.0.1)