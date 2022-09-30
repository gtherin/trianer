mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"gt@guydegnol.net\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\

[logger]\n\
# Level of logging: 'error', 'warning', 'info', or 'debug'.\n\
# Default: 'info'\n\
level = \"warning\"\n\


[theme]
backgroundColor='#e6dce2'
secondaryBackgroundColor='#f5edf2'

#primaryColor='#8f2c48'
#textColor = '#581845'
font ='sans serif'
" > ~/.streamlit/config.toml