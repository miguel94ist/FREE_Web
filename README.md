# Framework for remote experiments in education

## Installation

**-----  Unstructured, will be polished gradually. -----**

Install Python 3+.

Checkout the git repository into a directory. Create a python virtual environment (let's call it `free-env`):
```
virtualenv free-env
```

This will create a new directory `free-env`. Then, active the environment:
```
source free-env/Scripts/activate
```
or
```
free-env/Scripts/activate.bat
```

The environment activation should be apparent by seeing `(free-env)` as a prefix of the command line. **From now on, all commands are assumed to be executed within the virtual environment**.

Install python's dependent packages:
```
pip install -r REQUIREMENTS.txt
```

*TODO: Configure DB*

Configure available languages for translation by setting `LANGUAGES` constant in `freeweb/settings.py`. The template is:
```
LANGUAGES = [
    ('en', _('English')),
    ('pt', _('Portugese')),
]
```

If you increase the set of available languages, make sure you provide translations for applications' strings (described in the *Development guidelines* below).

If using SQLite as database, enable JSONField extension as described here: https://code.djangoproject.com/wiki/JSON1Extension

After the database is configured, we need to initialize it:
```
python manage.py migrate
```

Create a superuser for administrative access:
```
python manage.py createsuperuser
```

Compile translation files:
```
cd free
django-admin compilemessages
```

The application is configured with environment variables stored in the deployment environment in the `.env` file. Template for this file is in the `deploy\` directory. Fill in the individual configuration items, rename the file to `.env` and place it into the `freeweb\` directory.

Install Node.js (https://nodejs.org/en/) and Yarn (https://yarnpkg.com/getting-started/install)
Navigate into `free/assets` folder and run:
```
yarn install
```

This should download all javascript dependencies for the project. 


After all this, you can run the django development webservery with:
```
python manage.py runserver
```

In the production environment, the application should be bound to a production webserver using the WSGI interface.

## Development guidelines

When adding python library, please update the `REQUIREMENTS.txt` file by running:

```
pip freeze > REQUIREMENTS.txt
```

After any changes were made to texts displayed in the application, regenerate translation files:
```
cd free
django-admin makemessages -a
```

To execute this command, you need to have gettext installed. See https://mlocati.github.io/articles/gettext-iconv-windows.html

In `free/locale/<lang_code>` you should be able to see `.po` files containing strings extracted from the source code. Translate those strings. After changes to `.po` files run compilation (also in `free` directory):
```
django-admin compilemessages
```

This will create `.mo` files that will be used for translating strings in-app.

*TODO: Javascript internationalisation*

If any changes to API definition is made, the OpenAPI `.yml` schema needs to be regenerated:
```
python manage.py generateschema --file free-openapi-schema.yml
```

This `.yml` file can be then imported to https://editor.swagger.io or other API documentation generator tool. 