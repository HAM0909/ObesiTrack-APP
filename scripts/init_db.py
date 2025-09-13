import sys
import os

# Add project root to Python path
sys.path.insert(0, os.getcwd())

from app.database import Base, engine, get_db
from app.models.user import User
from app.models.prediction import Prediction

def create_tables():
    """Créer toutes les tables dans la base de données"""
    try:
        print("🔨 Creating tables in database...")
        
        # Créer toutes les tables définies dans les modèles
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tables created successfully!")
        print(f"📋 Created tables:")
        
        # Lister les tables créées
        for table_name in Base.metadata.tables.keys():
            print(f"   - {table_name}")
            
        # Vérifier la connexion
        with engine.connect() as conn:
            # Vérifier que les tables existent
            from sqlalchemy import text
            
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"\n🔍 Tables found in database:")
            for table in tables:
                print(f"   - {table}")
                
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()

def drop_tables():
    """Supprimer toutes les tables (utile pour recommencer)"""
    try:
        print("🗑️ Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped!")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")

if __name__ == "__main__":
    print("=== Database Initialization ===")
    
    choice = input("\nWhat do you want to do?\n1. Create tables\n2. Drop and recreate tables\n3. Just drop tables\nChoice (1-3): ")
    
    if choice == "1":
        create_tables()
    elif choice == "2":
        drop_tables()
        create_tables()
    elif choice == "3":
        drop_tables()
    else:
        print("Invalid choice. Creating tables by default...")
        create_tables()