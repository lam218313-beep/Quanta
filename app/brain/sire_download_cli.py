"""SIRE downloader CLI.

Minimal, no UI automation: downloads SUNAT SIRE "propuesta" for purchases (RCE)
and/or sales (RVIE) for a given period (YYYYMM) or a full year (YYYY).

Outputs ZIP and extracted TXT files into an output directory.

Usage examples:
  python brain/sire_download_cli.py --period 202501 --books sales purchases
  python brain/sire_download_cli.py --year 2025 --books purchases

Credentials are read from environment variables (can be loaded from .env at repo root):
  SUNAT_CLIENT_ID
  SUNAT_CLIENT_SECRET
  SUNAT_RUC
  SUNAT_USERNAME
  SUNAT_PASSWORD

Note: This tool does not print secrets.
"""

from __future__ import annotations

import argparse
import time
import os
import sys
from dataclasses import dataclass
import csv
from pathlib import Path
from typing import Iterable, Literal

from dotenv import load_dotenv


BookType = Literal["sales", "purchases"]


@dataclass(frozen=True)
class SunatClient:
    id: str = None
    name: str = ""
    ruc: str = ""
    sol_username: str = ""
    sol_password: str = ""
    api_client_id: str = ""
    api_client_secret: str = ""


@dataclass(frozen=True)
class RunItem:
    period: str
    book_type: BookType


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_env() -> None:
    root = _repo_root()
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()


def _require_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise SystemExit(
            f"Missing required env var: {name}. "
            "Set it in your environment or in .env at repo root."
        )
    return value


def _looks_like_placeholder(value: str) -> bool:
    v = (value or "").strip()
    if not v:
        return True
    lowered = v.lower()
    # Common placeholder patterns found in templates
    return any(
        token in lowered
        for token in (
            "your_",
            "<your",
            "changeme",
            "client_id_uuid",
            "client_secret",
            "example",
        )
    )


def _validate_period(period: str) -> str:
    p = period.strip()
    if len(p) != 6 or not p.isdigit():
        raise argparse.ArgumentTypeError("--period must be YYYYMM (e.g., 202501)")
    year = int(p[:4])
    month = int(p[4:])
    if year < 2000 or year > 2100:
        raise argparse.ArgumentTypeError("--period year out of range")
    if month < 1 or month > 12:
        raise argparse.ArgumentTypeError("--period month must be 01..12")
    return p


def _periods_for_year(year: int) -> list[str]:
    if year < 2000 or year > 2100:
        raise argparse.ArgumentTypeError("--year out of range")
    return [f"{year}{m:02d}" for m in range(1, 13)]


def _iter_items(periods: Iterable[str], books: Iterable[BookType]) -> list[RunItem]:
    items: list[RunItem] = []
    for period in periods:
        for book in books:
            items.append(RunItem(period=period, book_type=book))
    return items


def _ensure_import_path() -> None:
    # Allow running from repo root: `python brain/sire_download_cli.py`
    root = str(_repo_root())
    if root not in sys.path:
        sys.path.insert(0, root)


def _save_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _save_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _wait_for_ticket_with_progress(
    client,
    ticket_id: str,
    period: str,
    max_wait: int,
    poll_interval: int,
):
    start_time = time.time()
    last_message = None
    attempt = 0

    while time.time() - start_time < max_wait:
        attempt += 1
        result = client.check_ticket_status(ticket_id=ticket_id, period=period)
        status = (result.get("status") or "processing").lower()
        message = result.get("message")

        if status == "completed":
            filename = result.get("filename")
            if filename:
                print(f"Status: completed (file: {filename})")
            else:
                print("Status: completed")
            return result

        if status == "error":
            raise Exception(result.get("message") or "Ticket failed")

        # processing
        elapsed = int(time.time() - start_time)
        if message and message != last_message:
            print(f"[{attempt}] {message} (elapsed {elapsed}s)")
            last_message = message
        else:
            print(f"[{attempt}] processing (elapsed {elapsed}s)")

        time.sleep(poll_interval)

    raise TimeoutError(f"Ticket {ticket_id} timeout after {max_wait}s")


