from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from aiy.board import Board, Led
from aiy.leds import (Leds, Pattern, PrivacyLed, RgbLeds, Color)
from aiy.assistant.grpc import AssistantServiceClientWithLed
import cgi
import math
import time
import argparse
import locale
import logging
import signal
import sys

def volume(string):
    value = int(string)
    if value < 0 or value > 100:
        raise argparse.ArgumentTypeError('Volume must be in [0...100] range.')
    return value

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

class GP(BaseHTTPRequestHandler):
    def _set_headers(self):
	    self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_HEAD(self):
        self._set_headers()
    def do_GET(self):
        self._set_headers()
        print(self.path)
        print(parse_qs(self.path[2:]))
        self.wfile.write("<html><body><h1>Get Request Received!</h1></body></html>")
    def do_POST(self):
        self._set_headers()
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        item = form.getvalue("AI")
        print(item)
        if item == "WAKE":
            logging.basicConfig(level=logging.DEBUG)
            signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))

            parser = argparse.ArgumentParser(description='Assistant service example.')
            parser.add_argument('--language', default=locale_language())
            parser.add_argument('--volume', type=volume, default=100)
            args = parser.parse_args()

            with Board() as board:
                assistant = AssistantServiceClientWithLed(board=board,
                                                          volume_percentage=args.volume,
                                                          language_code=args.language)
                logging.info('Conversation started!')
                while True:
                # logging.info('Conversation started!')
                    assistant.conversation()
        else:
            with Leds() as leds:
                leds.update(Leds.rgb_on(Color.GREEN))
            print("Error systax to wake up AI")
def testLED():
    with Leds() as leds:
        print('RGB: Solid RED for 1 second')
        leds.update(Leds.rgb_on(Color.RED))
        time.sleep(10)

def run(server_class=HTTPServer, handler_class=GP, port=8088):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Server running at localhost:8088...')
    httpd.serve_forever()

run()