# Train-Station-API-Service

Service for buying tickets and monitoring journeys

## Installing process
Change mocks to your native data inside .env.sample. Do not forget to change file name to ".env".
#### Run with IDE(configure local db instead of remote)
```
    git clone https://github.com/Dmytry95/Train-Station-API-Service.git
    cd TrainStationAPI
    python -m venv venv
    sourse venv/bin/activate
    pip install -r requirements.txt
    set SECRET_KEY=DJANGO_SECRET_KEY
    set POSTGRES_HOST=db
    set POSTGRES_NAME=your_db_name
    set POSTGRES_USER=db_user
    set PASSWORD=POSTGRES_PASSWORD
    python manage.py migrate
    python manage.py runserver
```

## Run with docker
Docker should be installed
#### Open terminal
```
    docker-compose build
    docker-compose up
```

## Getting access

* create user via /api/user/register
* get access token via api/user/token(do not forget to add "Bearer " before token)


## Features
* JWT authenticated
* Admin panel /admin/
* Managing orders with journey and tickets
* Creating stations, trains, journeys
* Filtering journeys by date
* The ability to add photos to trains and stations
