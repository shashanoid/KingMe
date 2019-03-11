container=test
local_port=8000
container_flask_port=5000
python=python3

# Use python on windows
ifeq ($(OS),Windows_NT)
	python=python
endif

fresh: clean build run

build:
# Creates an image with name as specified by $(container)
	docker build -t $(container) .

run:
# Runs the image created by build
# -d 	runs the container in the background
# -p 	specifies a port mapping of the local machines $(local_port) to
# 	the container's machine $(container_flask_port)
	docker run -p $(local_port):$(container_flask_port) -d $(container)
	@echo Running on 127.0.0.1:$(local_port)

local-run:
# Runs the flask server locally without using a docker instance
	@$(python) src/flask/app.py

stop:
# Stop all running containers
	-@docker stop $$(docker ps -aq)

test:
# Run unit tests
	$(python) src/tests/test.py

lint:
# Run linter
# pip install pylint
	@pylint src/
# npm install -g jshint
	@jshint src/static/js

clean: stop
# Stop and remove all containers
	-@docker rm $$(docker ps -aq)
	-@rm -rf *~

coverage:
	@coverage run src/tests/test.py
	@coverage report -m