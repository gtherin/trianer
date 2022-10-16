

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import UploadFile, File, Cookie
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from starlette.responses import StreamingResponse


app = FastAPI()

# http://127.0.0.1:5000
@app.get('/')
def home():
    return {'hello': 'world'}

# http://127.0.0.1:5000/search?q=EFegzeg
@app.get('/search')
def search(q: str):
    return {'query': q}

# http://127.0.0.1:5000/lowercase?json_data={"a": "b", "text": "egzegz"}
@app.post('/lowercase')
def lower_case(json_data: Dict):
    text = json_data.get('text')
    return {'text': text.lower()}

@app.post('/upload')
def upload_file(file: UploadFile = File(...)):
    return {'name': file.filename}


@app.get('/profile')
def profile(name = Cookie(None)):
    """This func is useless
    """
    return {'name': name}



# http://127.0.0.1:5000/graph/blue
@app.get("/graph/{id_file}", name="Return the graph obtained")
async def create_graph(id_file: str):

    # Data for plotting
    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2 * np.pi * t)

    fig, ax = plt.subplots()
    ax.plot(t, s)

    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
        title='About as simple as it gets, folks')
    ax.grid()

    graph = fig
    # create a buffer to store image data
    buf = BytesIO()
    graph.savefig(buf, format="png")
    buf.seek(0)
        
    return StreamingResponse(buf, media_type="image/png")

if __name__ == '__main__':
    uvicorn.run(app)
