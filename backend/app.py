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
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Stock Astrology App</h1>
            
            <div class="phase completed">
                <h2>✅ PHASE 1: FOUNDATION DEPLOYED</h2>
                <p><strong>SQLite Version - Working Perfectly!</strong></p>
                <p>Database: SQLite (No external dependencies)</p>
            </div>

            <div class="phase">
                <h3>📋 Deployment Strategy</h3>
                <p><strong>Phase 1:</strong> ✅ SQLite Foundation (Current)</p>
                <p><strong>Phase 2:</strong> ➡️ Add Stock Management</p>
                <p><strong>Phase 3:</strong> ➡️ Add PostgreSQL Database</p>
                <p><strong>Phase 4:</strong> ➡️ Add Stock Price Data</p>
                <p><strong>Phase 5:</strong> ➡️ Add KP Astrology</p>
            </div>

            <div style="margin-top: 30px;">
                <h3>🔧 Test Endpoints</h3>
                <p><a href="/api/health" style="color: #667eea;">/api/health</a> - Health Check</p>
                <p><a href="/api/ready-for-phase2" style="color: #667eea;">/api/ready-for-phase2</a> - Check Phase 2 Readiness</p>
            </div>

            <div class="phase" style="background: #fff3cd; border-left-color: #ffc107;">
                <h3>⚠️ Important Note</h3>
                <p>Using SQLite first to avoid PostgreSQL dependency issues.</p>
                <p>We'll upgrade to PostgreSQL in Phase 3 after core features work.</p>
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
        "database": "sqlite",
        "message": "Foundation deployed successfully with SQLite",
        "timestamp": datetime.utcnow().isoformat(),
        "next_phase": "Add SQLite database models"
    })

@app.route('/api/ready-for-phase2')
def ready_for_phase2():
    return jsonify({
        "phase": "2",
        "status": "ready",
        "database": "sqlite",
        "instructions": "Add SQLite database models for stock management",
        "dependencies_needed": ["Flask-SQLAlchemy"],
        "note": "Using SQLite to avoid PostgreSQL dependency issues"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
