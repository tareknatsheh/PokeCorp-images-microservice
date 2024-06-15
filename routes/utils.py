
from gridfs import GridFS

def find_and_delete(fs: GridFS, pokemon_id: int):
    # Find the image by pokemon_id (filename)
    file = fs.find_one({"filename": str(pokemon_id)})
    if not file:
        print(f"image for {pokemon_id} was not found")
        return False
    
    print(f"deleting: {pokemon_id}, with {file._id}")
    # Delete the image using its _id
    fs.delete(file._id)
    return True