def _default_clients_file() -> Path:
    # Can be overridden via .env: SIRE_CLIENTS_FILE=clients/sunat_clients.csv
    configured = (os.getenv("SIRE_CLIENTS_FILE") or "").strip()
    if configured:
        p = Path(configured)
        if not p.is_absolute():
            p = _repo_root() / p
        return p
    return _repo_root() / "clients" / "sunat_clients.csv"


def _example_clients_file() -> Path:
    return _repo_root() / "clients" / "sunat_clients.example.csv"


def _load_clients_csv(path: Path) -> list[SunatClient]:
    if not path.exists():
        return []

    clients: list[SunatClient] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        # Detect delimiter for common variants (, ; \t |)
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except Exception:
            dialect = csv.excel

        reader = csv.DictReader(f, dialect=dialect)
        required = {
            "name",
            "ruc",
            "sol_username",
            "sol_password",
            "api_client_id",
            "api_client_secret",
        }
        fieldnames = set(reader.fieldnames or [])

        # If header is missing or invalid, fall back to a headerless 6-column format.
        # Order: name,ruc,sol_username,sol_password,api_client_id,api_client_secret
        if not reader.fieldnames or not required.issubset(fieldnames):
            f.seek(0)
            raw = csv.reader(f, dialect=dialect)
            for row in raw:
                if not row or all(not (c or "").strip() for c in row):
                    continue
                if len(row) < 6:
                    raise SystemExit(
                        f"Invalid clients CSV in {path}: expected 6 columns per row. "
                        "Order must be: name,ruc,sol_username,sol_password,api_client_id,api_client_secret"
                    )

                name, ruc, sol_username, sol_password, api_client_id, api_client_secret = [
                    (c or "").strip() for c in row[:6]
                ]
                if not name or not ruc:
                    continue
                if len(ruc) != 11 or not ruc.isdigit():
                    raise SystemExit(f"Invalid RUC in clients file ({path}): {ruc} (client {name})")

                clients.append(
                    SunatClient(
                        name=name,
                        ruc=ruc,
                        sol_username=sol_username,
                        sol_password=sol_password,
                        api_client_id=api_client_id,
                        api_client_secret=api_client_secret,
                    )
                )

            return clients

        for row in reader:
            name = (row.get("name") or "").strip()
            ruc = (row.get("ruc") or "").strip()
            sol_username = (row.get("sol_username") or "").strip()
            sol_password = (row.get("sol_password") or "").strip()
            api_client_id = (row.get("api_client_id") or "").strip()
            api_client_secret = (row.get("api_client_secret") or "").strip()

            if not name or not ruc:
                continue
            if len(ruc) != 11 or not ruc.isdigit():
                raise SystemExit(f"Invalid RUC in clients file ({path}): {ruc} (client {name})")

            clients.append(
                SunatClient(
                    name=name,
                    ruc=ruc,
                    sol_username=sol_username,
                    sol_password=sol_password,
                    api_client_id=api_client_id,
                    api_client_secret=api_client_secret,
                )
            )

    return clients


