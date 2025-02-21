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

    def __init__(self):
        super().__init__()
        self.s3 = ObjectStorageClient()

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
        remote_s3_path = get_s3_path(env)
        self.s3.download_object(remote_s3_path, local_path)
        logger.info(
            f"✅ Database downloaded from s3://{self.s3.bucket_name}/{remote_s3_path}"
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
        url = f"https://{self.s3.bucket_name}.{self.s3.endpoint_url.split('https://')[1]}/{get_s3_path(env)}"
        download_file_from_https(url=url, filepath=local_path)
        logger.info(f"✅ Database downloaded via HTTPS: {url} -> {local_path}")


class DatabaseDownloader:
    """
    Manages the database download process by selecting the appropriate strategy.
    """

    def __init__(self, strategy: DatabaseDownloadStrategy, env: str):
        """
        Initializes the database downloader with a specific strategy.

        :param strategy: The strategy to use for downloading the database.
        :param env: The environment to download from ("dev" or "prod").
        :return: None
        """
        self.strategy = strategy
        self.local_db_path = DUCKDB_FILE
        if env not in ("dev", "prod"):
            raise ValueError("'env' must be 'dev' or 'prod'")
        self.env = env

    def download(self):
        """
        Executes the download process.

        :return: None
        """
        self.strategy.download(self.env, self.local_db_path)


def execute(env: str, use_http: bool = False):
    """
    Executes the database download using the appropriate strategy.

    :param env: The environment to download from ("dev" or "prod").
    :param use_http: Whether to download via HTTPS instead of S3. Default is False.
    :return: None
    """
    strategy = HTTPDownloadStrategy() if use_http else HTTPSDownloadStrategy()
    downloader = DatabaseDownloader(strategy, env)
    downloader.download()
