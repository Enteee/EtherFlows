#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import time 
import sys
import json
import argparse
import xml.sax
import socket
import os
import functools
import pprint
import datetime
import pytz
import netifaces
import signal 
import struct
import binascii
from threading import Thread

DATA_MAXLEN = 200
DATA_TOO_LONG = 'Data too long'
STANDALONE = False
DEBUG = False
HOSTNAME=socket.gethostname()
KIBANA_NOT_SUPPORTED_CHARS = '_'
LOGSTASH_CONNECT_PORT = '5000'
LOGSTASH_CONNECT = '127.0.0.1:{}'.format(LOGSTASH_CONNECT_PORT)
BROADCAST_MAC = 'FF:FF:FF:FF:FF:FF'
TIMEZONE = pytz.timezone(time.tzname[0])

# Main thread is running
running = True

parser = argparse.ArgumentParser(description='Flowworker')

parser.add_argument('-i',
                    required=True,
                    type=str,
                    dest='interface',
                    help='Interface to listen on'
                    )
parser.add_argument('-S',
                    default=STANDALONE,
                    dest='standalone',
                    action='store_true',
                    help='Enable standalone mode'
                    )
parser.add_argument('-m',
                    default=BROADCAST_MAC,
                    dest='broadcast_mac',
                    help='Flow generator broadcast address'
                   )
parser.add_argument('-l',
                    default=DATA_MAXLEN,
                    type=int,
                    dest='data_maxlen',
                    help='Maximum lenght of data in tshark pdml-field [default: {}]'.format(DATA_MAXLEN)
                    )
parser.add_argument('-d',
                    default=DEBUG,
                    dest='debug',
                    action='store_true',
                    help='Debug mode'
                    )
parser.add_argument('-L',
                    default=LOGSTASH_CONNECT,
                    dest='logstash_connect',
                    help='Logstash receiver in the format HOSTNAME[:PORT] [default: {}]'.format(LOGSTASH_CONNECT)
                    )

class AutoVivification(dict):
    """
    Implementation of perl's autovivification feature.
    see: https://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python
    """
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

class PdmlHandler(xml.sax.ContentHandler):
    def __init__(self, worker):
        self.__worker = worker
        self.frame = {}

    def boolify(self, s):
        if s == 'True':
            return True
        if s == 'False':
            return False
        raise ValueError('Not a bool')

    # Try to convert variables into datatypes
    def autoconvert(self, s):
        for fn in (self.boolify, int, float):
            try:
                return fn(s)
            except ValueError:
                pass
        return s

    # Call when an element starts
    def startElement(self, tag, attributes):
        if tag == 'packet':
            self.__frame = AutoVivification()
        else:
            if 'name' in  attributes:
                name = attributes.getValue('name')
                # kibana does not support some characters at beginning of strings
                try:
                    while name[0] in KIBANA_NOT_SUPPORTED_CHARS:
                        name = name[1:]
                except IndexError:
                    pass
                if len(name) > 0:
                    # Build object tree
                    name_access = functools.reduce(lambda x,y: x[y], [self.__frame] + name.split('.'))
                    if(not isinstance(name_access, dict)):
                        return;
                    # Extract raw data
                    if 'show' in attributes:
                        show = attributes.getValue('show')
                        if len(show) > args.data_maxlen:
                            show = DATA_TOO_LONG
                        name_access['raw'] = self.autoconvert(show)
                    # Extract showname
                    if 'showname' in attributes:
                        showname = attributes.getValue('showname')
                        if len(showname) > args.data_maxlen:
                            showname = DATA_TOO_LONG
                        name_access['show'] = showname

    # Call when an elements ends
    def endElement(self, tag):
        if tag == 'packet':
            self.__worker.write_frame(self.__frame)

    # Call when a character is read
    def characters(self, content):
        pass

class Worker():
    """ MAC address of flowworker instance"""
    mac = "00:00:00:00:00:00"
    delay = datetime.timedelta()
    raw_socket = None

    def __init__(self):
        # Get mac address of interface
        addrs = netifaces.ifaddresses(args.interface)
        Worker.mac = "{}".format(
                addrs[netifaces.AF_LINK][0]['addr']
                )
        # bind raw socket
        if not args.standalone:
            Worker.raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
            Worker.raw_socket.bind((args.interface, 0))
            self.__keep_alive_thread = Thread(target = self.send_keep_alive)
            self.__keep_alive_thread.start()

    def write_frame(self, frame):
        # Get times
        capture_timestamp = datetime.datetime.fromtimestamp(frame['frame']['time_epoch']['raw'], TIMEZONE)
        processed_timestamp = datetime.datetime.now(TIMEZONE)
        Worker.delay = processed_timestamp - capture_timestamp
        if args.debug:
            print("Frame delay: {}".format(Worker.delay))
        # Set environment information to packet
        frame['@timestamp'] = capture_timestamp.isoformat()
        frame['env']['hostname']['raw'] = HOSTNAME
        frame['env']['interface']['raw'] = args.interface
        frame['env']['processed']['raw'] = processed_timestamp.isoformat()
        frame['env']['delay']['raw'] = Worker.delay.seconds + Worker.delay.microseconds * (10 ** -6)
        if not args.standalone:
            frame['env']['flowgen'] = "0x{3}{4}{5}".format(
                    *frame['eth']['src']['raw'].split(':'))

        # Write frame 
        try:
            log_socket.send(json.dumps(frame).encode('utf-8'))
            log_socket.send(b'\n')
        except Exception as e:
            print("[{}] ERROR: Could not send json object".format(
                frame
            ))
            log_socket.close()
            sys.exit(1)

    def send_keep_alive(self):
        while(running):
            worker_delay = Worker.delay.seconds * (10 ** 3)\
                       + Worker.delay.microseconds // (10 ** 3)
            if args.debug:
                print("Worker delay: {} ms".format(worker_delay))
            # send keep alive frame
            ka_frame = bytes.fromhex(args.broadcast_mac.replace(':','')) # dst MAC
            ka_frame += bytes.fromhex(Worker.mac.replace(':','')) # src MAC
            ka_frame += b'\x09\x00' # ethertype 
            ka_frame += struct.pack(">I", worker_delay) # payload
            crc = binascii.crc32(ka_frame) & 0xffffffff
            ka_frame += struct.pack("I", crc) # checksum
            try:
                Worker.raw_socket.send(ka_frame)
            except:
                print("error raw")
            time.sleep(1)

def SIGINT_handler(x,y):
    global running
    running = False

if ( __name__ == '__main__'):
    args = parser.parse_args()
    # Validate arguments
    # bind logstash socket
    (logstash_host, *logstash_port) = args.logstash_connect.split(':')
    if len(logstash_port) == 0:
        logstash_port = [LOGSTASH_CONNECT_PORT]
    logstash_port = int(logstash_port[0])
    logstash_socket = (logstash_host , logstash_port)
    log_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            log_socket.connect(logstash_socket)
        except:
            if args.debug:
                print("retry connecting, to: {}".format(logstash_socket))
            time.sleep(10)
            continue
        break

    # Create a Worker
    worker = Worker()
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # override the default ContextHandler
    handler = PdmlHandler(worker)
    parser.setContentHandler(handler)
    parser_thread = Thread(target = parser.parse, args = (sys.stdin,))
    parser_thread.start()

    # Set signal handlers 
    signal.signal(signal.SIGINT, SIGINT_handler)
    signal.signal(signal.SIGTERM, SIGINT_handler)

    while running:
        signal.pause()
