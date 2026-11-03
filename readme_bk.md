proyecto_satje/
│
├── app.py                 # Punto de entrada de la aplicación (Flask)
├── requirements.txt       # Dependencias
│
├── controllers/
│   └── consulta_controller.py  # Controlador de las rutas y lógica de peticiones
│
├── services/
│   └── satje_scraper_service.py # Servicio de automatización con Playwright (Modelo/Lógica)
│
└── views/                 # (Opcional, si devuelves JSON se usa el controlador directamente)