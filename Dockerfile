# Base Image to use
FROM python:3.10.5-slim

# Change Working Directory to app directory
WORKDIR /app
ADD . ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt \
    && rm -rf requirements.txt
WORKDIR /app


# Choose port
EXPOSE 8080
CMD sh setup.sh && streamlit run app.py --server.fileWatcherType none

