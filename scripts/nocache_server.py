# -*- coding: utf-8 -*-
"""No-cache static server — serve a Claude Design prototype so the browser/babel always re-fetch
fresh JSX. Babel-standalone caches transpiled modules by URL; no-store headers (plus serving on a
*fresh port* when in doubt) guarantee a clean recompile after you edit a .jsx.

Usage:
  python nocache_server.py [port] [root]
    port  default 8853   (use a NEW port whenever a change isn't showing up)
    root  default = current working directory (point at the project that holds the entry .html)

Then open  http://127.0.0.1:<port>/<entry>.html
"""
import os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8853
ROOT = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.getcwd()


class H(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    os.chdir(ROOT)
    print(f"serving {ROOT} at http://127.0.0.1:{PORT}/")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
