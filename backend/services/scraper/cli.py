import argparse
import getpass
import os
import sys
from pathlib import Path

# Asegurar path
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR.parent))

from backend.database import get_db, engine, Base
from backend.services.scraper.pipeline import ejecutar_pipeline_estudiante


def main():
    parser = argparse.ArgumentParser(description="CLI Runner para Scraper INSWEB de FIUNA")
    parser.add_argument("--cedula", "-c", type=str, help="Cédula de Identidad")
    parser.add_argument("--pin", "-p", type=str, help="PIN de INSWEB")
    args = parser.parse_args()

    print("🚀 === PIPELINE DE EXTRACCIÓN INSWEB FIUNA (MODO SILENCIOSO) ===")

    cedula = args.cedula or os.getenv("INSWEB_CI") or input("Ingresa tu Cédula de Identidad: ").strip()
    pin = args.pin or os.getenv("INSWEB_PIN") or getpass.getpass("Ingresa tu PIN (oculto): ").strip()

    if not cedula or not pin:
        print("❌ Error: Cédula y PIN son requeridos.")
        sys.exit(1)

    Base.metadata.create_all(bind=engine)
    db_gen = get_db()
    db = next(db_gen)

    try:
        resultado = ejecutar_pipeline_estudiante(cedula=cedula, pin=pin, db=db)
        conteos = resultado["conteo"]
        print("\n✅ ¡Sincronización completada con éxito!")
        print(f"📊 Cédula: {cedula}")
        print(f"   • Inscripciones guardadas: {conteos['inscripciones']}")
        print(f"   • Evaluaciones parciales guardadas: {conteos['parciales']}")
        print(f"   • Notas finales guardadas: {conteos['notas']}")
    except Exception as e:
        print(f"\n❌ Error durante el pipeline: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
