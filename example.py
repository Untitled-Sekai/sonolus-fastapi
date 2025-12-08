from sonolus_fastapi import Sonolus

app = Sonolus(
    address='https://example.com', # サーバーアドレスを指定してください Specify your server address
    port=8000, # サーバーポートを指定してください Specify your server port
    enable_cors=True, # CORSを有効にするかどうか Whether to enable CORS
)

app.load('path/to/sonolus/pack') # Sonolus packのパスを指定してください Specify the path to the Sonolus pack

if __name__ == "__main__":
    app.run() # サーバーを起動します Start the server