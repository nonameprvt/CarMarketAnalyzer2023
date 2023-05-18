FROM python:stretch
COPY ./backend/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
ADD . /code
WORKDIR /code
CMD ["python3", "./backend/car_market_backend.py"]
