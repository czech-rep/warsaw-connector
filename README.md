Project similar to Jakdojade

find connections between bus stops in Warsaw based on https://api.um.warszawa.pl/

in order to use, You have to register there and add a file .api_key.txt with api key (config.py reads it)

first, app has to download all data from api, whis requires 3 scripts that take over 20 minutes

data lands in postgres database (8000 stops, 350 lines, 850_000 departures)

alhgoritm is a BFS that keeps one fastest connection to every stop

for now, it will only find one fastest connection


example use: python walker/stops_available.py


search to Cm.Północny-Brama Płn. 01 from Pogodna 02 at 11:45:00

Line 502 11:54:00 from Pogodna 02 to Płowiecka 03 at 12:13:00

Line 722 12:15:00 from Płowiecka 01 to Wspólna Droga 01 at 12:22:00

Line 6 12:26:00 from Wspólna Droga 03 to Cm.Włoski 04 at 13:10:00

Line 181 13:23:00 from Cm.Włoski 02 to Cm.Północny-Brama Płn. 02 at 13:31:00

-  measured 0 min 16.7 s
