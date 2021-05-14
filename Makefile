build:
	docker build . -t bookworm

corenlp:
	docker run -p 9000:9000 --name coreNLP --rm -i -t frnkenstien/corenlp

server:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000