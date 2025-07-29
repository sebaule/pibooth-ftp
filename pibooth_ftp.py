import os
from ftplib import FTP, error_perm
import pibooth
import requests

__version__ = "1.0.0"
SECTION = "FTP"

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

    app.ftp = FTP()
    app.ftp.set_debuglevel(0)
    app.ftp.connect(host, port)
    app.ftp.login(username, password)
    try:
        app.ftp.cwd(remote_dir)
    except error_perm:
        parts = remote_dir.strip('/').split('/')
        path = ''
        for part in parts:
            path += '/' + part
            try:
                app.ftp.mkd(path)
            except error_perm:
                pass
        app.ftp.cwd(remote_dir)

@pibooth.hookimpl(trylast=True)
def state_finish_enter(cfg, app):
    gif_path = getattr(app, 'gif_path', None)
    jpg_path = getattr(app, 'previous_picture_file', None)
    upload_file = gif_path if gif_path and os.path.exists(gif_path) else jpg_path

    if not upload_file:
        app.previous_picture_url = ""
        return

    name = os.path.basename(upload_file)
    remote_path = f"{app.ftp_remote_dir.rstrip('/')}/{name}"

    # Upload FTP en binaire
    with open(upload_file, 'rb') as fp:
        app.ftp.storbinary(f'STOR {remote_path}', fp, 1024)
    app.previous_picture_url = f"{app.ftp_public_url.rstrip('/')}/{name}"

    # Réduction d'URL si activée
    if cfg.getboolean(SECTION, 'reduce_url_activated', fallback=False):
        reduce_service = cfg.get(SECTION, 'reduce_url', fallback='').strip()
        if reduce_service:
            url = app.previous_picture_url
            api_url = reduce_service.format(url=url)
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                shortened_url = response.json().get("shorturl")
                if shortened_url:
                    app.previous_picture_url = shortened_url

@pibooth.hookimpl
def pibooth_cleanup(app):
    if hasattr(app, "ftp"):
        app.ftp.quit()
