# Git Interface API microseervice 
## Instaltion and local run for development
### Instalation
```
pip3 install -r requirements.txt
```
### run
```
python3 -m flask run --host=0.0.0.0
```
### Build docker container and run
```
docker build --tag git-int-api .
docker run -d -p 5000:5000 git-int-api
```
## API Endpoints
This microservice expose next API end point

```GET /api/v1/getfile```

```GET /api/v1/getfiles```

```PUT /api/v1/addfile```

```PUT /api/v1/updatefile```

```POST /api/v1/createpr```

for more details load postman collection  
```
github_interface.postman_collection.json
```