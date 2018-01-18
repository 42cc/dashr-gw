# Dash Ripple Gateway
A proof-of-concept DASH-Ripple gateway with no KYC created basing on
[the Dash budget proposal](https://www.dashcentral.org/p/OpenSourceRippleGw).

## Quick Start
The project uses Docker and Docker Compose. You have to have them
installed to run a gateway (highly recommended to use the latest
versions of them).

1. Create volumes for data of dashd and rippled:
```sh
docker volume create --name=dashd-data
docker volume create --name=rippled-data
```
2. Build a Docker image of the project and start it:
```sh
docker-compose build
docker-compose up -d
```
3. Apply database migrations and load initial data of pages to the DB:
```sh
docker exec dashripplegw_web_1 bash -c "./manage.py migrate && ./manage.py loaddata initial_pages.json"
```
4. Create an admin for your gateway:
```sh
docker exec -it dashripplegw_web_1 bash -c "./manage.py createsuperuser"
```
5. A web-page of the gateway will run [here](http://localhost:8000/).
You should be able to log in
[the admin panel](http://127.0.0.1:8000/admin/) with credentials created
earlier.
6. Adjust [settings](http://127.0.0.1:8000/admin/core/gatewaysettings/)
of your gateway and content of
[base pages](http://127.0.0.1:8000/admin/core/page/), set
[credentials of your Ripple wallet](http://127.0.0.1:8000/admin/core/ripplewalletcredentials/).
7. Wait until Ripple ledger and Dash blockchain are loaded.

It is possible to use Dash and Ripple test nets. Follow "comment" and
"uncomment" instructions in '[docker-compose.yml](docker-compose.yml)'
before running the above commands. You can generate test-net Ripple
credentials [here](https://ripple.com/build/xrp-test-net/).

## Tests
Run tests:
```sh
docker run --rm dashripplegw_web make test
```

## License
The project is released under [the MIT license](LICENSE).
