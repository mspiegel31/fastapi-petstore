
FROM python:3.10-slim



ARG REQUIREMENTS="requirements/requirements.txt"

# install requirements
RUN pip install --upgrade pip && pip install pip-tools
COPY requirements/ requirements/
RUN pip-sync ${REQUIREMENTS}


WORKDIR /opt/app

COPY . /opt/app


CMD [ "uvicorn", "app.main:app", "--port", "80", "--host", "0.0.0.0", "--loop", "uvloop" ]
