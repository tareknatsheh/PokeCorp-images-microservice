import sys
sys.path.append('D:/backend-bootcamp/Final project/PokeCorp-images-microservice')  # Adjust the path as necessary

from utils.helping_functions import get_pok_img_url_by_id, store_image_in_mongodb


if __name__ == "__main__":
    from pymongo import MongoClient
    import gridfs

    client = MongoClient("mongodb://localhost:27018/")
    cursor = client["PokeCorpDB"]
    fs = gridfs.GridFS(cursor)

    # for pok_id in range(1,101):
    #     # pok_id = 1
    #     print(pok_id)
    #     img_url = get_pok_img_url_by_id(pok_id)
    #     store_image_in_mongodb(img_url, pok_id, fs)
    img_url = get_pok_img_url_by_id(140)
    store_image_in_mongodb(img_url, 140, fs)

