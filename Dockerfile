FROM python:3

ENV INSTALL_PATH /sunsetter
RUN mkdir ${INSTALL_PATH}
WORKDIR ${INSTALL_PATH}

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .
