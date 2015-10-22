#! /usr/bin/env python2
# vim: set fenc=utf8 ts=4 sw=4 et :
import sys
import json
import argparse
import xml.sax
import socket

#MAC Addr of the flow generator 
DATA_MAXLEN = 200
DATA_TOO_LONG = 'Data too long'

parser = argparse.ArgumentParser(description='Flowworker')

parser.add_argument('-i',
                    required=True,
                    type=str,
                    dest='interface',
                    help='Interface to listen on'
                    )
parser.add_argument('-no',
                    dest='no_answer',
                    action="store_true",
                    help='Dont answer packets'
                    )
parser.add_argument('-l',
                    default=DATA_MAXLEN,
                    type=int,
                    dest='data_maxlen',
                    help='Maximum lenght of data in tshark pdml-field [default: {}]'.format(DATA_MAXLEN)
                    )

class PdmlHandler(xml.sax.ContentHandler):
    def __init__(self):
        pass

    def send_ack(self, src, dst):
        src_hex = src.replace(':','').decode('hex')
        dst_hex = dst.replace(':','').decode('hex')

        payload = 'ENTE'
        checksum = '\x63\x07\x3d\x02'
        ethertype = '\x09\x00'
        s.send(dst_hex+src_hex+ethertype+payload+checksum)

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
            pkt.clear()
        else:
            if attributes.has_key('name'):
                name = attributes.getValue('name')
                # Extract raw data
                if attributes.has_key('show'):
                    show = attributes.getValue('show')
                    if len(show) > args.data_maxlen:
                        show = DATA_TOO_LONG
                    pkt[name] = self.autoconvert(show)
                # Extract showname
                if attributes.has_key('showname'):
                    showname = attributes.getValue('showname')
                    if len(showname) > args.data_maxlen:
                        showname = DATA_TOO_LONG
                    pkt['{}.show'.format(name)] = showname

    # Call when an elements ends
    def endElement(self, tag):
        if tag == 'packet':
            if not args.no_answer:
                try:
                    dst = pkt['eth.dst']
                    src = pkt['eth.src']
                    if dst not in flows:
                        self.send_ack(dst, src)
                        flows[dst] = True
                except KeyError:
                    pass
            json.dump(pkt,sys.stdout)
            sys.stdout.write('\n')
            sys.stdout.flush()

    # Call when a character is read
    def characters(self, content):
        pass

if ( __name__ == '__main__'):
    args = parser.parse_args()
    if not args.no_answer:
        flows = {}
        try:
            s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
        except socket.error , msg:
            print('Socket could not be created. Error Code : {} Message: {}'.format(str(msg[0]),msg[1]))
            sys.exit()
        try:
            s.bind((args.interface, 0))
        except:
            print('Could not bind socket')
            sys.exit()
    #pkt dictionary
    pkt = {}
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # override the default ContextHandler
    handler = PdmlHandler()
    parser.setContentHandler(handler)
    parser.parse(sys.stdin)
