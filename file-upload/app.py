"""A simple example of handling file uploads using Flask.
To test the example use the following command with custom file:
$ curl -H 'Content-Type: application/octet-stream' -X POST 127.0.0.1:5000/upload --upload-file <file>
"""
import contextlib
import os
import time
import shutil
import uuid

import flask


APP = flask.Flask('uploader')


@APP.route('/', defaults={'path': ''}, methods=['POST'])
@APP.route('/upload', methods=['POST'])
def post():
    """Get incoming stream and dump the data on filesystem.
    """
    print('A request received.')
    started_at = time.clock()

    content_type = flask.request.headers.get('Content-Type')
    if not content_type:
        err = 'Missing content type!'
        print(err)
        return err

    path = str(uuid.uuid4()) + '.import'

    try:
        with open(path, 'wb') as dst:
            shutil.copyfileobj(flask.request.stream, dst)

        print('Saved into ', path)

    except Exception as err:
        with contextlib.suppress(Exception):
            os.remove(path)

        print(err)

    "Processed in {0:f}".format(time.clock() - started_at)
    return path


if __name__ == '__main__':
    APP.run(port=5000)
