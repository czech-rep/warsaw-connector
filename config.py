database_url = "postgresql://postgres:postgres@localhost:5432/postgres"
# database_test_url = "postgresql://postgres:postgres@localhost:5432/postgres_test"

with open(".api_key.txt") as fl_:
    line = fl_.readline()
    api_key = line.strip()
