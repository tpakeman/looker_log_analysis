
# Upload to Postgres
![Demo](demo.gif)

## What does this do?
* This is a python CLI utility to ingest a looker log file into a postgres database
  * _Postgres was chosen as it is very easy to run locally on a macbook_
  * _Instructions for setting up postgres are below_
* Also included in `lkml_files/` is a set of LookML files to analyse the looker log data with some useful drill paths to make exploring easier

## Quickstart!
* Clone this repo and set up a local postgres DB (instructions below)
* Upload every looker logfile in your downloads folder with the label 'upload_10_07_2018' - use an existing table and print the results
  * `python looker_log_analysis/main.py --files ~/Downloads/looker.log* --label 'upload_10_07_2018'`
* Upload a logfile but clear the existing table and start again by using `--new` or `-n`
  * `python looker_log_analysis/main.py -f ~/Downloads/looker.log -l 'upload_10_07_2018' --new`
* As above, but don't print the progress by using `--silent` or `-s`:
  * `python looker_log_analysis/main.py -f ~/Downloads/looker.log -l 'upload_10_07_2018' -n --silent`
* Delete the whole table
  * `python looker_log_analysis/main.py --reset` or `python looker_log_analysis/main.py -r`
* Delete rows with the label 'local_data' from the table:
  * `python looker_log_analysis/main.py -r --clear 'local_data'` or `python looker_log_analysis/main.py -r -c local_data`
* Show the labels currently in the table:
  * `python looker_log_analysis/main.py --print` or `python looker_log_analysis/main.py -p`

---

## ⚠️ **Important** security considerations ⚠️
* Log files do not contain raw data, but they can contain _metadata_ which may be considered sensitive or proprietary. If you intend to use this on behalf of someone else or any Looker instance you do not own, **make sure you have permission from the owner first**
* It is also a security risk to keep any log data locally for longer than is absolutely necessary.
  * Delete log files once you have finished using them
  * Use `main.py --reset` to drop the table from the CLI or call the `db.teardown()` function directly within python

---

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
    * *NOTE - this should match the 'Connection' configuration in your config file*
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
  * Copy the files included in the `lkml_files/` directory here


### 3. Set up python and customise the config

* Ensure you have an installation of [python 3](https://www.python.org/downloads/)
  * Install pip - python's package manager: `sudo easy_install pip`
  * I recommend also using a virtual environment such as [`pipenv`](https://pypi.org/project/pipenv/)
* Git clone this repository
  * Install the required packages using pip or pipenv: `pip install -r requirements.txt` or `pipenv shell && pipenv install`
* There is a `config_example.ini` file in this directory which contains the settings used by the script. Duplicate this file and call it `config.ini`
  * Explanations of each configuration section are explained below

### 4. Run from the command line
  * You can run this from the command line by navigating to the parent directory and running `python looker_log_analysis/main.py`
  * There are various arguments:
    * `--help` or `-h` will print the instructions
    * `--reset` or `-r` will delete the existing postgres table
      * This can be used in conjunction with `--clear` or `-c` and a label to only remove a specific set of data
    * `--print` or `-p` will print the existing labels in the table and the number of rows that exist
    * Uploading data
      * **Required** `--files` or `-f` followed by a space-separated list of files to upload
      * **Required** `--label` or `-l` to add a label
      * `--new` or `-n` to delete the table and upload from scratch. Omit this to insert into the existing table
      * `--silent` or `-s` to supress progress information. Omit this to print the upload progress.

---

## Requirements
* Python 3.6+
* For parsing to postgres
  * `psycopg2` >=2.8

---

## Configuration
  * `host`: the address of the postgres database
    * _Default:_ `localhost`
  * `dbname`: the name of the database you created at setup
    * _Default_ `looker_logs`
  * `user`: the database user / role that you created at setup
    * _Default_ `looker`
  * `password`: the database user password that you created at setup
    * _Default_ `looker` - change this!
  * `table_name`: the name of the table that will be used to store the log data. This doesn't exist yet but will be created by the script
    * _Default_ `public.looker_logs` _(It's a good idea to include the schema name here too)_
  * `log_directory`: the directory where any application logs will be saved. They will also be printed to stdout
    * _Default_ `log` _(If you change this then make sure you add the new directory to your `.gitignore` file to avoid bloating this repo)_
  * `log_name` Filename for application log files
    * _Default_ `Looker Log Parsing`
  * `check_interval`: How many lines should be inserted before progress is printed
    * _Default_ `50000`
  * `commit_interval`: How many insert statements should be processed by the cursor before the connection commits them
    * _Default_ `100`
  * `statements_per_insert`: How many rows should each SQL `INSERT` statement contain
    * _Default_ `1000`

