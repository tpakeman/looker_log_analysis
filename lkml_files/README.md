#### Using the Looker explores
*More will be added to this in the future*

* The LookML files included create a single view and a single explore based on this table
* The explore has an `always_filter` on the `label` so you can isolate a specific upload
* `Index` is the primary key on the table. This does not come from the logfiles but is created during the upload process and auto-increments, so it is a useful proxy for the log file line number. This is useful when you want to see the next 50 or previous 50 lines, for example
  * This dimension contains a drill to see next 50 lines, previous 50 lines and 25 lines either side. The drill highlights the line you came from
* `Log level` is the logging level; one of DEBUG, INFO, WARN, ERROR or FATAL
* `Label` is the label we applied during upload
* `Source` is from the logs. I don't really know what this is :S
* `Thread` is the database thread / process 
  * There is a drill here to isolate the lines in a specific thread. The drill highlights the line you came from
* `Timestamp` is the log timestamp
* `Raw Text` is the raw text of the log line
* Some log lines contain a 'query summary' which contains detailed information about query runtimes.
  * The script here splits out the query summary and parses the individual components. They are in a seperate section in the view file
  * More information can be found on query_summary in guru.
