# Write a CLI tool that downloads Images by the given query and save it in given directory
# U can use whatever API u want, here is a caple that I found:
# https://www.pexels.com/ru-ru/api/documentation/?
# https://pixabay.com/api/docs/
# example:
# python script.py -q canada -n 5 --save-to canada-photos/
# where -a - query for REST API; -n - number of photos to donwload may be by defaut 1
# --save-to - folder where to save downloaded photos
# --source  - a source for uploading images(possible choices: pexels, pixabay)

import argparse
import os

from dotenv import load_dotenv

from image_downloader import PexelsImageDownloader, PixabayImageDownloader

load_dotenv()

IMAGE_DOWNLOADERS = {"pixabay": PixabayImageDownloader, "pexels": PexelsImageDownloader}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download images from pixabay.com")
    parser.add_argument(
        "-q", action="extend", nargs="+", required=True, help="query for API"
    )
    parser.add_argument("-n", help="number of images", default=1, type=int)
    parser.add_argument(
        "--save-to", type=str, required=True, help="folder for saving images"
    )
    parser.add_argument("--source", choices=["pixabay", "pexels"], required=True)
    args = parser.parse_args()
    api_key = os.getenv(f"API_KEY_{args.source.upper()}")
    api_url = os.getenv(f"API_URL_{args.source.upper()}")
    image_downloader = IMAGE_DOWNLOADERS[args.source](
        folder_path=args.save_to, api_key=api_key
    )
    image_data = image_downloader.get_image_data(query=args.q)
    image_urls = (
        image_downloader.get_image_urls(image_data, args.n) if image_data else None
    )
    if image_urls:
        name_prefix = f"{args.source}_" + "_".join(args.q)

        image_downloader.download_and_save_images_with_threads(image_urls, name_prefix)
        image_downloader.download_and_save_images_normal(image_urls, name_prefix)
