### TO DO
* Consider deploying as cloud service?
* Unit tests
  * Use mocks for connection objects
* Improve parsing coverage to reduce skipped lines
* Bugs
  * Counts don't exactly matched inserted rows 
* Features
  * CLI
    * Add log output to stdout, but prevent if --silent passed
    * Print to command line when tearing down
    * Print command should show row counts and date of last upload
    * Add a 'test' option to see the table setup status and check connectivity
  * Make the test_connection option more explicit in terms of what is working
  * Make sure the index auto-increments correctly
* Future
  * Make it possible to upload all logfiles in a directory
