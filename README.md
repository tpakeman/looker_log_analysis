
# Upload to Postgres
![Demo](demo.gif)

## What does this do?
* This is a set of python scripts to upload a looker log file to a postgres database
  * _Postgres was chosen as it is very easy to run locally on a macbook_
  * _Instructions for setting up postgres are below_
* Also included in `lkml_files/` is a set of LookML files to analyse the looker log data with some useful drill paths to make exploring easier
* These python scripts can be run from within an IDE, or from the command line

## **Important** security considerations
* Log files do not contain raw data, but they can contain _metadata_ which may be considered sensitive or proprietary. If you intend to use this on behalf of someone else or any Looker instance you do not own, **make sure you have permission from the owner first**
* It is also a security risk to keep any log data locally for longer than is absolutely necessary.
  * Delete log files once you have finished using them
  * Use the `teardown()` functions here to remove log data from your local postgres database

## Step by step instructions
### 1. Running postgres locally (Mac OSX only)

[Good instructions here](https://www.robinwieruch.de/postgres-sql-macos-setup/)

* Check if postgres is already installed
  * `postgres --version`
* Install if necessary
  * `brew install postgres`
* Create a database
  * `initdb /usr/local/var/postgres`
* Start the postgres service (OS X)
  * `pg_ctl -D /usr/local/var/postgres start`
* Create an actual database
  * `createdb mydatabasename`
* Check postgres is running correctly by opening the SQL client inside terminal
  * `psql mydatabasename`
* [Follow the Looker setup steps here](https://docs.looker.com/setup-and-management/database-config/postgresql)
  * **Important** We will need to grant additional privileges when creating the user in this step:
    * `GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO looker;`
    * `ALTER DEFAULT PRIVILEGES FOR USER looker IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO looker;`
* `Ctrl + D` to quit the sql client

### 2. Set up your Looker instance to run the analysis

* Create a new connection in Looker to your local postgres
  * Postgres runs on `localhost:5432` by default
  * The default postgres schema is `public`
  * Use the username and password you chose during setup
* Create a new project for the log analysis
  * Copy the files included in the `/analyse_in_looker/` directory here


### 3. Run the python script to import files

* Ensure you have an installation of [python 3](https://www.python.org/downloads/)
  * Install pip - python's package manager: `sudo easy_install pip`
  * I recommend also using a virtual environment such as [`pipenv`](https://pypi.org/project/pipenv/)
* Git clone this repository
  * Install the required packages using pip or pipenv: `pip install -r requirements.txt` or `pipenv shell && pipenv install`
* There is a `config_exmaple.ini` file in this directory which contains the settings used by the script. You should duplicate this file, call it `config.ini` and change any of the defaults below:
  * `table_name`: the name of the table that will be used to store the log data. This doesn't exist yet but will be created by the script
    * _Default_ `public.looker_logs` _(It's a good idea to include the schema name here too)_
  * `host`: the address of the postgres database
    * _Default:_ `localhost`
  * `dbname`: the name of the database you created at setup
    * _Default_ `looker_logs`
  * `user`: the database user / role that you created at setup
    * * _Default_ `looker`
* Run `test.py` to see the script in action:
  * This assumes you have a log file located at `~/looker/log/looker.log` - you can customise the script to point at a different location if you want
* Call `modules.parse_files()` will write a log file to postgres:
  * `files` should be the location of a logfile or array of logfiles
  * `label` is the label to apply to this upload (useful if you want to differentiate between multiple uploads)
  * `insert=True` to insert new rows into the existing table. `False` will delete the table and start from scratch
* When you are finished, call `modules.teardown()` to delete the table specified in the config file and start again
  * Optionally pass in a label to scrub data with a specific label from the table:
    * e.g. `teardown(label='local_logs_2018')` 
* Call `modules.test_connection()` to test the config file and return `True` for a successful connection
* Call `modules.setup()` to create the table if it does not exist or tell you how many rows it already has
* Call `modules.print_labels()` to see what upload labels currently exist in the table


### 3a. Running this from the command line
  * You can run this from the command line by navigating to the directory and running `python main.py`
  * There are various arguments:
    * `--help` or `-h` will print the instructions
    * `--reset` or `-r` will delete the existing postgres table
      * This can be used in conjunction with --c or -c and a label to only remove a specific set of data
    * `--print` or `-p` will print the existing labels in the table
    * Uploading data
      * **Required** `--files` or `-f` followed by a space-separated list of files to upload
      * **Required** `--label` or `-l` to add a label
      * `--new` or `-n` to delete the table and upload from scratch. Omit this to insert into the existing table
      * `--silent` or `-s` to supress progress information. Omit this to print the upload progress.

### Some command line examples

* Upload two logfiles in the downloads folder with the label 'upload_10_07_2018' - use an existing table and print the results
  * `python main.py --files ~/Downloads/looker.log ~/Downloads/looker(1).log --label 'upload_10_07_2018'`
* Upload a logfile but delete the existing table and start again by using `--new` or `-n`
  * `python main.py -f ~/Downloads/looker.log -l 'upload_10_07_2018' --new`
* As above, but don't print the progress by using `--silent` or `-s`:
  * `python main.py -f ~/Downloads/looker.log -l 'upload_10_07_2018' -n --silent`
* Delete the whole table
  * `python main.py --reset` or `python main.py -r`
* Delete rows with the label 'local_data' from the table:
  * `python main.py -r --clear 'local_data'` or `python main.py -r -c local_data`
* Show the labels currently in the table:
  * `python main.py --print` or `python main.py -p`

### Requirements
* Python 3.6+
* For parsing to postgres
  * `psycopg2` >=2.8

---
### TO DO
* Unit tests!
  
**Upload to postgres**
* CLI
  * Add log output to stdout, but prevent if --silent passed
  * Print to command line when tearing down
  * Add a 'test' option to see the table setup status
* Functionality
  * Make the test_connection option more explicit in terms of what is working
  * Make sure the index auto-increments correctly
* Future
  * Make it possible to upload all logfiles in a directory

**Parse logs**
* Retire the webapp (needs a big refresh)
* Make the CLI for parsing more useful