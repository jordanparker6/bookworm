build:
	docker build . -t bookworm

corenlp:
	docker run -p 9000:9000 --name coreNLP --rm -i -t frnkenstien/corenlp

server:
	docker run -p 8000:8000 -v $(PWD)/app:/bookworm/app bookworm