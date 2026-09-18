"""
Agente de Clasificación Contable con IA.

Lee los comprobantes enriquecidos (con glosas/ítems) de Supabase,
los envía a la IA con el contexto del Plan Contable y el Rubro de la empresa,
y guarda la cuenta contable asignada directamente en la base de datos.

Uso:
    python app/brain/db/ai_classifier.py
    python app/brain/db/ai_classifier.py --limit 50
    python app/brain/db/ai_classifier.py --book purchases
    python app/brain/db/ai_classifier.py --book sales
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Literal


BookType = Literal["purchases", "sales", "all"]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _ensure_import_path() -> None:
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)


def _load_env() -> None:
    from dotenv import load_dotenv
    env_path = _repo_root() / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()


def _get_plan_contable_datos(supabase) -> tuple[str, dict[str, str]]:
    """
    Obtiene las cuentas del PCGE.
    Devuelve:
      - Un string con el resumen (nivel 2, 3 y 4) para la IA.
      - Un diccionario completo con codigo -> descripcion para guardar en BD.
    """
    lineas = []
    diccionario = {}
    
    offset = 0
    limit = 1000
    while True:
        resp = supabase.table("plan_contable") \
            .select("codigo, descripcion, nivel") \
            .order("codigo") \
            .range(offset, offset + limit - 1) \
            .execute()
            
        data = resp.data
        if not data:
            break
            
        for row in data:
            codigo = row['codigo']
            descripcion = row['descripcion']
            diccionario[codigo] = descripcion
            # Incluir SOLO cuentas de nivel 4 (exactamente 4 dígitos)
            if row['nivel'] == 4:
                lineas.append(f"{codigo} - {descripcion}")
                
        if len(data) < limit:
            break
            
        offset += limit

    return "\n".join(lineas), diccionario


def _clasificar_con_openai(
    api_key: str,
    rubro_empresa: str,
    tipo_libro: str,
    glosas: list[str],
    plan_contable_resumen: str,
    es_personalizado: bool = False,
) -> list[tuple[str | None, str | None]]:
    """
    Llama a OpenAI gpt-4o-mini para clasificar una lista de glosas.
    """
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    tipo_texto = "compras/gastos" if tipo_libro == "COMPRAS" else "ventas/ingresos"
    elemento_esperado = "Elemento 6 (Gastos por naturaleza) o Elemento 3 (Activos)" if tipo_libro == "COMPRAS" else "Elemento 7 (Ingresos)"

    system_prompt = (
        "Eres un contador publico peruano experto en el Plan Contable General Empresarial (PCGE). "
        "Respondes UNICAMENTE con JSON valido, sin texto adicional ni markdown."
    )

    if tipo_libro == "COMPRAS" and not es_personalizado:
        # EL USUARIO HA PEDIDO RESTRINGIR A ELEMENTOS 6 Y 3 PARA COMPRAS
        lineas_plan = [linea for linea in plan_contable_resumen.split('\n') if linea.strip().startswith('6') or linea.strip().startswith('3')]
        plan_contable_resumen = '\n'.join(lineas_plan)

    if tipo_libro == "COMPRAS":
        lista_categorias = """   - Costo (ej. mercadería para venta, materia prima)
   - Gasto (ej. servicios, suministros consumidos, planillas)
   - Activo (ej. compra de computadoras, maquinaria, vehículos)
   - No deducibles (ej. multas, gastos sin sustento)
   - Suministros y materiales no auxiliares (ej. repuestos específicos)"""
    else:
        lista_categorias = """   - Venta de Bienes (ej. venta de mercadería, productos terminados)
   - Prestacion de Servicios (ej. honorarios, servicios brindados)
   - Otros Ingresos (ej. intereses, venta de activos fijos)"""

    if es_personalizado:
        regla_2 = "2. Usa EXCLUSIVAMENTE cuentas de la lista personalizada proporcionada. No puedes inventar cuentas."
        regla_3 = "3. La cuenta que elijas DEBE existir EXACTAMENTE en la lista personalizada proporcionada."
        regla_7 = "7. SI NO SABES a qué cuenta mandar una compra o gasto porque no coincide con ninguna cuenta de la lista personalizada, usa SIEMPRE '6599' (Otros gastos de gestión)."
        plan_titulo = "CUENTAS CONTABLES PERSONALIZADAS (Solo usar códigos de esta lista):"
    else:
        regla_2 = "2. Usa EXCLUSIVAMENTE cuentas de EXACTAMENTE 4 DÍGITOS. Está terminantemente prohibido inventar cuentas."
        regla_3 = "3. La cuenta que elijas DEBE existir en la lista proporcionada en PLAN CONTABLE DE 4 DÍGITOS."
        regla_7 = "7. SI NO SABES a qué cuenta mandar una compra o gasto, usa SIEMPRE la cuenta 6599 (Otros gastos de gestión)."
        plan_titulo = "PLAN CONTABLE DE 4 DÍGITOS (Solo usar códigos de esta lista):"

    user_prompt = f"""RUBRO DE LA EMPRESA: {rubro_empresa}
