# Write a CLI tool that downloads Images by the given query and save it in given directory
# U can use whatever API u want, here is a caple that I found:
# https://www.pexels.com/ru-ru/api/documentation/?
# https://pixabay.com/api/docs/
# example:
# python script.py -q canada -n 5 --save-to canada-photos/
# where -a - query for REST API; -n - number of photos to donwload may be by defaut 1
# --save-to - folder where to save downloaded photos

import argparse
import os

from dotenv import load_dotenv

from image_downloader import PixabayImageDownloader

load_dotenv()


API_URL = "https://pixabay.com/api/"
API_KEY = os.getenv("API_KEY_PIXABAY")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from pixabay.com")
    parser.add_argument(
        "-q", action="extend", nargs="+", required=True, help="query for API"
    )
    parser.add_argument(
        "-n", help="number of images", default=1, type=int, choices=[1, 2]
    )
    parser.add_argument(
        "--save-to", type=str, required=True, help="folder for saving images"
    )
    args = parser.parse_args()
    image_downloader = PixabayImageDownloader(
        folder_path=args.save_to, api_url=API_URL, api_key=API_KEY
    )
    image_data = image_downloader.get_image_data(query=args.q)
    image_urls = (
        image_downloader.get_image_urls(image_data, args.n) if image_data else None
    )
    if image_urls:
        name_prefix = "_".join(args.q)
        for url in image_urls:
            image_downloader.download_and_save_image(url=url, prefix=name_prefix)
