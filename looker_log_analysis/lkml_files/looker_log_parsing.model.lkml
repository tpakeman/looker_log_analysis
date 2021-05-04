connection: "postgres_logs" # You may need to change this

# include all the views
include: "looker_logs.view"

# This is static data so we can cache it forever
datagroup: looker_logs {
  sql_trigger: SELECT MAX(index) FROM looker_logs;;
  max_cache_age: "10000 hours"
}

explore: looker_logs {
  persist_with: looker_logs
  always_filter: {filters: {field: label}}
}
