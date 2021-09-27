FROM centos:8

RUN dnf install python3 -y

WORKDIR /opt/app
COPY scripts/models.py .
COPY scripts/requirements.txt .

RUN pip3 install pip -U
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3", "models.py" ]