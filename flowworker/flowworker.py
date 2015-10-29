#!/usr/bin/env python2
# vim: set fenc=utf8 ts=4 sw=4 et :
import time 
import sys
import json
import argparse
import xml.sax
import socket
import os

#MAC Addr of the flow generator 
DATA_MAXLEN = 200
DATA_TOO_LONG = 'Data too long'
FLOW_BUFFER_TIME = 3
STANDALONE_FILE = '/vagrant/sys/standalone'

parser = argparse.ArgumentParser(description='Flowworker')

parser.add_argument('-i',
                    required=True,
                    type=str,
                    dest='interface',
                    help='Interface to listen on'
                    )
parser.add_argument('-S',
                    default=os.path.isfile(STANDALONE_FILE),
                    dest='standalone',
                    action="store_true",
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
class Flow():

    """ The overall packet time """
    newest_overall_frame_time = 0

    def __init__(self, first_frame):
        self.__frames = []
        self.__flowid_mac = first_frame['eth.dst']
        self.__flowgen_mac = first_frame['eth.src']
        self.__flowgen = "0x{3}{4}{5}".format(*self.__flowgen_mac.split(':'))
        self.__flushed = False
        self.__newest_frame_time = self.__first_frame_time = first_frame['frame.time_epoch']
        self.add_frame(first_frame)
        self.__send_ack()

    def add_frame(self, frame):
        frame['env.flowid'] = self.__flowid_mac
        if not args.standalone:
            frame['env.flowgen'] = self.__flowgen
        # check if packet expands flow length
        self.__first_frame_time = min(self.__first_frame_time, frame['frame.time_epoch'])
        self.__newest_frame_time = max(self.__newest_frame_time, frame['frame.time_epoch'])
        Flow.newest_overall_frame_time = max(Flow.newest_overall_frame_time, frame['frame.time_epoch'])
        if self.__flushed:
            self._write_frame(frame)
        else:
            # Buffer packet
            self.__frames.append(frame)
            flow_length = self.__newest_frame_time - self.__first_frame_time
            if flow_length > args.flow_buffer_time:
                self.flush()

    def not_expired(self):
        return self.__newest_frame_time > Flow.newest_overall_frame_time - args.flow_buffer_time

    def flush(self):
        for p in self.__frames:
            self._write_frame(p)
        self.__frames = []
        self.__flused = True

    def __send_ack(self):
        if not args.standalone:
            ack_frame = self.__flowgen_mac.replace(':','').decode('hex') # dst MAC
            ack_frame += self.__flowid_mac.replace(':','').decode('hex') # src MAC
            ack_frame += '\x09\x00' # ethertype 
            ack_frame += 'ENTE' # payload
            ack_frame += '\x63\x07\x3d\x02' # checksum
            socket.send(ack_frame)

    def _write_frame(self, frame):
        json.dump(frame, sys.stdout)
        sys.stdout.write('\n')
        sys.stdout.flush()
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
            self.__frame = {}
        else:
            if attributes.has_key('name'):
                name = attributes.getValue('name')
                # Extract raw data
                if attributes.has_key('show'):
                    show = attributes.getValue('show')
                    if len(show) > args.data_maxlen:
                        show = DATA_TOO_LONG
                    self.__frame[name] = self.autoconvert(show)
                # Extract showname
                if attributes.has_key('showname'):
                    showname = attributes.getValue('showname')
                    if len(showname) > args.data_maxlen:
                        showname = DATA_TOO_LONG
                    self.__frame['{}.show'.format(name)] = showname

    # Call when an elements ends
    def endElement(self, tag):
        # clean up expired flows
        self.__flows = { flowid: flow for (flowid, flow) in self.__flows.items() if flow.not_expired() }
        if tag == 'packet':
            try:
                flowid = self.__frame['eth.dst']
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
    # bind socket
    if not args.standalone:
        socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        socket.bind((args.interface, 0))
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # override the default ContextHandler
    handler = PdmlHandler()
    parser.setContentHandler(handler)
    parser.parse(sys.stdin)
