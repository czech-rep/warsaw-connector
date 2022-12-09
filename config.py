database_url = "postgresql://postgres:postgres@localhost:5432/postgres"

with open(".api_key.txt") as fl_:
    line = fl_.readline()
    api_key = line.strip()
