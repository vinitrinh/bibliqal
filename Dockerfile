FROM tensorflow/tensorflow:latest-py3
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "--server.port", "5000","--server.headless","true", "--browser.serverAddress","0.0.0.0", "--server.enableCORS", "false",  "app.py"]
