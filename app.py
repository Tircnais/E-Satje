from flask import Flask
import os
from controllers.consulta_controller import consulta_bp

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # <-- Esto respeta estrictamente el orden de las llaves

os.makedirs(os.path.join('archivos', 'json'), exist_ok=True)
os.makedirs('controllers', exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('logs', exist_ok=True)
os.makedirs('services', exist_ok=True)

app.register_blueprint(consulta_bp)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
