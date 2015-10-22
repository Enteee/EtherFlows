#! /usr/bin/env python2
# vim: set fenc=utf8 ts=4 sw=4 et :
import sys
import json
import argparse
import xml.sax
import socket

#MAC Addr of the flow generator 
FLOWGEN_MAC = 'b4:be:b1:6b:00:b5'
DATA_MAXLEN = 200
DATA_TOO_LONG = 'Data too long'

parser = argparse.ArgumentParser(description='Flowworker')

parser.add_argument('-m',
                    default=FLOWGEN_MAC,
                    type=str,
                    dest='mac',
                    help='MAC address of flows generated; Set to "all" if you want to capture all MACs [default: {}]'.format(FLOWGEN_MAC)
                    )
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


class PdmlHandler( xml.sax.ContentHandler ):
    def __init__(self):
        pass

    def send_ack(self, src, dst):
        src_hex = src.replace(':','').decode('hex')
        dst_hex = dst.replace(':','').decode('hex')

        payload = ('['*30)+'ENTE'+(']'*30)
        checksum = '\x98\x08\xE8\x92'
        ethertype = '\x08\x01'

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
                #check if flow is in dictionary
                if not args.no_answer and name == 'eth.src':
                    src = attributes.getValue('show')
                    dst = str(pkt['eth.dst'])
                    if dst not in flows:
                        self.send_ack(dst, src)
                        flows[dst] = True
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
            print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        try:
            s.bind((args.interface, 0))
        except:
            print 'Could not bind socket'
            sys.exit()
    #pkt dictionary 
    pkt = {}   
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # override the default ContextHandler
    Handler = PdmlHandler()
    parser.setContentHandler( Handler )
    parser.parse(sys.stdin)
