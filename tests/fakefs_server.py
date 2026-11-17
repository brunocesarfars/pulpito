import json,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
DOCS={};LOCK=threading.Lock()
class H(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def _s(self,o,c=200):
        b=json.dumps(o).encode();self.send_response(c)
        self.send_header("Content-Type","application/json");self.send_header("Access-Control-Allow-Origin","*");self.send_header("Content-Length",str(len(b)));self.end_headers();self.wfile.write(b)
    def do_OPTIONS(self):
        self.send_response(204);self.send_header("Access-Control-Allow-Origin","*");self.send_header("Access-Control-Allow-Headers","*");self.send_header("Access-Control-Allow-Methods","*");self.end_headers()
    def do_POST(self):
        n=int(self.headers.get("Content-Length","0"));b=json.loads(self.rfile.read(n) or b"{}")
        with LOCK:
            if self.path=="/get":
                d=DOCS.get(b["path"]);self._s({"exists":d is not None,"data":d["data"] if d else None,"ver":d["ver"] if d else 0})
            elif self.path=="/list":
                p=b["path"]+"/";out=[]
                for k,v in DOCS.items():
                    if k.startswith(p) and "/" not in k[len(p):]:out.append({"id":k[len(p):],"data":v["data"],"ver":v["ver"]})
                self._s({"docs":out})
            elif self.path=="/commit":
                for c in b.get("checks",[]):
                    cur=DOCS.get(c["path"]);
                    if (cur["ver"] if cur else 0)!=c["ver"]:return self._s({"conflict":True})
                for w in b["writes"]:
                    if w.get("del"):DOCS.pop(w["path"],None)
                    else:
                        cur=DOCS.get(w["path"]);DOCS[w["path"]]={"data":w["data"],"ver":(cur["ver"] if cur else 0)+1}
                self._s({"ok":True})
            elif self.path=="/reset":DOCS.clear();self._s({"ok":True})
            elif self.path=="/dump":self._s(DOCS)
            else:self._s({},404)
ThreadingHTTPServer(("127.0.0.1",8766),H).serve_forever()
