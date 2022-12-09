# download all bus stops, lines and its time tables
# script is not idempotent
# this takes about 25 minutes

python download_data/bus_stops.py
python download_data/lines.py
python download_data/time_tables.py
