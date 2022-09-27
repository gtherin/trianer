# Description

This package is dedicated to planify long races.
Data models still need to be fitted on larger pools of athletes

# Some helpers

### Procfile
web: gunicorn gettingstarted.wsgi
web: sh setup.sh && streamlit run app.py

### Heroku

To test the pckage localy
```
heroku local
```

heroku ps:scale web=0
heroku ps:scale web=1
heroku restart

trianer-push
trianer-vetruve && git add . && git commit -m "Some push" && git push heroku master
git add app.py && git commit -m "Try fix" && git push heroku master
heroku logs --tail
heroku builds:cache:purge -a fathomless-brook-99194  --confirm fathomless-brook-99194

killall streamlit

python setup.py develop
