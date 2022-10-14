### Procfile
web: gunicorn gettingstarted.wsgi
web: sh setup.sh && streamlit run app.py

### Heroku

gcloud: Configuration is in Procfile

To test the package localy
```bash
heroku local

heroku ps:scale web=0
heroku ps:scale web=1
heroku restart
```


trianer-push
trianer-vetruve && git add . && git commit -m "Some push" && git push heroku master
heroku logs --tail
heroku builds:cache:purge -a fathomless-brook-99194  --confirm fathomless-brook-99194
killall streamlit

# Docker
https://medium.com/analytics-vidhya/deploying-streamlit-apps-to-google-app-engine-in-5-simple-steps-5e2e2bd5b172


# Build
docker build . -t streamlit-image

# Run a local version
docker run -p 8080:8080 --name streamlit-container streamlit-image

# Run a local container
docker restart streamlit-container

# Deploy on google
gcloud: Configuration is in the app.yaml and script 

docker build . -t streamlit-image && gcloud app deploy app.yaml --quiet

# Some gcloud options
gcloud projects create default
gcloud projects list
gcloud config configurations list




