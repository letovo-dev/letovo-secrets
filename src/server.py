#!/usr/bin/python

from flask import Flask, send_file, abort
import os, shutil
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

current_file_path = os.path.abspath(__file__)

app = Flask(__name__)


with open(os.path.join(current_file_path, 'src/config.json')) as config_file:
    config = json.load(config_file)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1 per minute"]
)


@app.route('/qr/<filename>', methods=['GET'])
@limiter.limit("10 per day")
def get_qr_code(filename):
    file_path = os.path.join(current_file_path, 'secret_files', filename)
    if os.path.isdir(file_path):
        subfolder = ""
        if os.path.exists(os.path.join(file_path, 'subfolder')):
            with open(os.path.join(file_path, 'subfolder'), 'r') as subfolder_file:
                subfolder = subfolder_file.read()
                if ".." in subfolder or subfolder.startswith("/"):
                    abort(403, description="have you found a bot or you just are being silly?\nanyway, go duck yourself")
            # os.remove(os.path.join(file_path, 'subfolder'))
            print(os.path.join(current_file_path, config['wiki_path'], subfolder))
            if not os.path.exists(current_file_path, os.path.join(config['wiki_path'], subfolder)):
                os.mkdir(os.path.join(current_file_path, config['wiki_path'], subfolder))

        # for file in os.listdir(config['wiki_path']):
        #     os.remove(os.path.join(config['wiki_path'], subfolder, file))

        for file in os.listdir(file_path):
            shutil.copy(os.path.join(file_path, file), os.path.join(current_file_path, config['wiki_path'], subfolder, file))
    else:
        abort(404, description="Resource not found")
    return send_file("./congrats.html")

@app.route('/')
def index():
    return "Не звоните сюда больше"

if __name__ == '__main__':
    app.run(debug=True)