"""
Quanta V2 - CLI para Registro de Usuarios
Permite crear usuarios de manera segura desde la terminal, insertando el registro
en Auth de Supabase y en la tabla de user_profiles con su respectivo rol.
"""

import sys
import argparse
from pathlib import Path
from getpass import getpass

# Asegurar importe de los módulos del proyecto
_root = Path(__file__).resolve().parents[3]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from app.brain.db.supabase_client import get_supabase


def get_cliente_id_by_ruc(supabase, ruc: str) -> str:
    res = supabase.table("clientes").select("id").eq("ruc", ruc).execute()
    if not res.data:
        print(f"❌ Error: No se encontró ningún cliente con RUC {ruc} en la base de datos.")
        sys.exit(1)
    return res.data[0]["id"]


def main():
    parser = argparse.ArgumentParser(description="Crear un usuario en Quanta V2")
    parser.add_argument("--email", help="Correo electrónico del usuario")
    parser.add_argument("--nombre", help="Nombre completo del usuario")
    parser.add_argument("--role", choices=["admin", "accountant", "client"], help="Rol del usuario")
    parser.add_argument("--ruc", help="RUC del cliente asociado (requerido si el rol es 'client')")

    args = parser.parse_args()

    print("\n=== QUANTA V2: REGISTRO DE USUARIO ===")
    
    email = args.email or input("Email: ").strip()
    password = getpass("Password: ")
    nombre = args.nombre or input("Nombre completo: ").strip()
    
    role = args.role
    while role not in ["admin", "accountant", "client"]:
        role = input("Rol (admin/accountant/client) [client]: ").strip() or "client"

    cliente_id = None
    if role == "client":
        ruc = args.ruc or input("RUC del cliente asociado: ").strip()
        if not ruc:
            print("❌ El rol 'client' requiere un RUC obligatorio.")
            sys.exit(1)
        supabase = get_supabase()
        cliente_id = get_cliente_id_by_ruc(supabase, ruc)
    else:
        # Para admin o accountant puede ser opcional
        supabase = get_supabase()
        if args.ruc:
            cliente_id = get_cliente_id_by_ruc(supabase, args.ruc)

    print("\n⏳ Creando usuario en Supabase Auth...")
    try:
        # 1. Crear en Auth
        auth_res = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True
        })
        user_id = auth_res.user.id
        
        print(f"✅ Usuario creado en Auth con ID: {user_id}")
        print("⏳ Creando perfil con rol y permisos...")
        
        # 2. Insertar en user_profiles
        supabase.table("user_profiles").insert({
            "id": user_id,
            "email": email,
            "nombre": nombre,
            "role": role,
            "cliente_id": cliente_id,
            "activo": True
        }).execute()
        
        print("\n🎉 ¡Usuario creado y configurado exitosamente!")
        print(f"   Email: {email}")
        print(f"   Rol:   {role}")
        if cliente_id:
            print(f"   RUC:   {args.ruc or ruc}")
            
    except Exception as e:
        print(f"\n❌ Ocurrió un error al crear el usuario:\n{e}")
        # Intentar limpieza si falló el paso 2
        try:
            if 'user_id' in locals():
                supabase.auth.admin.delete_user(user_id)
                print("⚠️  Se eliminó el usuario de Auth por fallo en la creación del perfil.")
        except:
            pass

if __name__ == "__main__":
    main()
