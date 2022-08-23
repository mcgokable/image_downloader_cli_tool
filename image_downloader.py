import logging
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from random import random
from threading import Lock
from typing import Any, Dict, List, Literal, Optional

import requests

from utils import time_me  # progress_bar, image_total, image_downloaded

logging.basicConfig(level="ERROR")
logger = logging.getLogger(__name__)

BUFFER_SIZE = 1024
lock = Lock()
image_total: int = 0
image_downloaded: int = 0
SYMBOL: Literal["█"] = "█"


class ImageDownloaderException(Exception):
    def __init__(self, message):
        super().__init__(message)


class IImageDownloader(ABC):
    @abstractmethod
    def get_image_urls(data: Dict[str, Any], number_of_urls: int) -> List[str]:
        ...

    @abstractmethod
    def get_image_data(self, query: List[str]) -> Optional[Dict[str, Any]]:
        ...

    @abstractmethod
    def build_request_params(self, query: List[str]):
        ...

    @abstractmethod
    def build_query(self, query: List[str]) -> str:
        ...

    @abstractmethod
    def download_and_save_images(self, urls: List[str], prefix: str = "") -> None:
        ...

    @abstractmethod
    def create_file_name(self, string: str, prefix: str = "") -> str:
        ...


class ImageDownloader(IImageDownloader):
    query_separator = " "
    api_url = ""

    def __init__(self, folder_path: str, api_key: str):
        self.folder_path = folder_path
        self.api_key = api_key

    def get_image_data(self, query: List[str]) -> Optional[Dict[str, Any]]:
        image_data = None
        try:
            response = requests.get(
                f"{self.api_url}", **self.build_request_params(query)
            )
            if response.ok:
                image_data = response.json()
            else:
                raise ImageDownloaderException(
                    f"Something went wrong. Status_code {response.status_code}."
                )
        except Exception as err:
            logger.error(f"Error in time of get_images_data: {err}.")
        else:
            return image_data

    def build_request_params(self, query: List[str]):
        return {"params": {"query": self.build_query(query)}}

    def build_query(self, query: List[str]) -> str:
        joined_query = self.query_separator.join(query)
        return joined_query

    def download_and_save_images(self, url: str, prefix: str = "") -> None:
        try:
            # import time
            # time.sleep(random.randint(1, 5))
            response = requests.get(url, stream=True)
            filename = self.create_file_name(response.request.url, prefix)
            with open(f"{self.folder_path}{filename}", "wb") as f:
                for data in response.iter_content(BUFFER_SIZE):
                    f.write(data)
        except Exception as err:
            logger.error(f"Error in time of downloading and saving image: {err}.")
        else:
            logger.info(f"Image {filename} saved successfuly.")

    @time_me
    def download_and_save_images_with_threads(
        self, urls: List[str], prefix: str = ""
    ) -> None:
        with ThreadPoolExecutor(10) as pool:
            pool.map(
                self.download_and_save_images, urls, [prefix for _ in range(len(urls))]
            )

    def download_and_save_images_with_progress_bar(
        self, urls: List[str], prefix: str = ""
    ) -> None:
        start = 0
        with ThreadPoolExecutor(10) as pool:
            futures = [
                pool.submit(self.download_and_save_images, *args)
                for args in zip(urls, [prefix for _ in range(len(urls))])
            ]
            for future in as_completed(futures):
                progress_bar(start, len(urls))
                start += 1

    def download_and_save_images_with_progress_bar_2(
        self, urls: List[str], prefix: str = ""
    ) -> None:
        global image_total, image_downloaded
        image_total = len(urls)
        image_downloaded = 0
        with ThreadPoolExecutor(10) as pool:
            futures = [
                pool.submit(self.download_and_save_images, *args)
                for args in zip(urls, [prefix for _ in range(len(urls))])
            ]
            for future in futures:
                future.add_done_callback(self.progress_bar)
            self.progress_bar(None)
        logger.info("Done.")

    @staticmethod  #partial
    def progress_bar(future) -> None:
        global lock, image_total, image_downloaded
        percent = 100 * (image_downloaded / image_total)
        progress = SYMBOL * int(percent) + "-" * int(100 - percent)
        # with lock:
        print(
                f"\r|{progress}| {percent:.2f}%  {image_downloaded}/{image_total}",
                end="\r",
            )
        image_downloaded += 1

    @time_me
    def download_and_save_images_normal(
        self, urls: List[str], prefix: str = ""
    ) -> None:
        for url in urls:
            self.download_and_save_images(url, prefix)

    def create_file_name(self, string: str, prefix: str = "") -> str:
        filename = uuid.uuid4().hex
        file_extension = string.split(".")[-1]
        full_name = (
            f"{prefix}_{filename}.{file_extension}"
            if prefix
            else f"{filename}.{file_extension}"
        )
        return full_name


class PixabayImageDownloader(ImageDownloader):
    query_separator = "+"
    api_url = "https://pixabay.com/api/"

    def build_request_params(self, query: List[str]):
        return {"params": {"key": self.api_key, "q": self.build_query(query)}}

    @staticmethod
    def get_image_urls(data: Dict[str, Any], number_of_urls: int) -> List[str]:
        image_urls = []
        try:
            image_urls = [
                data["hits"][i]["webformatURL"] for i in range(number_of_urls)
            ]
        except IndexError:
            pass
        return image_urls


class PexelsImageDownloader(ImageDownloader):
    api_url = "https://api.pexels.com/v1/search"

    def build_request_params(self, query: List[str]):
        headers = {"Authorization": self.api_key}
        params = {"query": self.build_query(query)}
        return {"headers": headers, "params": params}

    @staticmethod
    def get_image_urls(data: Dict[str, Any], number_of_urls: int) -> List[str]:
        image_urls = []
        try:
            image_urls = [
                data["photos"][i]["src"]["original"] for i in range(number_of_urls)
            ]
        except IndexError:
            pass
        return image_urls
