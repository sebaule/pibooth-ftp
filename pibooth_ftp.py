import os
from ftplib import FTP, error_perm
import pibooth
import requests
import logging

__version__ = "1.0.0"

SECTION = "FTP"

# Logger configuration
logging.basicConfig()
LOGGER = logging.getLogger('pibooth-ftp')
LOGGER.setLevel(logging.INFO)

@pibooth.hookimpl
def pibooth_configure(cfg):
    cfg.add_option(SECTION, 'host', '', "FTP server (ex: ftp.mysite.com)")
    cfg.add_option(SECTION, 'port', 21, "FTP port (default 21)")
    cfg.add_option(SECTION, 'username', '', "FTP login")
    cfg.add_option(SECTION, 'password', '', "FTP password")
    cfg.add_option(SECTION, 'remote_dir', '/photos', "FTP remote directory for upload")
    cfg.add_option(SECTION, 'public_url', '', "Public base URL to access photos (ex: https://mysite.com/photos)")
    cfg.add_option(SECTION, 'reduce_url_activated', False, "Activate or deactivate URL reduction")
    cfg.add_option(SECTION, 'reduce_url', 'https://is.gd/create.php?format=json&url={url}', "Service URL for reducing links (use {url} as placeholder)")

def get_ftp_cfg(cfg, key, default=None):
    return cfg.get(SECTION, key, fallback=default)

@pibooth.hookimpl
def pibooth_startup(cfg, app):
    host = get_ftp_cfg(cfg, 'host')
    port = int(get_ftp_cfg(cfg, 'port', 21))
    username = get_ftp_cfg(cfg, 'username')
    password = get_ftp_cfg(cfg, 'password')
    remote_dir = get_ftp_cfg(cfg, 'remote_dir', '/')
    app.ftp_remote_dir = remote_dir
    app.ftp_public_url = get_ftp_cfg(cfg, 'public_url')

    # FTP connection
    app.ftp = FTP()
    app.ftp.set_debuglevel(0)
    app.ftp.connect(host, port)
    app.ftp.login(username, password)
    # Create the remote directory if it does not exist
    try:
        app.ftp.cwd(remote_dir)
    except error_perm:
        # Recursive creation if the directory does not exist
        parts = remote_dir.strip('/').split('/')
        path = ''
        for part in parts:
            path += '/' + part
            try:
                app.ftp.mkd(path)
            except error_perm:
                pass  # Directory already exists
        app.ftp.cwd(remote_dir)

@pibooth.hookimpl
def state_processing_exit(cfg, app):
    # Choose the file to upload: GIF if video mode, otherwise image
    upload_file = getattr(app, 'gif_path', None)
    if upload_file and os.path.exists(upload_file):
        name = os.path.basename(upload_file)
    else:
        name = os.path.basename(app.previous_picture_file)
        upload_file = app.previous_picture_file

    remote_path = f"{app.ftp_remote_dir.rstrip('/')}/{name}"
    with open(upload_file, 'rb') as fp:
        app.ftp.storbinary(f'STOR {remote_path}', fp, 1024)
    app.previous_picture_url = f"{app.ftp_public_url.rstrip('/')}/{name}"

    # URL reduction if activated
    if cfg.getboolean(SECTION, 'reduce_url_activated', fallback=False):
        reduce_service = cfg.get(SECTION, 'reduce_url', fallback='').strip()
        if reduce_service:
            try:
                url = app.previous_picture_url
                if not url.startswith('http'):
                    LOGGER.error("Invalid URL for shortening: %s", url)
                    return

                api_url = reduce_service.format(url=url)
                response = requests.get(api_url, timeout=5)

                if response.status_code == 200:
                    shortened_url = response.json().get("shorturl")
                    if shortened_url:
                        app.previous_picture_url = shortened_url
                        LOGGER.info(f"Shortened URL: {shortened_url}")
                    else:
                        LOGGER.error("Invalid response from URL shortening service")
                else:
                    LOGGER.error(f"HTTP error during URL shortening ({response.status_code}): {response.text}")
            except Exception as e:
                LOGGER.error(f"Error during URL shortening: {e}")
        else:
            LOGGER.error("URL reduction activated but no service configured")


@pibooth.hookimpl
def pibooth_cleanup(app):
    if hasattr(app, "ftp"):
        app.ftp.quit()
