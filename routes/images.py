from fastapi import APIRouter, File, Form, HTTPException, status
from fastapi.responses import  Response
from pymongo import MongoClient
from decouple import config
import gridfs
import base64
from routes.utils import find_and_delete

router = APIRouter()

client = MongoClient(str(config("MONGODB_URI")))
cursor = client["PokeCorpDB"]
fs = gridfs.GridFS(cursor)


@router.get("/{pokemon_id}", response_class=Response)
def get_image_by_pokemon_id(pokemon_id: int):
    """Get pokemon image by their unique id and return as JPEG image"""
    res = fs.find_one({'filename': f"{pokemon_id}"})
    # res = fs.find_one({})
    print(res)
    if not res:
        raise HTTPException(status_code=404, detail="Image not found")
    
    res_bytes = res.read()
    return Response(content=res_bytes, media_type="image/jpeg")
    

@router.post("/")
async def upload_image(pokemon_id: int = Form(...), filedata: str = Form(...),  content_type: str = Form(...)):
    try:
        print("Got a call!")
        print(f"cont type: {content_type}")

        del_res = find_and_delete(fs, pokemon_id)

        image_as_bytes = str.encode(filedata)  # convert string to bytes
        img_recovered = base64.b64decode(image_as_bytes)  # decode base64string

        new_image_name = f"{pokemon_id}"
        fs.put(img_recovered, filename=new_image_name)

        return {
            "new_image_name": new_image_name,
            "message": "Image upload was successful" if not del_res else f"Old image of pokemon with id {pokemon_id} was overwritten by the new uploaded image"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/images/{pokemon_id}")
def delete_pokemon_img_by_id(pokemon_id: int):
    print(f"Deleting image of pokemon with id {pokemon_id}")
    try:
        done_deleting = find_and_delete(fs, pokemon_id)
        if not done_deleting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An image for pokemon with id {pokemon_id} not found")

        return {"message": f"Image for pokemon ID {pokemon_id} deleted successfully"}
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))