database:
	docker-compose up postgres

clean-volume:
	docker-compose down --remove-orphans
	docker volume rm jakdojade_pgdata
