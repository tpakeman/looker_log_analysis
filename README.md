# Analysing Looker logs... *in Looker!*
*(With postgres)*

### What this is for
* This is designed for people who have access to Looker logs and want to analyse and browsed them in Looker itself
* This is done by reading a log file in python and uploading it to a local postgres database, which is then connected to a Looker instance
* This is useful for Looker support staff as well as Looker customers who have access to their own log files


### **Important** security considerations

* Log files do not contain customer data, but they can contain sensitive metadata. If you intend to use this on behalf of a Looker customer or any Looker instance you do not own, **make sure you have permission from the owner first**
* It is also a security risk to keep any log data locally for longer than is absolutely necessary.
  * Delete log files once you have finished using them
  * Use the `teardown` function here to remove log data from your local postgres database


### What's in the repo
* Instructions on running a local postgres database
* Python 3 scripts to parse logfiles into postgres
* LookML files to analyse the logfiles from postgres


### Running postgres locally

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


### Set up your Looker instance to run the analysis

* Create a new connection in Looker to your local postgres
  * Postgres runs on `localhost:5432` by default
  * The default postgres schema is `public`
  * Use the username and password you chose during setup
* Create a new project for the log analysis
  * Copy the files included in the `LookML files` folder here


### Running the python script to import files

* Update the `config.json` file in this directory, to include:
  * `table_name`: the name of the table you would like to use in postgres
    * _Default_ `looker_logs`
  * `host`: the address of the postgres database
    * _Default:_ `localhost`
  * `dbname`: the name of the database you created at setup
    * _Default_ `looker_logs`
  * `user`: the database user / role that you created at setup
    * * _Default_ `looker`
* Run `main.py` to see the script in action:
  * Call `modules.parse_files` to write the logs to postgres:
    * `files` should be the location of a logfile or array of logfiles
    * `insert=True` to insert new rows into the existing table. `False` will delete the table and start from scratch
    * `label` is the label to apply to this upload (useful if you want to differentiate between multiple uploads)
    * `debug=True` will print the progress
  * When you are finished, call `modules.teardown()` to delete the table specified in the config file and start again
    * Optionally pass in a label to scrub data with a specific label from the table:
      * `teardown(label='local_logs_2018')` 
* Call `modules.test_connection()` to test the config file and return `True` for a successful connection
* Call `modules.setup()` to create the table if it does not exist or tell you how many rows it already has


### Running from the command line
  * TO DO

### Using the Looker explores
_More will be added to this_

* The `log label` always_filter lets you isolate a specific label we used when importing data
* `Index` is the primary key on the data - this iterates up for each line in the logs, so can be used as a proxy for the log line number. This is useful when you want to see the next 50 or previous 50 lines, for example
  * This contains a drill to see next 50 lines, previous 50 lines and 25 lines either side
  * The drill highlights the line you came from
* `Thread` is the database thread / process 
  * There is a drill here to isolate the lines in a specific thread
  * The drill highlights the line you came from
* The `Query summary` section contains information about individual query runtimes. 

### Requirements
* Python 3.6+
* `psycopg2`