#FROM nvidia/cuda:10.2-base
FROM python:3.8

#set up environment
RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y curl && apt-get install -y wget
RUN apt-get install unzip
RUN apt install -y default-jre
#RUN apt-get -y install python3.6 && apt-get -y install python3-pip && apt-get -y install git


# install from source
#RUN git clone https://github.com/thunlp/OpenNRE.git && cd OpenNRE && pip3 install -r requirements.txt && python setup.py install

# set the working directory in the container
WORKDIR /bookworm

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip3 install -r requirements.txt

# install models
RUN (echo "import stanza"; echo "stanza.install_corenlp()") | python
RUN python -m spacy download "en_core_web_trf"

# copy the content of the local src directory to the working directory
COPY app/ ./app

# command to run on container start
CMD [ "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000" ]