from flask import Flask
from controllers.consulta_controller import consulta_bp

app = Flask(__name__)

# Registrar el Blueprint (Arquitectura modular)
app.register_blueprint(consulta_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)