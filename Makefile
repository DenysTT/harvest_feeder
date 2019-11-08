release ?= develop
image = den4iks99/feed_harvest:$(release)
HARVEST_ACCESS_TOKEN = foo
HARVEST_ACCOUNT_ID = bar

build:
	docker build -t $(image) .

run:
	docker run --rm -e HARVEST_ACCESS_TOKEN=$(HARVEST_ACCESS_TOKEN) -e HARVEST_ACCOUNT_ID=$(HARVEST_ACCOUNT_ID) --name feeder $(image)
