.EXPORT_ALL_VARIABLES:
.PHONY: test clean

GIT_COMMIT_SHA1=$(shell git rev-parse HEAD | cut -c 1-8)

clean:
	@find . -name '*.pyc' -exec rm \{\} \;
	@find . -name '.coverage*' -exec rm \{\} \;

test: clean
	@docker-compose -p test run -p 8000 --rm web green -vvv --run-coverage