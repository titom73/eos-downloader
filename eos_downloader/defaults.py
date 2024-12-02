"""Default values for eos_downloader"""

DEFAULT_REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Chrome/123.0.0.0",
}
DEFAULT_SOFTWARE_FOLDER_TREE = (
    "https://www.arista.com/custom_data/api/cvp/getFolderTree/"
)

DEFAULT_DOWNLOAD_URL = "https://www.arista.com/custom_data/api/cvp/getDownloadLink/"

DEFAULT_SERVER_SESSION = "https://www.arista.com/custom_data/api/cvp/getSessionCode/"
