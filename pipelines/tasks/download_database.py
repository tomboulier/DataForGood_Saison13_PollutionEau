import logging
from abc import ABC, abstractmethod

from pipelines.config.config import get_s3_path
from pipelines.tasks._common import DUCKDB_FILE, download_file_from_https
from pipelines.utils.storage_client import ObjectStorageClient

logger = logging.getLogger(__name__)


class DatabaseDownloadStrategy(ABC):
    """
    Interface for database download strategies.
    """

    @abstractmethod
    def download(self, env: str, local_path: str):
        """
        Downloads the database from a specific source.

        :param env: The environment to download from ("dev" or "prod").
        :param local_path: The path where the database should be saved.
        :return: None
        """
        pass


class HTTPDownloadStrategy(DatabaseDownloadStrategy):
    """
    Strategy for downloading the database from an S3 storage,
    using HTTP instead of HTTPS.
    """

    def download(self, env: str, local_path: str):
        """
        Downloads the database from an S3 bucket.

        :param env: The environment to download from ("dev" or "prod").
        :param local_path: The path where the database should be saved.
        :return: None
        """
        logger.info(f"Downloading database from S3 in environment {env}")
        s3 = ObjectStorageClient()
        remote_s3_path = get_s3_path(env)
        s3.download_object(remote_s3_path, local_path)
        logger.info(
            f"✅ Database downloaded from s3://{s3.bucket_name}/{remote_s3_path}"
        )


class HTTPSDownloadStrategy(DatabaseDownloadStrategy):
    """
    Strategy for downloading the database via HTTPS.
    """

    def download(self, env: str, local_path: str):
        """
        Downloads the database via HTTPS.

        :param env: The environment to download from ("dev" or "prod").
        :param local_path: The path where the database should be saved.
        :return: None
        """
        logger.info("Downloading database via HTTPS")
        s3 = ObjectStorageClient()
        url = f"https://{s3.bucket_name}.{s3.endpoint_url.split('https://')[1]}/{get_s3_path(env)}"
        download_file_from_https(url=url, filepath=local_path)
        logger.info(f"✅ Database downloaded via HTTPS: {url} -> {local_path}")


class DatabaseDownloader:
    """
    Manages the database download process by selecting the appropriate strategy.
    """

    def __init__(self, strategy: DatabaseDownloadStrategy):
        """
        Initializes the database downloader with a specific strategy.

        :param strategy: The strategy to use for downloading the database.
        :return: None
        """
        self.strategy = strategy

    def download(self, env: str):
        """
        Executes the download process.

        :param env: The environment to download from ("dev" or "prod").
        :return: None
        """
        local_db_path = DUCKDB_FILE
        self.strategy.download(env, local_db_path)


def execute(env: str, use_http: bool = False):
    """
    Executes the database download using the appropriate strategy.

    :param env: The environment to download from ("dev" or "prod").
    :param use_http: Whether to download via HTTPS instead of S3. Default is False.
    :return: None
    """
    strategy = HTTPDownloadStrategy() if use_http else HTTPSDownloadStrategy()
    downloader = DatabaseDownloader(strategy)
    downloader.download(env)