TIPO DE COMPROBANTES: {tipo_texto}

Tu tarea: asignar a cada item el codigo de cuenta PCGE mas apropiado y la CATEGORIA a la que pertenece.

REGLAS CRÍTICAS:
1. Usa cuentas del {elemento_esperado}.
{regla_2}
{regla_3}
4. Considera el RUBRO. Si la empresa VENDE el producto -> es Costo/Mercaderia. Si es un servicio para el negocio (alquiler, mantenimiento, honorarios, comisiones bancarias, fletes) -> busca la cuenta especifica de Gasto por Servicios de Terceros.
5. Para la CATEGORIA, debes elegir OBLIGATORIAMENTE una de las siguientes:
{lista_categorias}
6. RAZONAMIENTO: Antes de dar el código, escribe una breve justificación en 'razonamiento' evaluando de qué trata el servicio/producto.
{regla_7}

{plan_titulo}
{plan_contable_resumen}

ITEMS A CLASIFICAR:
{chr(10).join(f"{i+1}. {g}" for i, g in enumerate(glosas))}

Responde con este JSON exacto:
{{
  "clasificaciones": [
    {{"item": 1, "razonamiento": "Servicio de transporte interprovincial", "codigo": "6311", "categoria": "Gasto"}},
    {{"item": 2, "razonamiento": "Lavado de camioneta corresponde a mantenimiento", "codigo": "6343", "categoria": "Gasto"}}
  ]
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        text = response.choices[0].message.content.strip()
        data = json.loads(text)
        clasificaciones = data.get("clasificaciones", [])

        resultados = [(None, None)] * len(glosas)
        for c in clasificaciones:
            idx = c.get("item", 0) - 1
            if 0 <= idx < len(glosas):
                codigo = str(c.get("codigo", "")).strip()
                categoria = str(c.get("categoria", "")).strip()
                resultados[idx] = (codigo, categoria)

        return resultados

    except Exception as e:
        print(f"  [ERROR OpenAI] {e}")
        return [(None, None)] * len(glosas)


def main() -> int:
    parser = argparse.ArgumentParser(description="Clasificador contable con IA")
    parser.add_argument("--limit", type=int, default=200, help="Max comprobantes a procesar")
    parser.add_argument(
        "--book",
        choices=["purchases", "sales", "all"],
        default="all",
        help="Libro a clasificar",
    )
    parser.add_argument("--ruc", type=str, help="RUC de la empresa para filtrar")
    parser.add_argument("--periodo", type=str, help="Periodo a enriquecer (ej: 202604)")
    args = parser.parse_args()

    _ensure_import_path()
    _load_env()

    from app.brain.db.supabase_client import get_supabase

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: Se necesita OPENAI_API_KEY en el .env")
        return 1

    supabase = get_supabase()

    print("Cargando resumen del Plan Contable...")
    plan_contable_resumen, diccionario_cuentas = _get_plan_contable_datos(supabase)
    print(f"  Cuentas cargadas en diccionario: {len(diccionario_cuentas)}")

    # Obtener todos los clientes activos con su rubro
    clientes_resp = supabase.table("clientes").select("id, razon_social, ruc, rubro, cuentas_contables").eq("activo", True).execute()
    clientes = {c["id"]: c for c in clientes_resp.data}

    total_clasificados = 0
    total_errores = 0

    for libro in (["purchases", "sales"] if args.book == "all" else [args.book]):
        tabla = "sire_preliminar_compras" if libro == "purchases" else "sire_preliminar_ventas"
        tipo_libro = "COMPRAS" if libro == "purchases" else "VENTAS"

        print(f"\n=== Procesando {tipo_libro} ===")

        # Resolve cliente_id from RUC if provided
        cliente_id_filter = None
        if args.ruc:
            r_client = supabase.table("clientes").select("id").eq("ruc", args.ruc).execute()
            if not r_client.data:
                print(f"Error: No se encontró cliente con RUC {args.ruc}")
                return 1
            cliente_id_filter = r_client.data[0]["id"]
            
        # Buscar registros sin cuenta_contable asignada que tengan descripcion_comprobante
        query = supabase.table(tabla) \
            .select("id, cliente_id, descripcion_comprobante") \
            .is_("cuenta_contable", "null") \
            .not_.is_("descripcion_comprobante", "null")
            
        if cliente_id_filter:
            query = query.eq("cliente_id", cliente_id_filter)
            
        if args.periodo:
            query = query.eq("periodo", args.periodo)
            
        resp = query.limit(args.limit).execute()

        registros = [r for r in resp.data if r.get("descripcion_comprobante", "").strip()]
        print(f"  Registros pendientes de clasificar: {len(registros)}")

        if not registros:
            print("  Nada que clasificar.")
            continue

        # Agrupar por cliente para usar el rubro correcto
        por_cliente: dict[str, list[dict]] = {}
        for r in registros:
            cid = r["cliente_id"]
            por_cliente.setdefault(cid, []).append(r)

        for cliente_id, regs in por_cliente.items():
            cliente = clientes.get(cliente_id, {})
            rubro = cliente.get("rubro") or "empresa comercial general"
            razon = cliente.get("razon_social", "Empresa")
            cuentas_cliente = cliente.get("cuentas_contables")

            if cuentas_cliente and cuentas_cliente.strip():
                plan_contable_usar = cuentas_cliente.replace(",", "\n")
                es_personalizado = True
                
                # Añadir descripciones al diccionario general desde las cuentas personalizadas
                import re
                for cuenta_line in cuentas_cliente.split(','):
                    match = re.search(r'(\d+)\s*\(([^)]+)\)', cuenta_line)
                    if match:
                        codigo, desc = match.groups()
                        diccionario_cuentas[codigo.strip()] = desc.strip()
            else:
                plan_contable_usar = plan_contable_resumen
                es_personalizado = False

            print(f"\n  Cliente: {razon} | Rubro: {rubro} | Cuentas personalizadas: {es_personalizado}")
            print(f"  Comprobantes a clasificar: {len(regs)}")

            # Procesar en lotes de 20 para no saturar el prompt
            LOTE = 20
            for i in range(0, len(regs), LOTE):
                lote = regs[i: i + LOTE]
                glosas = [r["descripcion_comprobante"] for r in lote]

                print(f"  Enviando lote {i // LOTE + 1} ({len(lote)} items) a OpenAI gpt-4o-mini...")
                resultados_ia = _clasificar_con_openai(
                    api_key=api_key,
                    rubro_empresa=rubro,
                    tipo_libro=tipo_libro,
                    glosas=glosas,
                    plan_contable_resumen=plan_contable_usar,
                    es_personalizado=es_personalizado,
                )

                # Actualizar en BD
                for reg, (codigo, categoria) in zip(lote, resultados_ia):
                    if codigo:
                        # ── Garantizar 4 dígitos ──────────────────────────────────────────
                        # Si la IA devolvió 2 o 3 dígitos, buscar el primer hijo de 4 dígitos
                        # en el diccionario del plan contable.
                        if len(codigo) < 4:
                            prefijo = codigo
                            hijo = next(
                                (k for k in sorted(diccionario_cuentas.keys())
                                 if k.startswith(prefijo) and len(k) == 4),
                                None
                            )
                            if hijo:
                                print(f"    [4-dig] {codigo} → {hijo} (expandido automáticamente)")
                                codigo = hijo
                            else:
                                # Fallback: buscar cualquier hijo más específico disponible
                                hijo = next(
                                    (k for k in sorted(diccionario_cuentas.keys())
                                     if k.startswith(prefijo) and len(k) > len(prefijo)),
                                    codigo  # si no hay nada, dejar como está
                                )
                                if hijo != codigo:
                                    print(f"    [4-dig] {codigo} → {hijo} (fallback a cuenta más específica)")
                                    codigo = hijo

                        descripcion = diccionario_cuentas.get(codigo, "")
                        supabase.table(tabla) \
                            .update({
                                "cuenta_contable": codigo,
                                "descripcion_cuenta": descripcion,
                                "categoria": categoria
                            }) \
                            .eq("id", reg["id"]) \
                            .execute()
                        total_clasificados += 1
                    else:
                        total_errores += 1

                # Pausa para no saturar la API
                time.sleep(1)

    print(f"\n=== Resumen Final ===")
    print(f"Clasificados exitosamente: {total_clasificados}")
    print(f"Sin clasificar (error IA): {total_errores}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
