## running postgres on docker

### start with volume for the first time
docker run --name <container_name> -e POSTGRES_USER=<postgres_user> -e POSTGRES_PASSWORD=<postgres_password> -e POSTGRES_DB=<postgres_db_name> -p 5434:5432 -v <postgres_volume_name>:/var/lib/postgresql/data -d postgres:16

### run the container
docker run --name <container_name> -e POSTGRES_USER=<postgres_user> -e POSTGRES_PASSWORD=<postgres_password> -e POSTGRES_DB=<postgres_db_name> -p 5434:5432 -d postgres:16

### get inside postgres database:
- docker ps
- docker exec -it <postgres_container_id> bash
- psql -U <postgres_user> -d <psotgres_db_name>
