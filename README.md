# Python_React
backend is python2.7 (flask), frontend is react

This assumes you have python, pip, and mysql installed on your machine and that you’ve created an empty database for the project in mysql. All of these commands are meant to be run from the base “webapp” directory of the project in a macos terminal, but their equivalent will work if developing on another operating system.
1.	Clone the repo - git clone https://github.com/senior-full-stack/Python_React.git
2.	Create a virtual environment for the project - virtualenv venv
3.	Activate the virtual environment - . venv/bin/activate
4.	Use pip to install the project requirements - pip install -r requirements.txt
5.	In the config folder, copy production.py.default to production.py - cp config/production.py.default config/production.py
6.	Edit production.py to add your database connection string, a secret, logging instance, and logging location
7.	In the dm_app folder, copy init.py.default to init.py - cp dm_app/__init__.py.default dm_app/__init__.py
8.	In the migrations app, copy alembic.ini.default to alembic.ini - cp migrations/alembic.ini.default migrations/alembic.ini
9.	Edit alembic.ini to include your database connection string
10.	Set the system variable “APP_CONFIG_FILE” equal to “../config/production.py” You’ll probably want to add this to your bash config or profile - export APP_CONFIG_FILE=../config/production.py
11.	Create the database structure with flask migrate - python migrate.py db upgrade
12.	Run make_db_prod to populate data - python make_db_prod.py
13.	Run the app - python run.py
14.	In another terminal window, create another virtual environment to test with - virtualenv test
15.	Activate that virtual environment - . test/bin/activate
16.	Pip install the test requirements - pip install -r test-requirements.txt
17.	Run test_happy_path to verify your environment is setup correctly - py.test dm_app/tests/test_happy_path.py

