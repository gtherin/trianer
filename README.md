
The aim of this package is dedicated to planify running or triathlon long races.

> This package used to be deployed on heroku. 
See se


#### 💗 Athlete

This section summarizes physiological constraints.
Only the weights might be updated once in a while

#### 🌍 Race

This section let you the choice between:

1. Use a known format for a race (ironman,  marathon, ...).
Average slopes can be configured manualy.

2. Use a known race. Mostly french races for now.
Gpx track quality might be poor. Shoud be nice to better filter them.

3. Have a fully personalized race. Discipline can be added.

##### Temperature

Temperature is an important parameter to simulate the dehydration.
By default (automatic mode), it is using the date and place of the race.
For all cases, **it is filtered by typical intraday** to replicate best its estimations.

#### 🏊🚴🏃 Performances

It is what you think you can perform on that distance.
**The estimated speed will take into account the relief and temperatures parameters.**

#### 🏆Simulation

The final estimation and nutrition plans need for the accomplishement of the race

#### 💦 Training (beta mode ⚠️🚧)

Should contains the training plan to get to that objective.
The app is a web wrapper to the [trianer website](https://trianer.guydegnol.net).

### Installation


To run it localy
```
git clone 
https://github.com/guydegnol/trianer

```
[Contact](mailto:gt@guydegnol.net)


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

<https://medium.com/analytics-vidhya/deploying-streamlit-apps-to-google-app-engine-in-5-simple-steps-5e2e2bd5b172>

# Build

docker build . -t streamlit-image

# Run a local version

docker run -p 8080:8080 --name streamlit-container streamlit-image

#

docker run -p 8081:8081 --name streamlit-container streamlit-image

# Run a local container

docker restart streamlit-container

# Deploy on google

gcloud: Configuration is in the app.yaml and script

docker build . -t streamlit-image && gcloud app deploy app.yaml
 --quiet

# Some gcloud options

gcloud projects create default
gcloud projects list
gcloud config configurations list

docker stop $(docker ps -a -q) && docker rm $(docker ps -a -q)

# Deploy web server

pub global activate webdev

# now go to the root folder of your project and do a build in release mode

flutter build web
scp -r web/
python -m http.server 8000 &
=======

## Colors

0xe6dce2

eb7a58 235 122 88

# <https://github.com/edwardinubuntu/flutter-web-dockerfile>

docker build -t trainer-app .

# Or

# <http://localhost:1200/>

 --app morning-bayou-58742

## Colors

0xe6dce2

eb7a58 235 122 88

flutter build web
wsl -- rsync -avzh --rsh='ssh -p13390' /mnt/c/Users/gt/projects/trianer/build/web/ 192.168.0.50:/home/guydegnol/projects/trianer/wedart
scp -r web/
python -m http.server 9400 &


### Procfile
web: gunicorn gettingstarted.wsgi
web: sh setup.sh && streamlit run app.py
