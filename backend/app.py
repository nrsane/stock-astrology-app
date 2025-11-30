from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stock Astrology App</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
                text-align: center;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 15px;
                color: #333;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .success {
                background: #d4edda;
                color: #155724;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Stock Astrology App</h1>
            <div class="success">
                <h2>✅ DEPLOYMENT SUCCESSFUL!</h2>
                <p><strong>Phase 1: Foundation Complete</strong></p>
                <p>Next: We'll add features step by step</p>
            </div>
            <p><a href="/health" style="color: #667eea;">Health Check</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy', 'message': 'App is running!'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
