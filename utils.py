from threading import Lock
from time import time
from typing import Any, Dict, List, Literal

lock = Lock()
image_total: int = 0
image_downloaded: int = 0
SYMBOL: Literal = "█"


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


def time_me(func):
    def wrapper(*args, **kwargs):
        start = time()
        res = func(*args, **kwargs)
        total_time = time() - start
        print(f"TIME {func.__name__}: {total_time}")
        return res

    return wrapper


# def progress_bar(current: int, total: int) -> None:
# percent = 100 * (current / float(total))
# bar = "█" * int(percent) + "-" * (100 - int(percent))
# print(f"\r|{bar}| {percent:.2f}%", end="\r")
def progress_bar(future) -> None:
    print("==============>>>", dir(future), future.result())
    global lock, image_total, image_downloaded
    print(image_total, image_downloaded)
    with lock:
        percent = 100 * (image_downloaded / image_total)
        image_downloaded += 1
        progress = SYMBOL * int(100 * percent) + "-" * int(100 - percent)
        print(f"\r|{progress}| {percent:.2f}%", end="\r", flush=True)
