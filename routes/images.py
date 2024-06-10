import io
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pymongo import MongoClient
from decouple import config
import gridfs

router = APIRouter()

client = MongoClient(str(config("MONGODB_URI")))
cursor = client["PokeCorpDB"]
fs = gridfs.GridFS(cursor)

@router.get("/{pokemon_id}")
def get_image_by_pok_id(pokemon_id: int) -> StreamingResponse:
    """Get pokemon image by their unique id

    Returns:
        json: pokemon details
    """
    res = fs.find_one({'filename': pokemon_id})
    if not res:
            raise HTTPException(status_code=404, detail="Image not found")
    
    return StreamingResponse(io.BytesIO(res.read()), media_type="image/jpeg")

@router.post("/")
async def upload_image(pokemon_id: int, file: UploadFile = File(...)):
    try:
        image_data = await file.read()
        fs.put(image_data, filename=pokemon_id)
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))