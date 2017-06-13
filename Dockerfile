#A simple Flask app container
FROM python:3.5
MAINTAINER Khoa Le "lenguyenkhoa1988@gmail.com"

#Place app in container
COPY . /app
WORKDIR /app

#Install dependencies either use -r requirements file or -e .
RUN pip install -r requirements.txt
# RUN pip install -e .
ENV FLASK_APP=twilio_app
ENV FLASK_DEBUG=true

# use the 1st command if "pip install -r requiremnts is used" 
# and when application.py file is required to deploy to cloud, e.g. beanstalk
CMD python application.py
# CMD flask run --host=0.0.0.0

# ENTRYPOINT ["python"]
# CMD ["app.py"]
