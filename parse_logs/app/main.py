from flask import Flask, redirect, request, render_template, url_for
from werkzeug.utils import secure_filename
import os
import json
from modules import parse, analyse
from config import Config


app = Flask(__name__)
app.config.from_object(Config())


def upload_files(request_data):
    if request_data.method == 'POST':
        file_ct = 0
        for fileob in request_data.files.values():
            filename = secure_filename(fileob.filename)
            save_path = "{}/{}".format(app.config["UPLOAD_FOLDER"], filename)
            fileob.save(save_path)
            file_ct += 1
    return json.dumps({"status": "Success",
                       "status_code": 200,
                       "files_uploaded": file_ct})


def clear_uploads():
    """Deletes files from the uploads folder for the session.
        Useful for clearing down without removing data"""
    for file in os.listdir(app.config["UPLOAD_FOLDER"]):
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], file))


def clear_data():
    """Deletes files from the data folder for the session.
        Useful for clearing down without removing uploads"""
    for file in os.listdir(app.config["DATA_FOLDER"]):
        os.remove(os.path.join(app.config["DATA_FOLDER"], file))


def save_config(config, outfile):
    with open(outfile, 'w', encoding='UTF-8') as f:
        f.write(json.dumps(config))


def load_config(infile):
    with open(infile, 'r', encoding='UTF-8') as f:
        config = json.loads(f.read())
    return config


def reload_demo():
    df = analyse.load_dataframe(os.path.join(app.config["DEMO_FOLDER"], 'raw_data.json'))
    config = analyse.read_config(df, {'chartLimit': 20})
    save_config(config, os.path.join(app.config["DEMO_FOLDER"], 'config.json'))


@app.route('/', methods=["GET", "POST"])
def home():
    clear_data()
    clear_uploads()
    return render_template('home.html')


@app.route("/sendfile", methods=["POST"])
def send_file():
    r = upload_files(request)
    return r


@app.route("/sendconfig", methods=["POST"])
def send_config():
    parse.logs_to_json(app.config["UPLOAD_FOLDER"], os.path.join(app.config["DATA_FOLDER"], 'raw_data.json'), debug=True)
    demo = False
    if request.form['threadChoice'] == 'yes':
        info = parse.full_logs_to_json(app.config["UPLOAD_FOLDER"], os.path.join(app.config["DATA_FOLDER"], 'full_data.json'))
    else:
        info = {'threads': [], 'sources': []}
        demo = True
        clear_uploads()
    df = analyse.load_dataframe(os.path.join(app.config["DATA_FOLDER"], 'raw_data.json'))
    config = analyse.read_config(df, request.form)
    newconfig = {**config, **info}
    save_config(newconfig, os.path.join(app.config["DATA_FOLDER"], 'config.json'))
    return render_template('data.html', config=newconfig, demo=demo)


@app.route("/sendconfig", methods=["GET"])
def reload_data():
    config = load_config(os.path.join(app.config["DATA_FOLDER"], 'config.json'))
    return render_template('data.html', config=config, demo=False)


@app.route("/senddemo", methods=["POST"])
def load_demo():
    reload_demo() # Uncomment to refresh (useful after new functionality added)
    config = load_config(os.path.join(app.config["DEMO_FOLDER"], 'config.json'))
    return render_template('data.html', config=config, demo=True)


@app.route("/clear", methods=["GET", "POST"])
def clear():
    app.config.from_object(Config())
    # teardown()
    return redirect(url_for('home'))


@app.route("/thread/<thread_id>", methods=["GET", "POST"])
def load_thread(thread_id):
    config = load_config(os.path.join(app.config["DATA_FOLDER"], 'config.json'))
    data, _ = parse.full_logs_to_json(app.config["UPLOAD_FOLDER"],
                                      log_pattern=thread_id,
                                      outtype='return')
    thread_list = config['threads']
    return render_template("explorer.html",
                           data=data,
                           thread_list=thread_list,
                           thread_id=thread_id)


# TO DO
# @app.route("/dashboard/<dashboard_id>", methods=["GET", "POST"])
# def load_dashboard(dashboard_id):
#     config = load_config()
#     dashboard_list = None
#     data, _ = parse.full_logs_to_json(app.config["UPLOAD_FOLDER"],
#                                    log_pattern=thread_id,
#                                    outtype='return')
#     return render_template("explorer.html", data=data, dashboard_list=dashboard_list)


if __name__ == '__main__':
    app.run(debug=True)
