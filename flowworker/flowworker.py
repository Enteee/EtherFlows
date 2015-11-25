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

DATA_MAXLEN = 200
DATA_TOO_LONG = 'Data too long'
FLOW_BUFFER_TIME = 0.5
STANDALONE = False
DEBUG = True
HOSTNAME=socket.gethostname()
KIBANA_NOT_SUPPORTED_CHARS = '_'
LOGSTASH_CONNECT_PORT = '5000'
LOGSTASH_CONNECT = '127.0.0.1:{}'.format(LOGSTASH_CONNECT_PORT)
TIMEZONE = pytz.timezone(time.tzname[0])


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
parser.add_argument('-l',
                    default=DATA_MAXLEN,
                    type=int,
                    dest='data_maxlen',
                    help='Maximum lenght of data in tshark pdml-field [default: {}]'.format(DATA_MAXLEN)
                    )
parser.add_argument('-t',
                    default=FLOW_BUFFER_TIME,
                    type=int,
                    dest='flow_buffer_time',
                    help='Lenght (in seconds) to buffer a flow before writing the packets [default: {}]'.format(FLOW_BUFFER_TIME)
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

class Flow():

    """ The overall packet time """
    newest_overall_frame_time = datetime.datetime(datetime.MINYEAR, 1, 1, tzinfo = TIMEZONE)

    def __init__(self, first_frame):
        self.__frames = []
        self.__flowid_mac = first_frame['eth']['dst']['raw']
        self.__flowgen_mac = first_frame['eth']['src']['raw']
        self.__flowgen = "0x{3}{4}{5}".format(*self.__flowgen_mac.split(':'))
        self.__flushed = False
        self.__first_frame_time = self.__newest_frame_time = datetime.datetime.fromtimestamp(first_frame['frame']['time_epoch']['raw'], TIMEZONE)
        self.add_frame(first_frame)
        self.__send_ack()

    def add_frame(self, frame):
        capture_timestamp = datetime.datetime.fromtimestamp(frame['frame']['time_epoch']['raw'], TIMEZONE)
        processed_timestamp = datetime.datetime.now(TIMEZONE)
        delay = processed_timestamp - capture_timestamp
        flow_length = self.__newest_frame_time - self.__first_frame_time
        frame['@timestamp'] = capture_timestamp.isoformat()
        frame['env']['flowid']['raw'] = self.__flowid_mac
        frame['env']['hostname']['raw'] = HOSTNAME
        frame['env']['interface']['raw'] = args.interface
        frame['env']['processed']['raw'] = processed_timestamp.isoformat()
        frame['env']['delay']['raw'] = delay.seconds + delay.microseconds * (10 ** -9)
        if not args.standalone:
            frame['env']['flowgen'] = self.__flowgen
        # check if packet expands flow length
        self.__first_frame_time = min(self.__first_frame_time, capture_timestamp)
        self.__newest_frame_time = max(self.__newest_frame_time, capture_timestamp)
        Flow.newest_overall_frame_time = max(Flow.newest_overall_frame_time, capture_timestamp)
        if args.debug:
            print('[{}] add_frame, flow:{}, length: {} seconds, flushed:{}'.format(
                Flow.newest_overall_frame_time,
                self.__flowid_mac,
                flow_length,
                self.__flushed))
        if self.__flushed:
            self._write_frame(frame)
        else:
            # Buffer packet
            self.__frames.append(frame)
            if flow_length >= datetime.timedelta(seconds=args.flow_buffer_time):
                if args.debug:
                    print("[{}] flusing flow, flowid: {}".format(
                        Flow.newest_overall_frame_time,
                        self.__flowid_mac))
                self.flush()

    def not_expired(self):
        return self.__newest_frame_time > \
            (Flow.newest_overall_frame_time - datetime.timedelta(seconds=args.flow_buffer_time))

    def flush(self):
        for p in self.__frames:
            self._write_frame(p)
        self.__frames = []
        self.__flused = True

    def __send_ack(self):
        if not args.standalone:
            ack_frame = bytes.fromhex(self.__flowgen_mac.replace(':','')) # dst MAC
            ack_frame += bytes.fromhex(self.__flowid_mac.replace(':','')) # src MAC
            ack_frame += b'\x09\x00' # ethertype 
            ack_frame += b'ENTE' # payload
            ack_frame += b'\x63\x07\x3d\x02' # checksum
            raw_socket.send(ack_frame)

    def _write_frame(self, frame):
        try:
            json_string = '{}\n'.format(json.dumps(frame))
            log_socket.send(json_string.encode('utf-8'))
        except Exception as e:
            print("ERROR: Could not send json object")
            log_socket.close()
            sys.exit(1)
        self.__send_ack()

class PdmlHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.__frame = {}
        self.__flows = {}

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
                        if(args.debug):
                            print("[{}] name not a dict, name: {}".format(
                                Flow.newest_overall_frame_time,
                                name))
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
            # clean up expired flows
            if args.debug:
                for (flowid, flow) in self.__flows.items():
                    if not flow.not_expired():
                        print("[{}] flow expired, flowid: {}".format(
                            Flow.newest_overall_frame_time,
                            flowid))
            self.__flows = { flowid: flow for (flowid, flow) in self.__flows.items() if flow.not_expired() }
            try:
                flowid = self.__frame['eth']['dst']['raw']
                if args.debug:
                    print("[{}] new packet, flowid: {}".format(
                        Flow.newest_overall_frame_time,
                        flowid))
                try: 
                    flow = self.__flows[flowid]
                    self.__flows[flowid].add_frame(self.__frame)
                except KeyError:
                    # flow unknown add new flow
                    self.__flows[flowid] = Flow(self.__frame)
            except KeyError:
                pass

    # Call when a character is read
    def characters(self, content):
        pass

if ( __name__ == '__main__'):
    args = parser.parse_args()
    # bind raw socket
    if not args.standalone:
        raw_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        raw_socket.bind((args.interface, 0))
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
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # override the default ContextHandler
    handler = PdmlHandler()
    parser.setContentHandler(handler)
    parser.parse(sys.stdin)
