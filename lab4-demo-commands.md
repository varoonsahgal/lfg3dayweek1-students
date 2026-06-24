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
