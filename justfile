set dotenv-load := false

project_name := `grep APP_NAME .env | cut -d '=' -f 2-`
version := `python3 setup.py --version | tr '+' '-'`
pypi_index := `grep PYPI_INDEX .env | cut -d '=' -f2`
extra_packages := `grep EXTRA_PACKAGES .env | cut -d '=' -f2`
docker_registry := `grep DOCKER_REGISTRY .env | cut -d '=' -f2`
project_image := docker_registry+"/"+project_name

default: (dev)


clean:
	rm -rf .pytest_cache build dist *.egg-info


dist: clean
	python3 setup.py sdist bdist_wheel


docker: dist
	docker build --build-arg PYPI_INDEX={{pypi_index}} --build-arg EXTRA_PACKAGES={{extra_packages}} --target=app -t {{project_name}}:{{version}} .
	docker tag {{project_name}}:{{version}} {{project_name}}:latest


docker-compose: docker
	docker compose up --build


docker-no-cache: dist
	docker build --build-arg PYPI_INDEX={{pypi_index}} --build-arg EXTRA_PACKAGES={{extra_packages}} --target=app -t {{project_name}}:{{version}} --no-cache .
	docker tag {{project_name}}:{{version}} {{project_name}}:latest


upload: docker
	docker tag {{project_name}}:{{version}} {{project_image}}:{{version}}
	docker push {{project_image}}:{{version}}


publish: upload
	cd ansible;	ansible-playbook -i hosts.yml --extra-vars="playbook_action=update app_version={{version}}" playbook.yml
	git tag -a 'v{{version}}' -m 'v{{version}}'


host:
	cd ansible;	ansible-playbook -i hosts.yml --extra-vars="playbook_action=host" playbook.yml


dev:
	uvicorn --reload --port 3000 --log-level warning app.main:server


gunicorn:
	gunicorn -b 0.0.0.0:3000 --timeout 999 --threads 12 -k uvicorn.workers.UvicornWorker app.main:server
