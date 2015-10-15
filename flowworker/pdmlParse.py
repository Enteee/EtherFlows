#! /usr/bin/env python2
# vim: set fenc=utf8 ts=4 sw=4 et :
import sys
import json
import xml.sax

class PdmlHandler( xml.sax.ContentHandler ):
    def __init__(self):
        pass

    def boolify(self, s):
        if s == 'True':
            return True
        if s == 'False':
            return False
        raise ValueError("Not a bool")

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
        if tag == "packet":
            pkt.clear()
        else:
            if attributes.has_key("name"):
                name = attributes.getValue("name")
            if attributes.has_key("show"):
                pkt[name] = self.autoconvert(attributes.getValue("show"))
            if attributes.has_key("showname"):
                pkt['{}.show'.format(name)] = attributes.getValue("showname")

    # Call when an elements ends
    def endElement(self, tag):
        if tag == "packet":
            json.dump(pkt,sys.stdout)
            sys.stdout.write("\n")
            sys.stdout.flush()

    # Call when a character is read
    def characters(self, content):
        pass

if ( __name__ == "__main__"):
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
