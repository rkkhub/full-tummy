# full-tummy


Migrations
```
docker-compose run --rm app sh -c "python manage.py makemigrations"
```

For testing the setup
```
docker-compose run --rm app sh -c "python manage.py test && flake8"
```

For running the setup in local environment

```
docker-compose run -d app sh -c "python manage.py runserver 0:8000"
```

```
docker-compose run --rm app sh -c "python manage.py startapp recipe"
```