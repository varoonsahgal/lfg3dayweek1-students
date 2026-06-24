```code
docker run --name demo04-db \
  -e POSTGRES_USER=demouser \
  -e POSTGRES_PASSWORD=demosecret \
  -e POSTGRES_DB=demodb \
  -p 5433:5432 \
  -d postgres:16
```


```code
psql "postgresql://demouser:demosecret@localhost:5433/demodb" -c "SELECT 1;"
```


Create a scratch directory for demo files:
```bash
mkdir -p /tmp/demo04
cd /tmp/demo04
```


Install packages:
```bash
pip install "sqlalchemy>=2.0" "psycopg[binary]" python-dotenv
```

```bash
psql "postgresql://demouser:demosecret@localhost:5433/demodb"
```

Run this:

```bash
CREATE TABLE test_demo (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);
```

