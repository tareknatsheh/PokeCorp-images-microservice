
import gridfs
from pymongo import MongoClient
from decouple import config

def get_mongo_client() -> MongoClient:
    return MongoClient(str(config("MONGODB_URI")))

def get_gridfs(mongo_client: MongoClient) -> gridfs.GridFS:
    return gridfs.GridFS(mongo_client["PokeCorpDB"])

def find_and_delete(fs: gridfs.GridFS, pokemon_id: int):
    # Find the image by pokemon_id (filename)
    file = fs.find_one({"filename": str(pokemon_id)})
    if not file:
        print(f"image for {pokemon_id} was not found")
        return False
    
    print(f"deleting: {pokemon_id}, with {file._id}")
    # Delete the image using its _id
    fs.delete(file._id)
    return True