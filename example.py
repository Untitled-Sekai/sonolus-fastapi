from sonolus_fastapi import Sonolus

app = Sonolus(
    address='https://example.com',
    port=8000,
    enable_cors=True,
)

if __name__ == "__main__":
    app.run()