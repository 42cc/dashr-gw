# Dash Ripple Gateway
## Quick Start
1. Create volumes for data of dashd and rippled.
```sh
docker volume create --name=dashd-data
docker volume create --name=rippled-data
```
2. Build Docker image of the project and start the project.
```sh
docker-compose build
docker-compose up -d
```
3. Apply DB migrations and load data of pages.
```sh
docker exec dashripplegw_web_1 bash -c "./manage.py migrate && ./manage.py loaddata initial_pages.json"
```
4. Create an admin for your gateway.
```sh
docker exec -it dashripplegw_web_1 bash -c "./manage.py createsuperuser"
```
