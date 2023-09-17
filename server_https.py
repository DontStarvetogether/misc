import http.server
import socketserver
import ssl

# 定义请求处理程序
class SimpleHandler(http.server.SimpleHTTPRequestHandler):
    pass

# 指定服务器地址和端口
host = "10.0.4.11"
port = 443

# 指定SSL证书文件路径
certificate_file = "/home/starve/certification/xiaowangzi.cool.crt"
private_key_file = "/home/starve/certification/xiaowangzi.cool.key"

# 创建SSL上下文
ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile=certificate_file, keyfile=private_key_file)

# 创建服务器对象
server_address = (host, port)
httpd = socketserver.TCPServer(server_address, SimpleHandler)

# 应用SSL上下文到服务器对象
httpd.socket = ssl_context.wrap_socket(httpd.socket)

# 启动服务器
print(f"Starting server on {host}:{port}")
httpd.serve_forever()