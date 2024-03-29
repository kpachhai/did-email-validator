FROM python:3.8

ADD requirements.txt /src/
RUN cd /src && pip install -r requirements.txt

ADD app /src/app
ADD lib /src/lib

WORKDIR /src

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:application"]

EXPOSE 5000