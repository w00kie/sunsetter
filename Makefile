.EXPORT_ALL_VARIABLES:
.PHONY: test build clean

GIT_COMMIT_SHA1_BUILD=$(shell git rev-parse HEAD | cut -c 1-8)

clean:
	@find . -name '*.pyc' -exec rm \{\} \;
	@find . -name '.coverage' -exec rm \{\} \;
	rm -rf screenshots

build-test:
	docker compose -f docker-compose.test.yml build web

up:
	docker compose -f docker-compose.test.yml up

down:
	docker compose -f docker-compose.test.yml down

test: clean
	docker compose -f docker-compose.test.yml \
		run web python -m coverage run -m pytest

build-cloudrun:
	docker build --build-arg GIT_COMMIT_SHA1_BUILD \
		--tag gcr.io/sunsetter/web .

push:
	docker push gcr.io/sunsetter/web

build:
	docker build --build-arg GIT_COMMIT_SHA1_BUILD -t sunsetter:prod .
