from .auth_routes import auth_bp
from .channel_routes import channel_bp
from .subscription_routes import subscription_bp
from .chat_routes import chat_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(channel_bp, url_prefix="/api/channels")
    app.register_blueprint(subscription_bp, url_prefix="/api/subscription")
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    # app.register_blueprint(stream_bp, url_prefix="/api/stream")    
    