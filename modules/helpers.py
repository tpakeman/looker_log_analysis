def estimate_size(files, log):
    """Perform a rough count of all lines in a set of files"""
    est = sum(sum(1 for _ in open(file, 'rb')) for file in files)
    log.info(f"Approx. {est:,} log lines will be parsed")
    return est