# Python: Getting Started

Alternatively, you can deploy it using this Heroku Button:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

For more information about using Python on Heroku, see these Dev Center articles:

- [Python on Heroku](https://devcenter.heroku.com/categories/python)

# Procfile
web: gunicorn gettingstarted.wsgi
web: sh setup.sh && streamlit run app.py

# Heroku
git push heroku master
heroku local

heroku ps:scale web=0
heroku ps:scale web=1
heroku restart

trianer-vetruve && git add . && git commit -m "Try fix" && git push heroku master
git add app.py && git commit -m "Try fix" && git push heroku master
heroku logs --tail
heroku builds:cache:purge -a fathomless-brook-99194  --confirm fathomless-brook-99194


killall streamlit
