from flask import Flask, jsonify
import os
from datetime import datetime

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
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
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
            .phase {
                background: #e3f2fd;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #2196f3;
            }
            .phase.completed {
                background: #d4edda;
                border-left-color: #28a745;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Stock Astrology App</h1>
            <div class="phase completed">
                <h2>✅ PHASE 1: FOUNDATION DEPLOYED</h2>
                <p><strong>Core application running successfully!</strong></p>
            </div>
            
            <div class="phase">
                <h3>📋 Deployment Phases</h3>
                <p><strong>Phase 1:</strong> ✅ Basic Flask App (Current)</p>
                <p><strong>Phase 2:</strong> ➡️ Database + Stock Management</p>
                <p><strong>Phase 3:</strong> ➡️ Real Stock Price Data</p>
                <p><strong>Phase 4:</strong> ➡️ KP Astrology & Correlation</p>
            </div>

            <div style="margin-top: 30px;">
                <h3>🔧 Test Endpoints</h3>
                <p><a href="/api/health" style="color: #667eea;">/api/health</a> - Health Check</p>
                <p><a href="/api/phase2-prepare" style="color: #667eea;">/api/phase2-prepare</a> - Prepare Phase 2</p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "phase": "1",
        "message": "Foundation deployed successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "next_phase": "Database integration"
    })

@app.route('/api/phase2-prepare')
def phase2_prepare():
    return jsonify({
        "phase": "2",
        "status": "ready",
        "instructions": "Add database dependencies to requirements.txt",
        "next_dependencies": ["Flask-SQLAlchemy", "SQLAlchemy", "psycopg2-binary"]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
