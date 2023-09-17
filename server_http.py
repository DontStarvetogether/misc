import http.server
import socketserver

# 定义请求处理程序
class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    pass

# 指定服务器地址和端口
host = "10.0.4.11"
port = 80

# 创建服务器对象
server_address = (host, port)
server = socketserver.TCPServer(server_address, SimpleHandler)

# 启动服务器
print(f"Starting server on {host}:{port}")
server.serve_forever()