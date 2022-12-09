from postgres

ENV POSTGRES_PASSWORD="postgres"
ENV POSTGRES_USER="postgres"

VOLUME /data:/var/lib/postgresql/data 

# USER 10

# The VOLUME instruction creates a mount point 
# with the specified name and marks it as holding 
# externally mounted volumes from native host 
# or other containers. The value can be a JSON array, 
# VOLUME ["/var/log/"], or a plain string with multiple arguments, 
# such as VOLUME /var/log or VOLUME /var/log /var/db. 
# For more information/examples and mounting instructions 
# via the Docker client, refer to Share Directories via Volumes documentation.
