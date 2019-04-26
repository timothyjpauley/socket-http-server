import socket
import sys
import traceback
import mimetypes
import os

#Tim Pauley
#Python 230a, Assignment 03
#Date: April 20 2019 

#Socket HTTP Server

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->
        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """
    return b"\r\n".join([
        b"HTTP/1.1 200 OK",
        b"Content-Type: " + mimetype,
        b"",
        body,
    ])

def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    return b"\r\n".join([
        b"HTTP/1.1 405 Method Not Allowed",
        b"",
        b"You can't do that on this server!",
    ])


def response_not_found():
    """Returns a 404 Not Found response"""
    return b"\r\n".join([
        b"HTTP/1.1 404 Not Found",
        b"",
        b"404 body!",
    ])


def parse_request(request):
    """
    This is where the GET Parse Request takes place
    """
    method, path, protocol = request.split("\r\n")[0].split(" ")
    if method != "GET":
        raise NotImplementedError("This server only handles GET requests.")

    return path

def response_path(path):
    """
    This method should return appropriate content and a mime type.
    If the requested path is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.
    If the path is a file, it should return the contents of that file
    and its correct mimetype.
    If the path does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.
    Ex:
        response_path('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")
        response_path('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")
        response_path('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")
        response_path('/a_page_that_doesnt_exist.html') -> Raises a NameError
    """
    home_dir = os.path.abspath("webroot")
    location = os.path.join(home_dir, path[1:])

    #This is where the directory checked
    if os.path.isdir(location):
        mime_type = mimetypes.types_map['.txt'].encode()
        content = os.listdir(location)
        str_content = str(content).encode()
        return str_content, mime_type

    #this is where the path is checked
    if os.path.isfile(location):
        with open(location, 'rb') as f:
            content = f.read()
            mime_type = mimetypes.guess_type(location, strict=True)[0].encode()
            return content, mime_type

    raise NameError

    # TODO: Raise a NameError if the requested content is not present
    # under webroot.

    # TODO: Fill in the appropriate content and mime_type give the path.
    # See the assignment guidelines for help on "mapping mime-types", though
    # you might need to create a special case for handling make_time.py
    #
    # If the path is "make_time.py", then you may OPTIONALLY return the
    # result of executing `make_time.py`. But you need only return the
    # CONTENTS of `make_time.py`.


#this is where the server is defined
def server(log_buffer=sys.stderr):
    #this translates to http://localhost:100000
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)
    #here is where the try loop begins
    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            #here is the try condition 
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                #while try connection
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break


                print("Request received:\n{}\n\n".format(request))

                #try loop begins    
                try:
                    path = parse_request(request)
                    print("Sending response", file=log_buffer)
                    content, mime_type = response_path(path)
                    response = response_ok(body=content, mimetype=mime_type)
                # TODO: Use response_path to retrieve the content and the mimetype,
                # based on the request path.

                except NotImplementedError:
                    response = response_method_not_allowed()
                        #content, mime_type = resolve_uri(url)
                except NameError:
                    response = response_not_found()
                # TODO; If parse_request raised a NotImplementedError, then let
                # response be a method_not_allowed response. If response_path raised
                # a NameError, then let response be a not_found response. Else,
                # use the content and mimetype from response_path to build a
                # response_ok.

                except:
                    traceback.print_exc()
                finally:
                    conn.sendall(response)
                    conn.close()

            except:
                traceback.print_exc()
    #here is where the keyboard Interrupt is used
    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)