# Framework for remote experiments in education
## Installation guide

Navigate to your preferred folder and download the latest release of the application:

```
wget https://github.com/e-lab-FREE/FREE_Web/releases/latest/download/FREE_Web_0_6_0.zip -O FREE_Web.zip
```

Unzip the package:
```
unzip -o FREE_Web.zip
```

Create a new python virtual environment, we will be calling it `free-env`.
```
virtualenv free-env
```

Activate the virtual environment:
```
source free-env/bin/activate
```

You should now see a prefix of `(free-env)` in your command line. After that, install the dependent packages:
```
pip install -r REQUIREMENTS.txt
```

The application is configured using environment variables. You can set them using the `/freeweb/.env` file. For your convenience, there is a `.env-template` file in the same folder, that you can rename to `.env` and alter the contents.

```
mv freeweb/.env-template freeweb/.env
```

**Available settings so far**

- `PROJECT_NAME`, `PROJECT_ACRONYMUM`, `SITE_NAME` - Texts that will appear in the page header
- `TIME_ZONE` - Time zone setting for tha app in `Europe/Lisbon` format.

- `FREE_PRODUCTION` - set to `on` to enable production mode (disables sensitive error messages etc.)
- `FREE_REVERSE_PROXY` - set to `on` to be able to run the FREE behind a reverse proxy
- `FREE_SECRET` - String used in hashing function. Set either to a random string of your choice, or generate one here: https://djecrety.ir 
- `FREE_ALLOWED_HOSTS` - comma separated list of domain names/addresses; only requests to these hosts will be processed by the application. This is necessary to prevent HTTP Host header attacks. More info [here](https://docs.djangoproject.com/en/3.2/topics/security/#host-headers-virtual-hosting).

- `JANUS_SERVER_ADDRESS`, `JANUS_STREAM_KEY` - Configuration of Janus video streaming server.

In future, this file will contain database configurations/passwords etc.

Right now, the application release is shipped with pre-filled example database in `sqlite` format. 

Download the database and put it into the project root:
```
wget https://github.com/e-lab-FREE/FREE_Web/releases/latest/download/db_template_0_6_0.sqlite3 -O db.sqlite3
```

This database contains a Pendulum experiment, as well as two example user accounts.

- `wp-admin` - superuser account with access to admin interface
- `wp-guest` - guest account

Both have a password `temporary123`. This password can be changed through admin interface.

Finally, run the application:
```
daphne freeweb.asgi:application
```

By default, the webserver will be available at port 8000. To change the port, pass `-p <portnumber>` parameter to the `daphne` command. You can also force binding to specific addres by `-b <address>`.

## Update guide

Follow the first two steps of the installation guide. The commands already contain overwrite switches so that the old version will be overwritten, while `.env` and `.sqlite` files won't be touched.

A new release might contain changes to the database structure. If you are preserving your database from a previous version, run
```
python manage.py migrate
```
