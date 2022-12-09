Project similar to jakdojade
find connections between bus stops in Warsaw based on https://api.um.warszawa.pl/
in order to use, You have to register there and add a file .api_key.txt with api key (config.py reads it)

first, app has to download all data from api, whis requires 3 scripts that take over 20 minutes
data lands in postgres database (8000 stops, 350 lines, 850_000 departures)

alhgoritm is a BFS that keeps fastest connection to every stop
for now, it will only find one fastest connection

example use: python walker/stops_available.py

