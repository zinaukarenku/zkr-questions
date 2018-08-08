.PHONY: all

pull:
	git pull

release:
	docker-compose up -d --build
