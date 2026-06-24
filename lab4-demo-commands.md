docker run --name demo04-db \
  -e POSTGRES_USER=demouser \
  -e POSTGRES_PASSWORD=demosecret \
  -e POSTGRES_DB=demodb \
  -p 5433:5432 -d postgres:16  
