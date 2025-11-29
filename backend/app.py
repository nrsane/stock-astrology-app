from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
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
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                padding: 40px;
                border-radius: 15px;
                color: #333;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                color: #667eea;
                margin-bottom: 20px;
            }
            .status {
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Stock Astrology App</h1>
            <p><strong>Successfully Deployed on Render!</strong></p>
            
            <div class="status">
                <h3>✅ Application Status: RUNNING</h3>
                <p>Python 3.11 + Flask - Stable Version</p>
            </div>
            
            <p>Next steps: Add database and KP astrology features</p>
            
            <div style="margin-top: 30px;">
                <h4>Test Endpoints:</h4>
                <p><a href="/api/health" style="color: #667eea;">/api/health</a> - Health check</p>
                <p><a href="/api/test" style="color: #667eea;">/api/test</a> - Test endpoint</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Stock Astrology App is running on Python 3.11",
        "python_version": "3.11.8",
        "timestamp": "2024"
    })

@app.route('/api/test')
def test():
    return jsonify({
        "message": "Test successful!",
        "app": "Stock Astrology",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
