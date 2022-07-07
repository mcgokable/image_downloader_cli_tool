import abc
import uuid
from typing import Any, Dict, List, Optional

import requests


class ImageDownloaderException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ImageDownloader:
    def __init__(self, folder_path: str, api_url: str, api_key: str):
        self.folder_path = folder_path
        self.api_url = api_url
        self.api_key = api_key

    @abc.abstractmethod
    def get_image_data(self, query: str) -> Optional[Dict[str, Any]]:
        ...

    @abc.abstractmethod
    def get_image_urls(data: Dict[str, Any], number_of_urls: int) -> List[str]:
        ...

    def download_and_save_image(self, url: str, prefix: str = "") -> None:
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                filename = self.create_file_name(url, prefix)
                with open(f"{self.folder_path}{filename}", "wb") as f:
                    for chunk in response:
                        f.write(chunk)
        except Exception as err:
            print("Error!", err)

    def create_file_name(self, string: str, prefix: str = ""):
        filename = uuid.uuid4()
        file_extension = string.split(".")[-1]
        full_name = (
            f"{prefix}_{filename}.{file_extension}"
            if prefix
            else f"{filename}.{file_extension}"
        )
        return full_name


class PixabayImageDownloader(ImageDownloader):
    def get_image_data(self, query: str) -> Optional[Dict[str, Any]]:
        params = {"key": self.api_key, "q": query}  # check with manual url with +
        image_data = None
        try:
            response = requests.get(f"{self.api_url}", params=params)
            if response.ok:
                image_data = response.json()
            else:
                raise ImageDownloaderException(
                    f"Something went wrong. Status_code {response.status_code}."
                )
        except Exception as err:
            print("Error!", err)
        else:
            return image_data

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
    def get_image_data(self, query: str) -> Optional[Dict[str, Any]]:
        headers = {"Authorization": self.api_key}
        params = {"query": query}
        image_data = None
        try:
            response = requests.get(f"{self.api_url}", params=params, headers=headers)
            if response.ok:
                image_data = response.json()
            else:
                raise ImageDownloaderException(
                    f"Something went wrong. Status_code {response.status_code}."
                )
        except Exception as err:
            print("Error!", err)
        else:
            return image_data

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
