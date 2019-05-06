.EXPORT_ALL_VARIABLES:
.PHONY: test build clean

OSRELEASE = $(shell cat /proc/sys/kernel/osrelease)
ifneq (,$(findstring Microsoft,$(OSRELEASE)))
	docker_cmd = docker.exe
	compose_cmd = docker-compose.exe
else
	docker_cmd = docker
	compose_cmd = docker-compose
endif

GIT_COMMIT_SHA1_BUILD=$(shell git rev-parse HEAD | cut -c 1-8)

clean:
	@find . -name '*.pyc' -exec rm \{\} \;
	@find . -name '.coverage*' -exec rm \{\} \;

build-test:
	@$(compose_cmd) -f docker-compose.test.yml -p test build

up:
	$(compose_cmd) -f docker-compose.test.yml -p test up

down:
	$(compose_cmd) -f docker-compose.test.yml -p test down

test: clean
	@$(compose_cmd) -f docker-compose.test.yml -p test \
		run --rm --entrypoint green \
		web -vvv --run-coverage

build-cloudrun:
	@$(docker_cmd) build --build-arg GIT_COMMIT_SHA1_BUILD \
		--tag gcr.io/sunsetter/web .

push:
	@$(docker_cmd) push gcr.io/sunsetter/web

build:
	@$(docker_cmd) build --build-arg GIT_COMMIT_SHA1_BUILD -t sunsetter:prod .