"""A simple example of handling large file downloads using Flask + Gevent
in nonblocking manner.

To test the example prepare the test data:
a. Create the 'static' folder in the projects root.
b. Put a large file (e.g. ~5Gb) called test-data into it.

Now you can download the test data from one terminal, e.g.:
$ curl -w "\n%{time_total}" -X GET 127.0.0.1:5000/download --output result

and verify that the server is not blocked from another, e.g.:
$ curl -w "\n%{time_total}" -X GET 127.0.0.1:5000/ping
"""

from gevent import monkey
monkey.patch_all()

import sys

import flask
from gevent.fileobject import FileObjectThread
from gevent.pywsgi import WSGIServer

APP = flask.Flask('gevent-downloader')


def file_stream(path, chunk_size=16*1024*1024):
    with open(path, 'rb') as src:
        wrapper = FileObjectThread(src, 'rb')

        while True:
            data = wrapper.read(chunk_size)
            if not data:
                return

            yield data


@APP.route('/download', methods=['GET'])
def download():
    print('Starting download...')

    return flask.Response(
        flask.stream_with_context(file_stream('./static/test-data')),
        headers={'Content-Length': 12001017856},
        content_type='application/octet-stream',
        direct_passthrough=True,
    )


@APP.route('/ping', methods=['GET'])
def ping():
    print('Ping-pong')

    return 'Pong'


def main():
    try:
        APP.config.from_object('config')

        server = WSGIServer(('0.0.0.0', 5000,), APP.wsgi_app)

        print('Ready to serve, my master!')
        server.serve_forever()

    except KeyboardInterrupt:
        pass

    return 0


if __name__ == '__main__':
    sys.exit(main())
