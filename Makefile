lint:
	ruff format
	ruff check --fix

test:
	python -m pytest --cov

build:
	docker buildx build \
				  --build-arg VERSION=$(shell git log --oneline . | wc -l | tr -d ' ') \
				  -t ghcr.io/fopina/tgbot-educabiz-$(shell git log --oneline . | wc -l | tr -d ' ') \
				  -t ghcr.io/fopina/tgbot-educabiz:latest \
				  --load \
				  .

testpub:
	docker buildx build \
	              --platform linux/amd64,linux/arm64 \
				  --build-arg VERSION=$(shell git log --oneline . | wc -l | tr -d ' ') \
				  -t ghcr.io/fopina/tgbot-educabiz-$(shell git log --oneline . | wc -l | tr -d ' ') \
				  -t ghcr.io/fopina/tgbot-educabiz:latest \
				  --push \
				  .

# tests in docker
tind:
	docker build -t x --target tests .
	docker run --rm x
