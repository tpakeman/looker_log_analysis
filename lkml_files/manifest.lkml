project_name: "looker_log_parsing"

# Self contained
constant: log_lines {
  value: "/explore/looker_log_parsing/looker_logs?fields=looker_logs.index,looker_logs.timestamp_time,looker_logs.loglevel,looker_logs.thread,looker_logs.source,looker_logs.query&sorts=looker_logs.index&f[looker_logs.label]={{_filters['looker_logs.label']}}"
}

# Link suffix
constant: line_highlight {
  value: "&vis=%7B%22show_view_names%22%3Afalse%2C%22show_row_numbers%22%3Atrue%2C%22truncate_column_names%22%3Afalse%2C%22hide_totals%22%3Afalse%2C%22hide_row_totals%22%3Afalse%2C%22table_theme%22%3A%22editable%22%2C%22limit_displayed_rows%22%3Afalse%2C%22enable_conditional_formatting%22%3Atrue%2C%22conditional_formatting%22%3A%5B%7B%22type%22%3A%22equal+to%22%2C%22value%22%3A{{index._value}}%2C%22background_color%22%3A%22%2336b88b%22%2C%22font_color%22%3A%22%23fcf2ff%22%2C%22color_application%22%3A%7B%22collection_id%22%3A%2296e3fd5a-9632-47ab-b63f-ede29395012f%22%2C%22palette_id%22%3A%228cf23aaf-0c6e-4234-9bd9-984932b506b3%22%7D%2C%22bold%22%3Afalse%2C%22italic%22%3Afalse%2C%22strikethrough%22%3Afalse%2C%22fields%22%3A%5B%22looker_logs.index%22%5D%7D%5D%2C%22conditional_formatting_include_totals%22%3Afalse%2C%22conditional_formatting_include_nulls%22%3Afalse%2C%22type%22%3A%22table%22%7D"
}

# Link suffix
constant: queries_only {
  value: "&f[looker_logs.label]={{_filters['looker_logs.label']}}&f[looker_logs.is_query_summary]=Yes&sorts=looker_logs.index"
}

# Self contained
constant: query_summary_lines {
  value: "/explore/looker_log_parsing/looker_logs?fields=looker_logs.index,looker_logs.timestamp_time,looker_logs.thread,looker_logs.source,looker_logs.query_source,looker_logs.event,looker_logs.slug,looker_logs.dashboard_id,looker_logs.dashboard_session,looker_logs.init_avg,looker_logs.prepare_avg,looker_logs.acquire_connection_avg,looker_logs.dt_average,looker_logs.execute_sql_avg,looker_logs.postprocess_avg,looker_logs.marshalled_cache_load_avg,looker_logs.setup_avg,looker_logs.total_avg,looker_logs.unaccounted_avg,looker_logs.stream_avg,looker_logs.stream_to_cache_avg,looker_logs.stream_this_avg,looker_logs.stream_others_avg,looker_logs.cache_load_avg,looker_logs.grand_total_avg&f[looker_logs.is_query_summary]=Yes&sorts=looker_logs.index&limit=500&f[looker_logs.label]={{_filters['looker_logs.label']}}"
}
