import logging
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any, Dict, List, Literal, Optional

import requests

logger = logging.getLogger(__name__)
SYMBOL: Literal["█"] = "█"


class FileDownloaderException(Exception):
    def __init__(self, message):
        super().__init__(message)


class BaseFileDownloader(ABC):
    @abstractmethod
    def download_file(self, url: str) -> None:
        ...


class BaseFileSaver(ABC):
    @abstractmethod
    def save_file(self, folder_path: str, file_data: Dict[str, Any]) -> None:
        ...


class FileSaver(BaseFileSaver):
    def __init__(self, folder_path: str):
        self.folder_path = folder_path

    def save_file(self, file_data: Dict[str, Any]) -> None:
        with open(f"{self.folder_path}{file_data['file_name']}", "wb") as f:
            f.write(file_data["file_content"])


class ThreadingFileSaver(FileSaver):
    def save_file(self, future_obj) -> None:
        super().save_file(future_obj.result())


class FileDownloader(BaseFileDownloader):
    query_separator = " "
    api_url = ""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def _get_file_data(self, query: List[str]) -> Optional[Dict[str, Any]]:
        file_data = None
        try:
            response = requests.get(
                f"{self.api_url}", **self._build_request_params(query)
            )
            if response.ok:
                file_data = response.json()
            else:
                raise FileDownloaderException(
                    f"Something went wrong. Status_code {response.status_code}."
                )
        except Exception as err:
            logger.error(f"Error in time of get_file_data: {err}.")
        else:
            return file_data

    def _build_request_params(self, query: List[str]):
        return {"params": {"query": self._build_query(query)}}

    def _build_query(self, query: List[str]) -> str:
        joined_query = self.query_separator.join(query)
        return joined_query

    def download_file(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(url, stream=True)
        except Exception as err:
            logger.error(f"Error in time of downloading file: {err}.")
        else:
            logger.info("File downloads successfuly.")
            return {
                "file_content": response.content,
                "file_name": self._create_file_name(response.request.url),
            }

    def _create_file_name(self, string: str, prefix: str = "prefix") -> str:
        filename = uuid.uuid4().hex
        file_extension = string.split(".")[-1]
        full_name = (
            f"{prefix}_{filename}.{file_extension}"
            if prefix
            else f"{filename}.{file_extension}"
        )
        return full_name

    @staticmethod
    def _get_file_paths(file_data: Dict[str, Any]) -> List[str]:
        raise NotImplemented


class PixabayDownloader(FileDownloader):
    query_separator = "+"
    api_url = "https://pixabay.com/api/"

    def _build_request_params(self, query: List[str]):
        return {"params": {"key": self.api_key, "q": self._build_query(query)}}

    @staticmethod
    def _get_file_paths(file_data: Dict[str, Any], number_of_files: int) -> List[str]:
        file_paths = []
        try:
            file_paths = [
                file_data["hits"][i]["webformatURL"] for i in range(number_of_files)
            ]
        except IndexError:
            pass
        return file_paths

    def _create_file_name(self, string: str, prefix: str = "pixabay") -> str:
        return super()._create_file_name(string, prefix)


class PexelsDownloader(FileDownloader):
    api_url = "https://api.pexels.com/v1/search"

    def _build_request_params(self, query: List[str]):
        headers = {"Authorization": self.api_key}
        params = {"query": self._build_query(query)}
        return {"headers": headers, "params": params}

    @staticmethod
    def _get_file_paths(data: Dict[str, Any], number_of_files: int) -> List[str]:
        file_paths = []
        try:
            file_paths = [
                data["photos"][i]["src"]["original"] for i in range(number_of_files)
            ]
        except IndexError:
            pass
        return file_paths

    def _create_file_name(self, string: str, prefix: str = "pexels") -> str:
        return super()._create_file_name(string, prefix)


class ThreadingDownloaderSaveTool:
    total_files = 0
    downloaded_files = 0

    def __init__(self, file_downlaoder: BaseFileDownloader, file_saver: BaseFileSaver):
        self.file_downloader = file_downlaoder
        self.file_saver = file_saver

    def run(self, query: str, number_of_files: int) -> None:
        ThreadingDownloaderSaveTool.total_files = number_of_files
        file_data = self.file_downloader._get_file_data(query)
        if file_data:
            file_paths = self.file_downloader._get_file_paths(
                file_data, number_of_files
            )
            if file_paths:
                self.download_file_with_threads(file_paths)

    def download_file_with_threads(self, paths: List[str], prefix: str = "") -> None:
        with ThreadPoolExecutor(10) as pool:
            futures = [
                pool.submit(self.file_downloader.download_file, path) for path in paths
            ]
            for future in futures:
                future.add_done_callback(self.progress_bar)
                future.add_done_callback(self.file_saver.save_file)
            self.progress_bar(None)
        logger.info("Done.")

    @staticmethod
    def progress_bar(future: Future) -> None:
        percent = 100 * (
            ThreadingDownloaderSaveTool.downloaded_files
            / ThreadingDownloaderSaveTool.total_files
        )
        progress = SYMBOL * int(percent) + "-" * int(100 - percent)
        print(
            f"\r|{progress}| {percent:.2f}%  {ThreadingDownloaderSaveTool.downloaded_files}/{ThreadingDownloaderSaveTool.total_files}",
            end="\r",
        )
        ThreadingDownloaderSaveTool.downloaded_files += 1
