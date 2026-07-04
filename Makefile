lint:
	uv run ruff format
	uv run ruff check --fix

lint-check:
	uv run ruff format --diff
	uv run ruff check

test:
	if [ -n "$(GITHUB_RUN_ID)" ]; then \
		uv run pytest --cov --cov-report=xml --junitxml=junit.xml -o junit_family=legacy; \
	else \
		uv run python -m pytest --cov; \
	fi

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
