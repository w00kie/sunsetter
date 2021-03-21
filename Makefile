.EXPORT_ALL_VARIABLES:
.PHONY: test build clean

GIT_COMMIT_SHA1_BUILD=$(shell git rev-parse HEAD | cut -c 1-8)

clean:
	@find . -name '*.pyc' -exec rm \{\} \;
	@find . -name '.coverage' -exec rm \{\} \;
	rm -rf screenshots

build-test:
	docker-compose -f docker-compose.test.yml -p test build

up:
	docker-compose -f docker-compose.test.yml -p test up

down:
	docker-compose -f docker-compose.test.yml -p test down

test: clean
	docker-compose -f docker-compose.test.yml -p test \
		run --rm --entrypoint green \
		web -vvv --run-coverage

build-cloudrun:
	docker build --build-arg GIT_COMMIT_SHA1_BUILD \
		--tag gcr.io/sunsetter/web .

push:
	docker push gcr.io/sunsetter/web

build:
	docker build --build-arg GIT_COMMIT_SHA1_BUILD -t sunsetter:prod .
