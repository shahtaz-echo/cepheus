## running the app locally
- create virtual environment and active it
python -m venv env
source env/bin/activate

- install requirements packages
pip install -r requirements.txt


- run postgres on docker
docker run --name cepheus_db -e POSTGRES_USER=cepheus -e POSTGRES_PASSWORD=test1234 -e POSTGRES_DB=cepheus_db -p 5434:5432 -v cepheus_db_data:/var/lib/postgresql/data -d postgres:16

- run the app with uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 5010 --reload


## running postgres on docker

### start a container with a volume
docker run --name <container_name> -e POSTGRES_USER=<postgres_user> -e POSTGRES_PASSWORD=<postgres_password> -e POSTGRES_DB=<postgres_db_name> -p 5434:5432 -v <postgres_volume_name>:/var/lib/postgresql/data -d postgres:16

### get inside postgres database:
- docker ps
- docker exec -it <postgres_container_id> bash
- psql -U <postgres_user> -d <psotgres_db_name>

### psql command(example as product table)
- SELECT * FROM products;
- \d+ products -> get all columns
- DELETE FROM products; ->remove all the items
- \dt -> to see all the tables

MIGRATION ON TABLE (product_id was added later):
- ALTER TABLE products
- ADD COLUMN product_id VARCHAR NOT NULL;

- ALTER TABLE products
- ADD CONSTRAINT uix_tenant_product UNIQUE (tenant, product_id);