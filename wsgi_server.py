from src.server import app
from gunicorn.app.base import BaseApplication

class GunicornApp(BaseApplication):
    def __init__(self, app, options=None):
        self.app = app
        self.options = options or {}
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.app

if __name__ == '__main__':
    options = {
        'bind': '0.0.0.0:8080',  
        'workers': 2,            
        'timeout': 60          
    }
    
    GunicornApp(app, options).run()

# Note:  use `lsof -i :8080` and `kill {pid}`  to release the port