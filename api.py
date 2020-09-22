import time
import tornado.web
import tornado.log
import tornado.options
import logging
import json
import random

from prometheus_client import Histogram, Counter, start_http_server, REGISTRY
from prometheus_client.exposition import choose_encoder


class BaseHandler(tornado.web.RequestHandler):
    def write_json(self, obj, status_code=200):
        self.set_header("Content-Type", "application/json")
        self.set_status(status_code)
        self.write(json.dumps(obj))


class MetricsHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        encoder, content_type = choose_encoder(self.request.headers.get("accept"))
        self.set_header("Content-Type", content_type)
        self.write(encoder(REGISTRY))


REQUEST_TIME = Histogram(
    'response_time',
    'Response time (seconds)',
)

REQUEST_COUNT = Counter(
    'response_status',
    'Response status',
    labelnames=('status',)
)


class RandomHandler(BaseHandler):
    @tornado.gen.coroutine
    def get(self):
        start = time.time()
        yield tornado.gen.sleep(random.random() * 10)

        status_code = random.choice([
            200,
            200,
            200,
            200,
            200,
            200,
            200,
            300,
            300,
            300,
            400,
            400,
            500,
        ])
        end = time.time()

        REQUEST_COUNT.labels(str(status_code)).inc()
        self.write_json(None, status_code=status_code)
        REQUEST_TIME.observe(end - start)


# /listings/ping
class PingHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        self.write("pong!")


def make_app(options):
    return tornado.web.Application([
        (r"/metrics", MetricsHandler),
        (r"/", RandomHandler),
        (r"/ping", PingHandler),
    ], debug=options.debug)


if __name__ == "__main__":
    # Define settings/options for the web app
    # Specify the port number to start the web app on (default value is port 6000)
    tornado.options.define("port", default=6000)
    # Specify whether the app should run in debug mode
    # Debug mode restarts the app automatically on file changes
    tornado.options.define("debug", default=True)

    # Read settings/options from command line
    tornado.options.parse_command_line()

    # Access the settings defined
    options = tornado.options.options

    start_http_server(8000)

    # Create web app
    app = make_app(options)
    app.listen(options.port)

    logging.info("Starting listing service. PORT: {}, DEBUG: {}".format(options.port, options.debug))

    # Start event loop
    tornado.ioloop.IOLoop.instance().start()
