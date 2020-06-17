
### Information included
* The `time taken` (in seconds) for each step of the query execution
  * _Details of these steps and what they mean are not included here_
* The query `timestamp`
* The database thread (`process_id`) to cross reference against the rest of the logs
* The `query_source` (dashboard, api, explore, etc.)
* The `dashboard_id` (if relevant)
* The query `slug` for cross referencing against other logging tools such as the system activity model. 

---
# Demo
![Demo](flask_demo.gif)

---
## Using the Flask App
* Make sure you have the correct modules installed
* Run `app/main.py` and then access `localhost:5000`

---
## Using just the script
* This currently must be run from within python, but a CLI is a work in progress
* The simplest way to run this is to use the `logs_to_csv` function in `app/modules/parse` and pass in a directory of logfiles and a csv file for the output. Pass `debug=True` to print the progress. See an example of this in `/demo.py`

---

### Contents
* `/demo.py` contains an example script to combine and run the functions contained in `/modules`
* Everything else is saved inside `/app`:
  * `/modules`:
    * `parse.py` contains functions to parse the query_summary from the logfiles and save to 
   csv or json
    * `analyse.py` contains functions to manipulate and analyse this data in pandas.
  * `/static` and `/templates` contain the html, css and js used by the app
  * `/data` and `/uploads` are where the log data is stored during the app session
  * `/demo` contains sanitised log data to use in the demo
  * `/main.py` is the main Flask script
