import time
import tornado.web
import tornado.log
import tornado.options
import logging
import random

from prometheus_client import REGISTRY
from prometheus_client.exposition import choose_encoder


class MetricsHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        encoder, content_type = choose_encoder(
            self.request.headers.get("accept")
        )
        self.set_header("Content-Type", content_type)
        self.write(encoder(REGISTRY))


class RandomHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        start = time.time()
        yield tornado.gen.sleep(random.random())

        status_code = random.choice([
            200, 200, 200, 200, 200, 200, 200,
            300, 300, 300, 300,
            400, 400,
            500,
        ])
        self.set_status(status_code)
        end = time.time()
        time_taken = end - start


def make_app(options):
    return tornado.web.Application([
        (r"/metrics", MetricsHandler),
        (r"/", RandomHandler),
    ], debug=options.debug)


if __name__ == "__main__":
    # Define settings/options for the web app
    # Specify the port number to start the web app on
    tornado.options.define("port", default=6000)
    # Specify whether the app should run in debug mode
    # Debug mode restarts the app automatically on file changes
    tornado.options.define("debug", default=True)

    # Read settings/options from command line
    tornado.options.parse_command_line()

    # Access the settings defined
    options = tornado.options.options

    # Create web app
    app = make_app(options)
    app.listen(options.port)

    logging.info("Starting app. PORT: {}, DEBUG: {}".format(
        options.port, options.debug)
    )

    # Start event loop
    tornado.ioloop.IOLoop.instance().start()
