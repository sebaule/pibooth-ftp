

pibooth-ftp
===========

|PythonVersions| |PypiPackage| |Downloads|

``pibooth-ftp`` is a plugin for the `pibooth`_ application.

Its permits to upload the pictures to a `ftp server`. It requires an
internet connection.

Install
-------

    $ pip3 install pibooth-ftp

Configuration
-------------

Here below the new configuration options available in the `pibooth`_ configuration.
**The keys and their default values are automatically added to your configuration after first** `pibooth`_ **restart.**

.. code-block:: ini

    [FTP]
    # FTP server (ex: ftp.mysite.com)
    host = ftp.mysite.com

    # FTP Port (Default 21)
    port = 21

    # Login identifier
    username = mylogin

    # Connection Password
    password = mypassword

    # Remote directory to upload photos (e.g., /photos)
    remote_dir = /photos

    # Public URL to access photos (e.g., https://mysite.com/photos)
    public_url = https://mysite.com/photos

    # Activate or deactivate URL shortening (True or False)
    reduce_url_activated = True

    # URL shortening service (must contain {url})
    reduce_url = https://is.gd/create.php?format=json&url={url}


.. note:: Edit the configuration by running the command ``pibooth --config``.



Exemple d'installation du serveur FTP & HTTP
-------
Proposition d'un serveur FTP et Web simple :
- Vsftp
    https://security.appspot.com/vsftpd/vsftpd_conf.html
- Nginx
    https://nginx.org/en/docs/

Serveur FTP : Upload des images
Serveur Web : téléchargement des images

Cinématique :
-------
**pibooth --> serveur FTP :**

    ftp://<login>:<Motdepasse>@<monip>
    dépôt de l'image dans /home/ftpuser/photos

**Utilisateur (smartphone) --> serveur Web  :**

    http(s)://<monip>/photos
    Téléchargement automatique de l'image

Interdiction aux utilisateurs de pouvoir visualiser les autres images qui se trouvent sur le severur (à côté de celle téléchargée)

Déroulez les commandes suivantes sur Debian 12
-------
**Installation serveur FTP : VSFTPD**

    sudo apt-get update
    sudo apt-get upgrade

    sudo apt-get install -y vsftpd


    sudo adduser ftpuser
    sudo passwd ftpuser
    sudo mkdir /home/ftpuser/photos
    sudo chown ftpuser:www-data /home/ftpuser/photos
    sudo chown ftpuser:www-data /home/ftpuser/photos/*

    sudo chmod o+x /home
    sudo chmod o+x /home/ftpuser
    sudo chmod 755 /home/ftpuser/photos
    sudo chmod 644 /home/ftpuser/photos/*



    sudo nano /etc/vsftpd.conf

Y configurer ces valeurs :

    listen=NO
    listen_ipv6=YES
    anonymous_enable=YES
    local_enable=YES
    write_enable=YES
    local_umask=022
    anon_upload_enable=NO
    anon_mkdir_write_enable=NO
    anon_other_write_enable=NO
    anon_root=/home/ftpuser/photos
    dirmessage_enable=YES
    use_localtime=YES
    xferlog_enable=YES
    connect_from_port_20=YES
    chroot_local_user=YES
    allow_writeable_chroot=YES
    pam_service_name=vsftpd
    rsa_cert_file=/etc/ssl/certs/ssl-cert-snakeoil.pem
    rsa_private_key_file=/etc/ssl/private/ssl-cert-snakeoil.key
    ssl_enable=NO
    no_anon_password=YES
    dirlist_enable=YES
    hide_file={*}


        
**Installation serveur Web : NGINX**

    sudo apt update
    sudo apt install nginx
    sudo ln -s /home/ftpuser/photos /var/www/photos
    sudo nano /etc/nginx/sites-available/default

indiquer la configuration suivante : 

    server {
            listen 80 default_server;
            listen [::]:80 default_server;

            add_header X-Frame-Options "SAMEORIGIN";
            add_header X-Content-Type-Options "nosniff";
            add_header X-XSS-Protection "1; mode=block";
            add_header Content-Security-Policy "default-src 'self';";

            root /var/www;

            index index.html index.htm;

            server_name _;

            location /photos/ {
                    autoindex off;
                    # First attempt to serve request as file, then
                    # as directory, then fall back to displaying a 404.
                    #try_files $uri $uri/ =404;
                    try_files $uri =404;
                    add_header Content-Disposition 'attachment';
            }

            location / {
                    return 403;
            }

    }

    
**Aide au debug**

Pour visualiser les erreurs : 

    sudo /usr/sbin/vsftpd /etc/vsftpd.conf

Tester la configuration de nginw :

    sudo nginx -t
