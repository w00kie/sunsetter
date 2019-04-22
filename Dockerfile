FROM python:3

ENV INSTALL_PATH /sunsetter
RUN mkdir ${INSTALL_PATH}
WORKDIR ${INSTALL_PATH}

COPY requirements/ requirements/

RUN pip install -r requirements/test.txt

COPY . .
