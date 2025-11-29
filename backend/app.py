from flask import Flask, jsonify, render_template
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
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { background: #667eea; color: white; padding: 2rem; border-radius: 10px; text-align: center; }
            .card { background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin: 1rem 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📈 Stock Astrology App</h1>
            <p>Basic Version - Successfully Deployed! 🚀</p>
        </div>
        
        <div class="card">
            <h2>Welcome!</h2>
            <p>This is the basic version of the Stock Astrology App.</p>
            <p><strong>Status:</strong> ✅ Running successfully</p>
            <p><strong>Next:</strong> Add database and KP astrology features</p>
        </div>
        
        <div class="card">
            <h3>Test Links</h3>
            <p><a href="/api/health">Health Check</a></p>
            <p><a href="/api/hello">Hello API</a></p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Stock Astrology App is running!",
        "version": "1.0.0"
    })

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from Stock Astrology App!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
