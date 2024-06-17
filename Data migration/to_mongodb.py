from tokenize import PlainToken
from fastapi.responses import JSONResponse
import requests
from fastapi import HTTPException
from pymongo import MongoClient
import gridfs
import base64

client = MongoClient("mongodb://localhost:27018/")
cursor = client["PokeCorpDB"]
fs = gridfs.GridFS(cursor)

def store_image_in_mongodb(image_url, pokemon_id):

    try:
        # first make sure that we don't already have an img for this pokemon
        if fs.exists({"filename": str(pokemon_id)}):
            raise HTTPException(status_code=400, detail=f"Image already exists for the given pokemon with id {pokemon_id}")

        # Fetch the image from the URL
        response = requests.get(image_url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch image from URL.")

        image_data = response.content

        # Convert the image to base64
        encoded_image = base64.b64encode(image_data).decode('utf-8')

        # Store the image in GridFS
        fs.put(base64.b64decode(encoded_image), filename=str(pokemon_id))

        return JSONResponse(content={"filename": str(pokemon_id)}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def get_pok_img_url_by_id(pokemon_id):
    res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
    res = res.json()
    if "sprites" in res:
        return res["sprites"]["front_default"]

if __name__ == "__main__":
    for pok_id in range(1,101):
        # pok_id = 1
        print(pok_id)
        img_url = get_pok_img_url_by_id(pok_id)
        store_image_in_mongodb(img_url, pok_id)

