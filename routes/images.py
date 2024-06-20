from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import  Response
from pymongo import MongoClient
import base64
from routes.utils import *
from utils.helping_functions import get_pok_img_url_by_id, store_image_in_mongodb
import logging

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.get("/{pokemon_id}", response_class=Response)
def get_image_by_pokemon_id(
    pokemon_id: int, 
    mongo_client: MongoClient = Depends(get_mongo_client)
) -> Response:
    """Get pokemon image by pokemon id

    Args:
        pokemon_id (int): unique pokemon id

    Returns:
        Response: The image
    """
    try:
        fs = get_gridfs(mongo_client)
        file_data = fs.find_one({'filename': str(pokemon_id)})
        
        if file_data is None:
            logger.error(f"Image not found for pokemon_id: {pokemon_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        
        res_bytes = file_data.read()
        logger.info(f"Image bytes were read for pokemon_id: {pokemon_id}")
        return Response(content=res_bytes, media_type="image/jpeg")
    
    except HTTPException as http_error:
            raise http_error
    except Exception as e:
        logger.error(f"Failed getting image for pokemon_id {pokemon_id}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing image data")
    
    finally:
        mongo_client.close()
        logger.info("mongodb connection closed")
    

@router.post("/")
async def upload_image(
    pokemon_id: int = Form(...),
    filedata: str = Form(...), 
    content_type: str = Form(...),
    mongo_client: MongoClient = Depends(get_mongo_client)
    ):
    """Upload a pokemon img encoded in base64

    Args:
        pokemon_id (int, optional)
        filedata (str, optional)
        content_type (str, optional)

    Returns:
        json: upload result
    """
    try:
        logger.info(f"Got a new image, content-type is {content_type}")

        fs = get_gridfs(mongo_client)
        # to avoid duplicates, delete existing img with same name:
        image_replaced = find_and_delete(fs, pokemon_id)
        
        if image_replaced:
            logger.info(f"An older img of {pokemon_id} was found and deleted")
        else:
            logger.info(f"No previous older img was found for {pokemon_id}")

        image_bytes = str.encode(filedata)  # convert string to bytes
        img_recovered = base64.b64decode(image_bytes)  # decode base64string

        new_image_name = f"{pokemon_id}"
        fs.put(img_recovered, filename=new_image_name)

        return {
            "new_image_name": new_image_name,
            "message": "Image upload was successful" if not image_replaced else f"Old image of pokemon with id {pokemon_id} was overwritten by the new uploaded image"
        }
    
    except HTTPException as http_error:
            raise http_error
    except Exception as e:
        logger.error(f"Something went wrong with updating pokemon {pokemon_id} img in the db")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        mongo_client.close()
        logger.info("mongodb connection closed")


@router.post("/pokapi", status_code=status.HTTP_201_CREATED)
def add_pokemon_image_from_pokapi(
    pokemon_id: int,
    mongo_client: MongoClient = Depends(get_mongo_client)):
    """Update or add pokemon img from pokapi.co website

    Args:
        pokemon_id (int): id of the pokemon

    Returns:
        json: update/add result
    """
    try:
        fs = get_gridfs(mongo_client)

        img_url = get_pok_img_url_by_id(pokemon_id)
        store_result = store_image_in_mongodb(img_url, pokemon_id, fs)

        return {
            "message": f"An image for pokemon with id {pokemon_id} has been added from pokapi.co",
            "details": store_result
        }
    
    except HTTPException as http_error:
            raise http_error
    except Exception as e:
        logger.error(f"Something went wrong with updating pokemon {pokemon_id} img in the db using pokapi")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        mongo_client.close()
        logger.info("mongodb connection closed")

@router.delete("/{pokemon_id}")
def delete_pokemon_img_by_id(
     pokemon_id: int,
     mongo_client: MongoClient = Depends(get_mongo_client)):
    """Deleting image of pokemon by id

    Args:
        pokemon_id (int): unique pokemon id

    Returns:
        json: deletion result
    """
    
    try:
        logger.info(f"Deleting image of pokemon with id {pokemon_id}")

        fs = get_gridfs(mongo_client)
        done_deleting = find_and_delete(fs, pokemon_id)

        if not done_deleting:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"An image for pokemon with id {pokemon_id} not found")

        return {"message": f"Image for pokemon ID {pokemon_id} deleted successfully"}
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))