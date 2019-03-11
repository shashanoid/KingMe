FROM python:3.7.2-slim

# Creates the kingme user
# RUN adduser --disabled-login --gecos "First Last,RoomNumber,WorkPhone,HomePhone" kingme

# WORKDIR /home/kingme

# Copies the entire repository over
COPY . .

# Install python dependencies listed in src/requirements.txt
RUN pip install --upgrade pip && \
    pip install --default-timeout=100 -r src/requirements.txt

# RUN pip install pylint
# Get list of dependencies
# RUN echo $(pip freeze)

# Run unit tests
RUN python src/tests/test.py

# Set FLASK_APP (might not be necessary)
# ENV FLASK_APP src/flask/app.py

# Magic number - flask app is hosted on port 5000 on the container
EXPOSE 5000

# Specifies the command on startup of the image as python src/flask/app.py
ENTRYPOINT [ "python" ]
CMD [ "src/flask/app.py" ]
