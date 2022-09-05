from dependency_injector import containers, providers

from file_downloader import (PexelsDownloader, PixabayDownloader,
                             ThreadingDownloaderSaveTool, ThreadingFileSaver)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    pixabay_downloader = providers.Factory(
        PixabayDownloader,
        api_key=config.api_key,
    )
    pexels_downloader = providers.Factory(
        PexelsDownloader,
        api_key=config.api_key,
    )
    downloader = providers.Selector(
        config.source,
        pixabay=pixabay_downloader,
        pexels=pexels_downloader,
    )
    threading_saver = providers.Factory(
        ThreadingFileSaver,
        folder_path=config.save_to,
    )
    download_save_tool = providers.Factory(
        ThreadingDownloaderSaveTool,
        file_downlaoder=downloader,
        file_saver=threading_saver,
    )
