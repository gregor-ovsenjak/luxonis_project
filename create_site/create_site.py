import psycopg2
from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write('<html><head><title>Items</title><meta charset="UTF-8"></head><body>'.encode())

        conn = psycopg2.connect(
        dbname="mydatabase",
        user="myuser",
        password="mypassword",
        host="postgres",
        port="5432",
        options='-c client_encoding=utf-8'   
    )
        
        cur = conn.cursor()

        cur.execute("SELECT name,locality,price, image_url FROM flats;") 
        rows = cur.fetchall()
        
        for row in rows:
            self.wfile.write(f"<h2>{row[0]}</h2>".encode() )
            self.wfile.write(f"<h3>{row[1]}</h2>".encode() )
            self.wfile.write(f"<h3>{row[2]}</h2>".encode() )
            self.wfile.write(f"<img src='{row[3]}' width='200' height='200'><br><br>".encode()) 

        cur.close()
        conn.close()

        self.wfile.write("</body></html>".encode())

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
    

if __name__ == '__main__':
    run()