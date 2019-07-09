connection: "local_postgres"

# include all the views
include: "*.view"

datagroup: looker_logs {
  sql_trigger: SELECT MAX(index) FROM looker_logs;;
  max_cache_age: "10000 hours"
}

persist_with: looker_logs

explore: looker_logs {
  always_filter: {
    filters: {
      field: label
      value: "local_data"
    }
  }
}
