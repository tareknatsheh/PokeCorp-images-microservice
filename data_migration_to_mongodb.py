from utils.helping_functions import get_pok_img_url_by_id, store_image_in_mongodb

if __name__ == "__main__":
    from decouple import config
    from pymongo import MongoClient
    import gridfs

    client = MongoClient(str(config("MONGODB_URI")))
    cursor = client["PokeCorpDB"]
    fs = gridfs.GridFS(cursor)

    for pok_id in range(1,154):
        # pok_id = 1
        print(pok_id)
        img_url = get_pok_img_url_by_id(pok_id)
        store_image_in_mongodb(img_url, pok_id, fs)



