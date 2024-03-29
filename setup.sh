mkdir -p ~/.streamlit/

echo "\
[general]
email = \"gt@guydegnol.net\"
" > ~/.streamlit/credentials.toml

echo "\
[server]
headless = true
enableCORS=false
port = 8502

[logger]
# Level of logging: 'error', 'warning', 'info', or 'debug'.
level = \"warning\"

[theme]
backgroundColor='#e6dce2'
secondaryBackgroundColor='#f5edf2'

#primaryColor='#8f2c48'
#textColor = '#581845'
font ='sans serif'
" > ~/.streamlit/config.toml