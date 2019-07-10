# Analysing Looker logs... *in Looker!*
*(With postgres)*

### What does this do?
* This is a set of python scripts to upload a looker log file to a postgres database
  * _Postgres was chosen as it is very easy to run locally on a macbook_
  * _Instructions for setting up postgres are below_
* Also included is a set of LookML files to analyse the looker log data with some useful drill paths to make exploring easier
* These python scripts can be run from within an IDE, or from the command line


### **Important** security considerations

* Log files do not contain raw data, but they can contain _metadata_ which may be considered sensitive or proprietary. If you intend to use this on behalf of someone else or any Looker instance you do not own, **make sure you have permission from the owner first**
* It is also a security risk to keep any log data locally for longer than is absolutely necessary.
  * Delete log files once you have finished using them
  * Use the `teardown()` functions here to remove log data from your local postgres database


### What's in the repo
* Instructions on running a local postgres database and connecting it to Looker
* Python 3 scripts to parse logfiles into postgres and instructions for running this from the command line
* LookML files to analyse the logfiles from postgres


---

### 1. Running postgres locally

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
* Create a new user called `looker`
  * `CREATE USER looker;`
* `Ctrl + D` to quit the sql client


### 2. Set up your Looker instance to run the analysis

* Create a new connection in Looker to your local postgres
  * Postgres runs on `localhost:5432` by default
  * The default postgres schema is `public`
  * Use the username and password you chose during setup
* Create a new project for the log analysis
  * Copy the files included in the `LookML files` folder here


### 3. Run the python script to import files

* Update the `config.json` file in this directory, to include:
  * `table_name`: the name of the table you would like to use in postgres
    * _Default_ `looker_logs`
  * `host`: the address of the postgres database
    * _Default:_ `localhost`
  * `dbname`: the name of the database you created at setup
    * _Default_ `looker_logs`
  * `user`: the database user / role that you created at setup
    * * _Default_ `looker`
* Run `test.py` to see the script in action:
  * Call `modules.parse_files()` will write a log file to postgres:
    * `files` should be the location of a logfile or array of logfiles
    * `label` is the label to apply to this upload (useful if you want to differentiate between multiple uploads)
    * `insert=True` to insert new rows into the existing table. `False` will delete the table and start from scratch
    * `debug=True` will print the progress
  * When you are finished, call `modules.teardown()` to delete the table specified in the config file and start again
    * Optionally pass in a label to scrub data with a specific label from the table:
      * e.g. `teardown(label='local_logs_2018')` 
* Call `modules.test_connection()` to test the config file and return `True` for a successful connection
* Call `modules.setup()` to create the table if it does not exist or tell you how many rows it already has
* Call `modules.print_labels()` to see what upload labels currently exist in the table


### 3a. Running this from the command line
  * You can run this from the command line by running `python main.py` in the appropriate directory.
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

### Using the Looker explores
_More will be added to this in the future_

* The LookML files included create a single view and a single explore based on this table
* The explore has an `always_filter` on the `label` so you can isolate a specific upload
* `Index` is the primary key on the table. This does not come from the logfiles but is created during the upload process and auto-increments, so it is a useful proxy for the line number in the log files. This is useful when you want to see the next 50 or previous 50 lines, for example
  * This dimension contains a drill to see next 50 lines, previous 50 lines and 25 lines either side. The drill highlights the line you came from
* `Thread` is the database thread / process 
  * There is a drill here to isolate the lines in a specific thread. The drill highlights the line you came from
* The `Query summary` section contains information about individual query runtimes.
  * More information on this can be found in guru

### Requirements
* Python 3.6+
* `psycopg2`