def _select_clients(clients: list[SunatClient], selectors: list[str]) -> list[SunatClient]:
    if not selectors:
        return clients

    wanted = {s.strip().lower() for s in selectors if s.strip()}
    selected = [c for c in clients if c.name.strip().lower() in wanted or c.ruc.strip().lower() in wanted]
    if not selected:
        raise SystemExit(
            "No clients matched --client selectors. "
            "Use --client <name-or-ruc> or omit --client to run all clients from CSV."
        )
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Download SUNAT SIRE propuesta (ZIP + TXT)")

    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--period", type=_validate_period, help="Period YYYYMM, e.g. 202501")
    scope.add_argument("--year", type=int, help="Full year YYYY, e.g. 2025")

    parser.add_argument(
        "--books",
        nargs="+",
        choices=["sales", "purchases"],
        default=["sales", "purchases"],
        help="Which books to download",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default=str(_repo_root() / "downloads" / "sire"),
        help="Output directory",
    )

    parser.add_argument(
        "--clients-file",
        type=str,
        default="",
        help=(
            "CSV file with multiple clients. If omitted, uses SIRE_CLIENTS_FILE from .env, "
            "or falls back to single-client SUNAT_* env vars."
        ),
    )
    parser.add_argument(
        "--client",
        action="append",
        default=[],
        help="Filter which client(s) to run by name or RUC (repeatable)",
    )
    parser.add_argument("--max-wait", type=int, default=240, help="Max seconds to wait per ticket")
    parser.add_argument("--poll-interval", type=int, default=3, help="Seconds between ticket polls")
    parser.add_argument(
        "--no-zip",
        action="store_true",
        help="Do not save ZIP; still saves TXT if possible",
    )
    parser.add_argument(
        "--no-txt",
        action="store_true",
        help="Do not extract/save TXT",
    )
    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="Do not generate XLSX (Excel) from the extracted TXT",
    )
    parser.add_argument(
        "--scrape-xml",
        action="store_true",
        help="Automatically run the web scraper to download XMLs and enrich the Excel",
    )
    parser.add_argument(
        "--scrape-limit",
        type=int,
        default=0,
        help="Limit number of XMLs to download (useful for testing)",
    )

    args = parser.parse_args()

    _ensure_import_path()
    _load_env()

    from brain.integrations.sunat_sire import SunatSireClient  # local import after sys.path fix

    # Determine clients source (DB)
    from brain.db.supabase_client import get_supabase
    
    print("Fetching clients from Supabase database...")
    supabase = get_supabase()
    response = supabase.table("clientes").select("*").execute()
    db_clients = response.data
    
    clients = []
    for row in db_clients:
        clients.append(SunatClient(
            id=row.get("id"),
            name=row.get("razon_social") or row.get("ruc"),
            ruc=row.get("ruc"),
            sol_username=row.get("usuario_sol", ""),
            sol_password=row.get("clave_sol", ""),
            api_client_id=row.get("client_id_api", ""),
            api_client_secret=row.get("client_secret_api", "")
        ))
        
    if args.client:
        clients = _select_clients(clients, list(args.client))
        print(f"Filtered to {len(clients)} clients.")
    else:
        print(f"Found {len(clients)} clients in database.")

    books: list[BookType] = [b for b in args.books]
    outdir = Path(args.outdir).expanduser().resolve()

    if args.period:
        periods = [args.period]
    else:
        periods = _periods_for_year(args.year)

    successes: list[str] = []
    failures: list[str] = []

    for sunat_client in clients:
        print(f"\n==============================")
        print(f"Client: {sunat_client.name} ({sunat_client.ruc})")
        print(f"==============================")

        # Validar que el cliente tenga credenciales API configuradas
        if not sunat_client.api_client_id or not sunat_client.api_client_secret:
            msg = (
                f"{sunat_client.ruc}:*:* -> Credenciales API faltantes. "
                "Este cliente no tiene 'client_id_api' ni 'client_secret_api' en la BD. "
                "Obtenlas desde SUNAT > Portal SIRE > Configuracion > Credenciales API y "
                "actualiza el registro en la tabla 'clientes'."
            )
            print(f"SKIP: {msg}")
            failures.append(msg)
            continue

        client = SunatSireClient(
            client_id=sunat_client.api_client_id,
            client_secret=sunat_client.api_client_secret,
            ruc=sunat_client.ruc,
            username=sunat_client.sol_username,
            password=sunat_client.sol_password,
        )

        items = _iter_items(periods, books)
        for item in items:
            label = f"{sunat_client.ruc}:{item.period}:{item.book_type}"
            print(f"\n=== {item.period}:{item.book_type} ===")

            try:
                # Output path includes client (to avoid mixing outputs)
                period_dir = outdir / sunat_client.ruc / item.period / item.book_type
                
                # Check if we can skip SIRE download
                txt_path = None
                if getattr(args, "skip_sire", False):
                    # Find the most recent txt in that directory
                    if period_dir.exists():
                        txts = list(period_dir.glob("*.txt"))
                        if txts:
                            txt_path = sorted(txts, key=os.path.getmtime)[-1]
                            print(f"Skipping SIRE download, using existing TXT: {txt_path.name}")
                            
                if not txt_path:
                    ticket_id = client.request_download(item.period, item.book_type)
                    print(f"Ticket: {ticket_id}")

                    try:
                        file_info = _wait_for_ticket_with_progress(
                            client=client,
                            ticket_id=ticket_id,
                            period=item.period,
                            max_wait=30,  # First attempt: wait max 30s
                            poll_interval=3.0,
                        )
                    except TimeoutError:
                        print("⏳ SUNAT is taking too long. Cancelling and requesting a fresh ticket to bypass queue...")
                        # By requesting a new ticket, SUNAT often returns it instantly from cache
                        ticket_id = client.request_download(item.period, item.book_type)
                        print(f"New Ticket: {ticket_id}")
                        file_info = _wait_for_ticket_with_progress(
                            client=client,
                            ticket_id=ticket_id,
                            period=item.period,
                            max_wait=240,  # Second attempt: wait up to 4 mins
                            poll_interval=4.0,
                        )
                    filename = file_info.get("filename") or f"{item.period}-{item.book_type}.zip"

                    book_code = client.BOOK_CODES[item.book_type]
                    zip_bytes = client.download_file(file_info, book_code)

                    if not args.no_zip:
                        zip_path = period_dir / filename
                        _save_bytes(zip_path, zip_bytes)
                        print(f"Saved ZIP: {zip_path}")

                    if not args.no_txt:
                        txt_content = client.extract_txt_from_zip(zip_bytes)
                        txt_name = filename
                        if txt_name.lower().endswith(".zip"):
                            txt_name = txt_name[:-4] + ".txt"
                        else:
                            txt_name = txt_name + ".txt"
                        txt_path = period_dir / txt_name
                        _save_text(txt_path, txt_content)
                        print(f"Saved TXT: {txt_path}")
                        
                        # METER LA DATA PRELIMINAR A LA BD DE SUPABASE
                        if getattr(sunat_client, "id", None):
                            from brain.db.sire_db_inserter import parse_and_insert_sire_txt
                            print(f"Inserting into Supabase DB for {sunat_client.ruc} - {item.period}")
                            parse_and_insert_sire_txt(
                                client_id=sunat_client.id, 
                                periodo=item.period, 
                                book_type=item.book_type, 
                                txt_path=txt_path
                            )
                if not args.no_excel and txt_path:
                    import subprocess
                    
                    xml_dir = None
                    if args.scrape_xml:
                        print(f"\nRunning XML scraper for {txt_path.name}...")
                        base_xml_out = _repo_root() / "downloads" / "xml"
                        cmd = [
                            sys.executable,
                            str(_repo_root() / "brain" / "sire_xml_scrape_cli.py"),
                            "--sire-txt", str(txt_path),
                            "--book", item.book_type,
                            "--outdir", str(base_xml_out),
                        ]
                        if args.scrape_limit:
                            cmd.extend(["--limit", str(args.scrape_limit)])
                        
                        env = os.environ.copy()
                        env["PYTHONIOENCODING"] = "utf-8"
                        env["PYTHONPATH"] = str(_repo_root())
                        subprocess.run(cmd, check=False, env=env)
                        xml_dir = base_xml_out / item.period / item.book_type

                    from brain.sire_txt_to_excel import convert_one  # local import

                    xlsx_path = txt_path.with_suffix(".xlsx")
                    sheet_name = f"{item.book_type}_{item.period}"[:31]
                    convert_one(
                        txt_path,
                        xlsx_path,
                        encoding="utf-8",
                        overwrite=True,
                        has_header=True,
                        sheet_name=sheet_name,
                        add_concept=True,  # Default to True to get the base CONCEPTO too
                        xml_dir=xml_dir,
                    )

                successes.append(label)

            except Exception as e:
                msg = f"{label} -> {type(e).__name__}: {e}"
                print(f"ERROR: {msg}")
                failures.append(msg)

    print("\n=== Summary ===")
    print(f"OK: {len(successes)}")
    print(f"FAIL: {len(failures)}")
    if failures:
        print("\nFailures:")
        for f in failures:
            print(f"- {f}")

    return 0 if not failures else 2


if __name__ == "__main__":
    raise SystemExit(main())
