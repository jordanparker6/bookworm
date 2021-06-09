build:
	docker build . -t bookworm


tests:
	pytest -v

server:
	docker run -p 8000:8000 -v $(PWD)/app:/bookworm/app bookworm