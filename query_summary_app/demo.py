from app.modules import parse
import os

if __name__ == '__main__':
    data_directory = os.path.join(os.path.expanduser('~'), 'Documents', 'python', 'looker', 'logs', 'query_performance')
    log_directory = os.path.join(data_directory, 'local_data')
    output_file = os.path.join(data_directory, 'data', 'test_output.csv')
    parse.logs_to_csv(log_directory, output_file, debug=True)
