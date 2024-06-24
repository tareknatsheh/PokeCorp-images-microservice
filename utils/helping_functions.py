import requests
from fastapi import HTTPException
from fastapi.responses import JSONResponse

def get_pok_img_url_by_id(pokemon_id):
    res = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}")
    res = res.json()
    if "sprites" in res:
        return res["sprites"]["front_default"]
    
def store_image_in_mongodb(image_url, pokemon_id, fs):

    try:
        # first make sure that we don't already have an img for this pokemon
        if fs.exists({"filename": str(pokemon_id)}):
            file = fs.find_one({"filename": str(pokemon_id)})
            print(f"deleting: {pokemon_id}, with {file._id}")
            fs.delete(file._id)
            # raise HTTPException(status_code=400, detail=f"Image already exists for the given pokemon with id {pokemon_id}")

        response = requests.get(image_url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch image from URL.")

        image_data = response.content

        fs.put(image_data, filename=str(pokemon_id))

        return JSONResponse(content={"filename": str(pokemon_id)}, status_code=201)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))