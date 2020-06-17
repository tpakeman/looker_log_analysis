# Summary
### This contains some tools for parsing and analysing Looker log files
* There are currently two main utilities in this repository:
  * `upload_to_postgres/` - A CLI to parse one or more logfiles and upload them to a Postgres database
    * `analyse_in_looker/` Contains a set of `.lkml` files that can be used to analyse this output in Looker
  * `query_summary_app/` - A Flask webapp to upload logfiles and visualise the query summary in the browser
    * The `query_summary` section of Looker's logfiles contains a detailed breakdown of how long queries take to execute, including not only database query runtimes but also the time taken for Looker to process and render the returned data.
    * This is helpful for isolating the bottleneck in slow query execution. 
    * The functions found in `query_summary_app/app/modules/parse.py` can also be used in isolation to parse logfiles and extract the query summary part

### Requirements
* Python 3.6+
* For parsing to postgres
  * `psycopg2` >=2.8
* For the webapp
  * `flask`
  * `pandas`
