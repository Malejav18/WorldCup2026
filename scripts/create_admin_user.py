"""Script para crear un usuario admin en auth.db."""
from pathlib import Path
import sys

# Agregar backend al path para importar los modulos
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy.orm import Session

from shared.security import hash_password
from shared.database import build_engine, build_session_factory
from auth_service.app.config import settings as auth_settings
from auth_service.app.database import Base as AuthBase
from auth_service.app.entities.user import User
from user_service.app.config import settings as user_settings
from user_service.app.database import Base as UserBase
from user_service.app.entities.user_profile import UserProfile


def create_admin_user(email: str, password: str) -> None:
    """Crea un usuario admin en auth.db y su perfil en user.db.
    
    Args:
        email: Email del usuario admin
        password: Contrasena en texto plano (sera hasheada)
    """
    # Auth DB: construir engine y session
    auth_engine = build_engine(auth_settings.database_path)
    AuthSession = build_session_factory(auth_engine)
    
    # User DB: construir engine y session
    user_engine = build_engine(user_settings.database_path)
    UserSession = build_session_factory(user_engine)
    
    # Crear tablas si no existen
    AuthBase.metadata.create_all(auth_engine)
    UserBase.metadata.create_all(user_engine)
    
    auth_db: Session = AuthSession()
    user_db: Session = UserSession()
    
    try:
        # Verificar que el usuario no exista ya en auth-service
        existing_user = auth_db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"⚠️  El usuario con email {email} ya existe en auth.db.")
            return
        
        # Crear nuevo usuario admin en auth-service
        admin_user = User(
            email=email,
            password_hash=hash_password(password),
            role="ADMIN",
            is_active=True,
        )
        auth_db.add(admin_user)
        auth_db.commit()
        auth_db.refresh(admin_user)
        
        # Crear perfil en user-service usando el mismo UUID
        existing_profile = user_db.query(UserProfile).filter(UserProfile.email == email).first()
        if existing_profile:
            print(f"⚠️  El perfil de usuario con email {email} ya existe en user.db.")
        else:
            profile = UserProfile(
                id=admin_user.id,
                email=email,
                display_name="Administrator",
            )
            user_db.add(profile)
            user_db.commit()
        
        print(f"✅ Usuario admin creado exitosamente:")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        print(f"   Creado en auth.db: {admin_user.created_at}")
        print(f"   Perfil creado en user.db")
        
    except Exception as e:
        auth_db.rollback()
        user_db.rollback()
        print(f"❌ Error al crear el usuario admin: {e}")
        raise
    finally:
        auth_db.close()
        user_db.close()


if __name__ == "__main__":
    # Valores por defecto para el usuario admin
    DEFAULT_ADMIN_EMAIL = "admin@worldcup2026.com"
    DEFAULT_ADMIN_PASSWORD = "AdminPassword123!"
    
    # Permitir pasar email y password como argumentos
    admin_email = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ADMIN_EMAIL
    admin_password = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_ADMIN_PASSWORD
    
    print(f"Creando usuario admin con email: {admin_email}")
    create_admin_user(admin_email, admin_password)
