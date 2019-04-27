.EXPORT_ALL_VARIABLES:
.PHONY: test build clean

OSRELEASE = $(shell cat /proc/sys/kernel/osrelease)
ifneq (,$(findstring Microsoft,$(OSRELEASE)))
	compose_cmd = docker-compose.exe
else
	compose_cmd = docker-compose
endif

GIT_COMMIT_SHA1=$(shell git rev-parse HEAD | cut -c 1-8)

clean:
	@find . -name '*.pyc' -exec rm \{\} \;
	@find . -name '.coverage*' -exec rm \{\} \;

build-test:
	@$(compose_cmd) -f docker-compose.test.yml -p test \
		build web

test: clean
	@$(compose_cmd) -f docker-compose.test.yml \
		-p test run -p 8000 --rm \
		web green -vvv --run-coverage

build:
	@$(compose_cmd) build web