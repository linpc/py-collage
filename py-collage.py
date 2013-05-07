#!/usr/bin/env python2

import exceptions
import getopt
import os
import socket
import sys
import SimpleHTTPServer
import SocketServer

import Image


DEFAULT_PORT = 8000

def usage():
    print 'Usage'
    print "\t", sys.argv[0], "[-h|--help]"
    print "\t", sys.argv[0], "[[-p|--port] <port>]", "[-i|--index]", "[-t|--thumbnail]", "[-T|--title]"
    print '''
        -h, --help          show usage
        -p, --port          bind web server at <port> instead of default 8000
        -i, --index         create index html file
        -t, --thumbnail     craete thumbnails (imply --index)
        -T, --title         set web page title (imply --index)
'''


def server_start(port):
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

    try:
        httpd = SocketServer.TCPServer(("", port), Handler)
    except socket.error:
        print "Error: socket port %d already in use" % port
        sys.exit(3)

    print 'serving at port', port
    httpd.serve_forever()


def port_parse(port_string):
    try:
        try_port = int(port_string)
    except exceptions.ValueError:
        usage()
        sys.exit(1)

    if try_port < 0 or try_port > 65535:
        print 'Error: given port out of range'
        print 'bind at default port', DEFAULT_PORT
        try_port = DEFAULT_PORT

    return try_port


def thumbnail_create():
    dirroot = os.getcwd()

    if os.path.isdir(os.path.join(dirroot, 't')):
        print 'thumbnail folder t/ exists'
        print 'skip...'
        return
#        sys.exit(2)

    os.mkdir('t', 0700)
    thumbdir = os.path.join(dirroot, 't')

    size = 320, 320

    for filename in os.listdir(dirroot):
        outfile = os.path.join(thumbdir, filename)
        try:
            im = Image.open(filename)
            im.thumbnail(size)
            im.save(outfile, "jpeg")
            print "create thumbnail", outfile
        except IOError:
            print "cannot create thumbnail for", filename


def index_create(title, is_thumbnail):
    dirroot = os.getcwd()

    if os.path.exists(os.path.join(dirroot, 'index.html')):
        print 'index.html exists'
        print 'skip...'
        return
#        sys.exit(2)

    index = open('index.html', 'w')

    HTML_HEADER = '''
<!DOCTYPE html>
<head>
    <meta charset="UTF-8" />
    <title>%s</title>
</head>
'''[1:]

    IMG_ENTRY = '\t<a href="%s"><img src="%s" /></a>\n'
    IMG_TINY_ENTRY = '\t<a href="%s"><img src="t/%s" /></a>\n'

    index.write(HTML_HEADER % title)

    index.write('<body>\n')

    for filename in os.listdir(dirroot):
        if filename == 'index.html' or filename == 't':
            continue

        if is_thumbnail == True:
            index.write(IMG_TINY_ENTRY % (filename, filename))
        else:
            index.write(IMG_ENTRY % (filename, filename))

    index.write("</body>\n</html>")

    index.close()


####################################
# main: parse arguments
####################################

def main(argv):
    is_index = False
    is_thumbnail = False
    is_Title = False

    port = DEFAULT_PORT
    title = 'Photos'

    try:
        opts, args = getopt.getopt(argv, "hp:itT:", ["help", "port=", "index", "thumbnail", "title="])
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif opt in ("-i", "--index"):
            is_index = True
        elif opt in ("-p", "--port"):
            port = port_parse(arg)
        elif opt in ("-t", "--thumbnail"):
            thumbnail_create()
            is_thumbnail = True
            is_index = True
        elif opt in ("-T", "--title"):
            title = arg
            is_index = True

    if args != []:
        port = port_parse(args[0])

    if is_index == True:
        index_create(title, is_thumbnail)

    server_start(port)


####################################
# main
####################################

if __name__ == "__main__":
    print "Current directory:", os.getcwd()
    main(sys.argv[1:])
