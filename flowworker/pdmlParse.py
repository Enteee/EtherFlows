#! /usr/bin/env python2


import sys
import json
import xml.sax




class PdmlHandler( xml.sax.ContentHandler ):
   def __init__(self):
      self.CurrentData = ""
      self.type = ""
      self.format = ""
      self.year = ""
      self.rating = ""
      self.stars = ""
      self.description = ""

   # Call when an element starts
   def startElement(self, tag, attributes):
      self.CurrentData = tag
      if tag == "packet":
         pkt.clear()
      else:
          if attributes.has_key("name") and attributes.has_key("showname"):
              name = attributes.getValue("name")
              showname = attributes.getValue("showname")
              pkt[name] = showname

          #name = attributes["name"]
          #showname = attributes["showname"]
          #pkt[name] = showname

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


#if __name__ == "__main__":
#
#    e = xml.etree.ElementTree.parse(sys.stdin).getroot()
#    for pkt in e.findall('packet'):
#            print("{")
#            for proto in pkt.findall('proto'):
#                for field in proto.findall('field'):
#                    name = field.get('name')
#                    if name != "":
#                        showname = field.get('showname')
#                        print("\t\"{}\": \"{}\",".format(name,showname))
#
#            print("}")
    