import typing
from typing import Any, Dict, List


def get_image_urls_from_pixabay(data: Dict[str, Any], number_of_urls: int) -> List[str]:
    image_urls = []
    try:
        image_urls = [data["hits"][i]["webformatURL"] for i in range(number_of_urls)]
    except IndexError:
        pass
    return image_urls


def get_image_urls_from_pexels(data: Dict[str, Any], number_of_urls: int) -> List[str]:
    image_urls = []
    try:
        image_urls = [
            data["photos"][i]["src"]["original"] for i in range(number_of_urls)
        ]
    except IndexError:
        pass
    return image_urls
