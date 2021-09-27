FROM centos:8

RUN dnf install python3 -y

WORKDIR /opt/app
COPY scripts/models.py .
COPY scripts/etl.py .
COPY scripts/ws_etl.py .
COPY scripts/requirements.txt .

RUN pip3 install pip -U
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "uvicorn", "ws_etl:app", "--host", "0.0.0.0" ]