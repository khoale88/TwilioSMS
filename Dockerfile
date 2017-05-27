#A simple Flask app container
FROM python:2.7
MAINTAINER Khoa Le "lenguyenkhoa1988@gmail.com"

#Place app in container
COPY . /app
WORKDIR /app

#Install dependencies
RUN pip install -r requirements.txt

CMD python main.py
# ENTRYPOINT ["python"]
# CMD ["app.py"]
