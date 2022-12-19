database:
	docker-compose up --detach postgres

clean-volumes:
	docker-compose down --remove-orphans
	docker volume rm jakdojade_pgdata

database-build-tables:
	alembic upgrade head
