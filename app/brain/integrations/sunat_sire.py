"""
SUNAT SIRE API Client
Implements OAuth2 authentication and voucher download for both:
- RVIE (Registro de Ventas e Ingresos Electrónico)
- RCE (Registro de Compras Electrónico)

Based on official SUNAT API manuals.
"""

import requests
import time
import zipfile
import io
from typing import Dict, List, Optional, Literal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SunatSireClient:
    """
    Client for SUNAT SIRE API (Sistema Integrado de Registro Electrónico)
    
    Handles:
    1. OAuth2 authentication (Client Credentials + Password Grant)
    2. Ticket-based async downloads
    3. ZIP file extraction
    4. TXT parsing
    """
    
    # API Endpoints
    AUTH_URL = "https://api-seguridad.sunat.gob.pe/v1/clientessol/{client_id}/oauth2/token/"
    BASE_URL = "https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros"
    
    # Book codes
    BOOK_CODES = {
        "sales": "140000",      # RVIE - Registro de Ventas
        "purchases": "080000"   # RCE - Registro de Compras
    }
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        ruc: str,           # RUC (11 dígitos)
        username: str,      # Usuario SOL (ej: BABILONI)
        password: str       # Clave SOL
    ):
        """
        Initialize SIRE client with OAuth2 credentials
        
        Args:
            client_id: Client ID from SOL SUNAT
            client_secret: Client Secret from SOL SUNAT
            ruc: RUC (11 digits)
            username: SOL username (e.g., BABILONI, MODDATOS)
            password: SOL password
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.ruc = ruc
        self.username = username
        self.password = password
        # OAuth2 requires RUC + Username concatenated
        self.oauth_username = f"{ruc}{username}"
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    def _is_token_valid(self) -> bool:
        """Check if current token is still valid"""
        if not self.access_token or not self.token_expires_at:
            return False
        return datetime.now().timestamp() < self.token_expires_at
    
    def authenticate(self) -> str:
        """
        Get OAuth2 access token using Client Credentials + Password Grant
        
        Returns:
            Access token string
        
        Raises:
            requests.HTTPError: If authentication fails
        """
        if self._is_token_valid():
            logger.info("Using cached access token")
            return self.access_token
        
        url = self.AUTH_URL.format(client_id=self.client_id)
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "password",
            "scope": "https://api-sire.sunat.gob.pe",  # Correct scope for SIRE API
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.oauth_username,  # RUC + Username concatenated
            "password": self.password
        }
        
        logger.info(f"Authenticating with SUNAT for RUC: {self.ruc}, User: {self.username}")
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            # Token expires in 3600 seconds (1 hour), set expiry to 55 minutes for safety
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now().timestamp() + (expires_in - 300)
            
            logger.info("Successfully authenticated with SUNAT")
            return self.access_token
            
        except requests.HTTPError as e:
            logger.error(f"Authentication failed: {e.response.text if e.response else str(e)}")
            raise
    
    def request_download(
        self,
        period: str,
        book_type: Literal["sales", "purchases"]
    ) -> str:
        """
        Request download of voucher proposal (returns ticket ID)
        
        Args:
            period: Tax period in format YYYYMM (e.g., "202401")
            book_type: "sales" for RVIE or "purchases" for RCE
        
        Returns:
            Ticket ID for polling
        
        Raises:
            ValueError: If book_type is invalid
            requests.HTTPError: If request fails
        """
        if book_type not in self.BOOK_CODES:
            raise ValueError(f"Invalid book_type: {book_type}. Must be 'sales' or 'purchases'")
        
        # Ensure we have a valid token
        token = self.authenticate()
        
        if book_type == "sales":
            # RVIE - Ventas
            endpoint = f"{self.BASE_URL}/rvie/propuesta/web/propuesta/{period}/exportapropuesta"
            params = {
                "codTipoArchivo": "0"  # 0 = TXT, 1 = XLS
            }
        else:
            # RCE - Compras
            endpoint = f"{self.BASE_URL}/rce/propuesta/web/propuesta/{period}/exportacioncomprobantepropuesta"
            params = {
                "codTipoArchivo": "0",  # 0 = TXT, 1 = CSV
                "codOrigenEnvio": "2"   # 2 = Servicio API (Obligatorio para compras)
            }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.info(f"Requesting {book_type} download for period {period}")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Use GET for both
                response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                
                if response.status_code == 429 and attempt < max_retries - 1:
                    sleep_time = 5 * (attempt + 1)
                    logger.warning(f"429 Too Many Requests. Retrying in {sleep_time}s (attempt {attempt+1}/{max_retries})...")
                    time.sleep(sleep_time)
                    continue
                    
                response.raise_for_status()
                
                data = response.json()
                
                # Check for error response
                if "cod" in data and data["cod"] != "0000":
                    raise Exception(f"SUNAT error {data.get('cod')}: {data.get('msg', 'Unknown error')}")
                
                ticket_id = data.get("numTicket")
                if not ticket_id:
                    raise Exception(f"No ticket ID in response: {data}")
                
                logger.info(f"Download requested successfully. Ticket ID: {ticket_id}")
                
                return ticket_id
                
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 429 and attempt < max_retries - 1:
                    sleep_time = 5 * (attempt + 1)
                    logger.warning(f"429 Too Many Requests HTTPError. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                    continue
                logger.error(f"Download request failed: {e.response.text if e.response else str(e)}")
                raise
        
        raise Exception("Max retries reached for download request")
    
    def check_ticket_status(self, ticket_id: str, period: str, *, per_page: int = 200, max_pages: int = 5) -> Dict:
        """
        Check status of a download ticket via Service 5.16 (Search Tickets by Period)
        
        Args:
            ticket_id: Ticket ID to find
            period: Period YYYYMM
        
        Returns:
            Dict: status info
        """
        token = self.authenticate()
        
        # Service 5.16 URL
        url = f"{self.BASE_URL}/rvierce/gestionprocesosmasivos/web/masivo/consultaestadotickets"
        
        # SUNAT returns a paginated list; in busy accounts a ticket might not be in the first 50.
        # We scan multiple pages with a larger page size to find the exact ticket.
        params = {
            "perIni": period,
            "perFin": period,
            "page": "1",
            "perPage": str(per_page),
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        try:
            for page in range(1, max_pages + 1):
                params["page"] = str(page)
                logger.debug(f"Polling ticket {ticket_id} for period {period} (page {page})...")
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                registros = data.get("registros", [])

                target_record = next((r for r in registros if r.get("numTicket") == ticket_id), None)
                if target_record:
                    break

            if not target_record:
                return {
                    "status": "processing",
                    "message": f"Ticket not found yet (scanned {max_pages} page(s))",
                }
                
            # Check status
            # codEstadoProceso: 2/Terminado? Manual says "03" or "04"? 
            # Actually Manual 5.16 says "codEstadoProceso". 
            # Valid codes: 1=Proceso, 2=Terminado, 3=Error? 
            # In previous tests successful response showed "desEstadoProceso": "Terminado"
            
            status_desc = target_record.get("desEstadoProceso", "")
            status_code = target_record.get("codEstadoProceso")
            
            if status_code == "02" or status_desc.upper() == "TERMINADO":
                # Success
                # Get filename from archivoReporte
                archivos = target_record.get("archivoReporte", [])
                if not archivos:
                     return {"status": "error", "message": "Ticket completed but no file attached"}
                
                # Usually the first file
                file_info = archivos[0]
                return {
                    "status": "completed",
                    "filename": file_info.get("nomArchivoReporte"),
                    "codTipoArchivoReporte": file_info.get("codTipoArchivoReporte"),
                    "codProceso": target_record.get("codProceso"),
                    "perTributario": target_record.get("perTributario"),
                    "numTicket": ticket_id,
                    "message": "Download ready"
                }
            elif status_code == "03": # Error
                 return {"status": "error", "message": f"Error processing: {status_desc}"}
            else:
                 return {"status": "processing", "message": f"Status: {status_desc} ({status_code})"}
                 
        except requests.HTTPError as e:
            logger.error(f"Ticket check failed: {e.response.text if e.response else str(e)}")
            # Don't raise, just return processing/error to keep polling loop alive if transient
            return {"status": "processing", "message": "Transient error checking status"}

    def wait_for_ticket(
        self,
        ticket_id: str,
        period: str, # ADDED period argument
        max_wait: int = 300,
        poll_interval: int = 10
    ) -> Dict:
        """
        Poll ticket until ready or timeout. Returns dict with filename and other download params.
        """
        start_time = time.time()
        logger.info(f"Waiting for ticket {ticket_id} for period {period}")
        
        while time.time() - start_time < max_wait:
            result = self.check_ticket_status(ticket_id, period)
            
            if result["status"] == "completed":
                logger.info(f"Ticket ready. File: {result['filename']}")
                return result
            elif result["status"] == "error":
                raise Exception(f"Ticket failed: {result['message']}")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Ticket {ticket_id} timeout")

    def download_file(self, file_info: Dict, book_code: str) -> bytes:
        """
        Download ZIP file using appropriate service
        RVIE (140000): Service 5.17
        RCE (080000): Service 5.32 (presumed, via rce path)
        """
        token = self.authenticate()
        
        # Use unified path for both books (RVIE and RCE)
        # Service 5.17 and 5.32 seem to share the same endpoint structure
        base_path = "rvierce/gestionprocesosmasivos/web/masivo/archivoreporte"
        
        url = f"{self.BASE_URL}/{base_path}"
        
        # Mandatory parameters for Service 5.17/5.32
        params = {
            "nomArchivoReporte": file_info["filename"],
            "codTipoArchivoReporte": file_info.get("codTipoArchivoReporte") or "01",
            "codLibro": book_code,
            "codProceso": file_info.get("codProceso"),
            "perTributario": file_info.get("perTributario"),
            "numTicket": file_info.get("numTicket")
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        
        logger.info(f"Downloading {file_info['filename']} from {url} with params: {params}")
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=60)
            response.raise_for_status()
            return response.content
        except requests.HTTPError as e:
            logger.error(f"Download failed: {e.response.text if e.response else str(e)}")
            raise

    def extract_txt_from_zip(self, zip_data: bytes) -> str:
        """
        Extract TXT content from ZIP file
        """
        import io, zipfile
        zip_buffer = io.BytesIO(zip_data)
        
        with zipfile.ZipFile(zip_buffer) as z:
            txt_files = [f for f in z.namelist() if f.endswith('.txt')]
            
            if not txt_files:
                raise Exception("No TXT file found in ZIP")
            
            # Read first TXT file
            txt_content = z.read(txt_files[0]).decode('utf-8', errors='replace')
            logger.info(f"Extracted TXT file: {txt_files[0]} ({len(txt_content)} chars)")
            
            return txt_content
    
    def parse_vouchers(self, txt_content: str, book_type: Literal["sales", "purchases"]) -> List[Dict]:
        """
        Parse TXT content into structured voucher data
        """
        vouchers = []
        
        for line_num, line in enumerate(txt_content.strip().split('\n'), 1):
            if not line.strip():
                continue
            
            try:
                fields = line.split('|')
                
                # Common fields for both sales and purchases
                voucher = {
                    "line_number": line_num,
                    "ruc_issuer": fields[0] if len(fields) > 0 else None,
                    "series": fields[1] if len(fields) > 1 else None,
                    "number": fields[2] if len(fields) > 2 else None,
                    "date": fields[3] if len(fields) > 3 else None,
                    "type": fields[4] if len(fields) > 4 else None,
                    "taxable_base": float(fields[7]) if len(fields) > 7 and fields[7] else 0.0,
                    "igv": float(fields[8]) if len(fields) > 8 and fields[8] else 0.0,
                    "total": float(fields[9]) if len(fields) > 9 and fields[9] else 0.0,
                    "book_type": book_type,
                    "raw_line": line
                }
                
                # Add customer/supplier info
                if book_type == "sales":
                    voucher["ruc_customer"] = fields[5] if len(fields) > 5 else None
                    voucher["customer_name"] = fields[6] if len(fields) > 6 else None
                else:  # purchases
                    voucher["ruc_supplier"] = fields[5] if len(fields) > 5 else None
                    voucher["supplier_name"] = fields[6] if len(fields) > 6 else None
                
                vouchers.append(voucher)
                
            except Exception as e:
                logger.warning(f"Failed to parse line {line_num}: {str(e)}")
                continue
        
        logger.info(f"Parsed {len(vouchers)} vouchers from TXT")
        return vouchers

    def download_vouchers(
        self,
        period: str,
        book_type: Literal["sales", "purchases"],
        max_wait: int = 300
    ) -> List[Dict]:
        """
        Complete flow: Request -> Poll -> Download -> Parse
        """
        logger.info(f"Starting {book_type} download for {period}")
        
        book_code = self.BOOK_CODES[book_type]
        
        # 1. Request
        ticket_id = self.request_download(period, book_type)
        
        # 2. Poll
        # Note: ticket check needs period
        file_info = self.wait_for_ticket(ticket_id, period, max_wait)
        logger.info(f"Ticket Ready Info: {file_info}")
        
        # 3. Download
        zip_data = self.download_file(file_info, book_code)
        
        # 4. Extract
        txt_content = self.extract_txt_from_zip(zip_data)
        
        # 5. Parse
        vouchers = self.parse_vouchers(txt_content, book_type)
        
        return vouchers

    def upload_replacement(self, period: str, book_type: Literal["sales", "purchases"], zip_path: str) -> str:
        """
        Upload a ZIP file to replace the SUNAT proposal.
        
        Args:
            period: Tax period in format YYYYMM
            book_type: 'sales' or 'purchases'
            zip_path: Absolute path to the .zip file containing the .txt
            
        Returns:
            Ticket ID for tracking the upload status
        """
        token = self.authenticate()
        
        # Based on standard SIRE API paths for replacement:
        if book_type == "sales":
            endpoint = f"{self.BASE_URL}/rvie/propuesta/web/reemplaza"
        else:
            endpoint = f"{self.BASE_URL}/rce/propuesta/web/reemplaza"
            
        import os
        filename = os.path.basename(zip_path)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        logger.info(f"Uploading replacement ZIP for {book_type} ({period}) to {endpoint}")
        
        try:
            with open(zip_path, 'rb') as f:
                files = {
                    'archivo': (filename, f, 'application/zip')
                }
                # Parameters like nomArchivo might be required as query params or form data.
                data = {
                    'nomArchivo': filename,
                    'perTributario': period
                }
                response = requests.post(endpoint, headers=headers, files=files, data=data, timeout=60)
                
                # If specific endpoint gives 404, fallback to generic
                if response.status_code in [404, 405]:
                    logger.warning(f"Endpoint {endpoint} failed with {response.status_code}. Trying generic endpoint.")
                    f.seek(0)
                    generic_endpoint = f"{self.BASE_URL}/rvierce/receptorpropuesta/web/propuesta"
                    response = requests.post(generic_endpoint, headers=headers, files=files, data=data, timeout=60)

                response.raise_for_status()
                resp_data = response.json()
                
                if "cod" in resp_data and resp_data["cod"] != "0000":
                    raise Exception(f"SUNAT error {resp_data.get('cod')}: {resp_data.get('msg', 'Unknown error')}")
                
                ticket_id = resp_data.get("numTicket")
                if not ticket_id:
                    raise Exception(f"No ticket ID in response: {resp_data}")
                    
                logger.info(f"Upload successful. Ticket ID: {ticket_id}")
                return ticket_id
                
        except requests.HTTPError as e:
            logger.error(f"Upload request failed: {e.response.text if e.response else str(e)}")
            raise

# Example usage
if __name__ == "__main__":
    import os
    logging.basicConfig(level=logging.INFO)
    
    # Initialize client with credentials from .env
    client = SunatSireClient(
        client_id=os.getenv("SUNAT_CLIENT_ID"),
        client_secret=os.getenv("SUNAT_CLIENT_SECRET"),
        ruc=os.getenv("SUNAT_RUC"),
        username=os.getenv("SUNAT_USERNAME"),
        password=os.getenv("SUNAT_PASSWORD")
    )
    
    # Download sales vouchers for January 2024
    sales_vouchers = client.download_vouchers("202401", "sales")
    print(f"Downloaded {len(sales_vouchers)} sales vouchers")
    
    # Download purchase vouchers for January 2024
    purchase_vouchers = client.download_vouchers("202401", "purchases")
    print(f"Downloaded {len(purchase_vouchers)} purchase vouchers")
