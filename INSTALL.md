# FREE Installation Guide #

Navigate to your preferred folder and download the latest release of the application:

```
wget https://github.com/e-lab-FREE/FREE_Web/releases/latest/download/FREE_Web.zip 
```

Unzip the package:
```
unzip FREE_Web.zip
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
pip install -r REQUIREMENTS-STANDALONE.txt
```

Run the application:
```
daphne freeweb.asgi:application
```

By default, the webserver will be available at port 8000. To change the port, pass `-p <portnumber>` parameter to the `daphne` command.