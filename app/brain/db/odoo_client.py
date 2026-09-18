"""
Odoo XML-RPC client connection.
Uses Python's built-in xmlrpc.client.
"""
import xmlrpc.client
from config import get_settings


class OdooClient:
    """Client for Odoo XML-RPC API."""
    
    def __init__(self):
        settings = get_settings()
        self.url = settings.odoo_url
        self.db = settings.odoo_db
        self.username = settings.odoo_user
        self.password = settings.odoo_password
        self._uid = None
    
    @property
    def common(self):
        """Common endpoint for authentication."""
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
    
    @property
    def models(self):
        """Models endpoint for CRUD operations."""
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
    
    def authenticate(self) -> int:
        """
        Authenticate with Odoo and return user ID.
        """
        if self._uid is None:
            self._uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
        return self._uid
    
    def execute(self, model: str, method: str, *args, **kwargs):
        """
        Execute a method on an Odoo model.
        
        Example:
            client.execute('res.partner', 'search_read', 
                          [[['is_company', '=', True]]], 
                          {'fields': ['name', 'vat'], 'limit': 5})
        """
        uid = self.authenticate()
        return self.models.execute_kw(
            self.db, uid, self.password,
            model, method, args, kwargs
        )
    
    def search_read(self, model: str, domain: list = None, fields: list = None, limit: int = 10):
        """
        Convenience method for search_read.
        """
        domain = domain or []
        fields = fields or []
        return self.execute(
            model, 'search_read',
            [domain],
            fields=fields,
            limit=limit
        )
    
    def create(self, model: str, values: dict) -> int:
        """Create a record and return its ID."""
        return self.execute(model, 'create', [values])
    
    def version(self) -> dict:
        """Get Odoo server version (no auth required)."""
        return self.common.version()

    def create_vendor_bill(self, doc_data: dict) -> int:
        """
        Create a Vendor Bill (account.move) in Odoo from extracted data.
        
        Args:
            doc_data: Dictionary containing extracted fields:
                - ruc: Supplier RUC
                - supplier_name: Supplier Name (optional, for creation)
                - date: Invoice Date (YYYY-MM-DD)
                - total: Total Amount
                - currency: PEN or USD (default PEN)
                - ref: Invoice Number (e.g. F001-123)
        
        Returns:
            int: The ID of the created account.move
        """
        try:
            # 1. Find or Create Partner (Supplier)
            ruc = doc_data.get('ruc', {}).get('value')
            name = doc_data.get('supplier_name', {}).get('value', f"Proveedor {ruc}")
            
            if not ruc:
                raise ValueError("Cannot push to Odoo: Missing RUC")

            # Search by VAT/RUC
            partners = self.search_read(
                'res.partner', 
                [['vat', '=', ruc], ['is_company', '=', True]], 
                ['id']
            )
            
            if partners:
                partner_id = partners[0]['id']
            else:
                # Create new partner
                partner_id = self.create('res.partner', {
                    'name': name,
                    'vat': ruc,
                    'is_company': True,
                    'supplier_rank': 1,  # It's a supplier
                    'country_id': 173  # Peru ID (usually), but safe to omit if unsure
                })
            
            # 2. Prepare Invoice Line
            # For MVP, we create a single line with the total description
            total = float(doc_data.get('total', {}).get('value', 0))
            description = "Servicios Profesionales (Auto-Generated)"
            
            invoice_line = {
                'name': description,
                'quantity': 1,
                'price_unit': total,
            }
            
            # 3. Create Account Move (Invoice)
            invoice_date = doc_data.get('date', {}).get('value')
            # Convert DD/MM/YYYY to YYYY-MM-DD if needed
            if invoice_date and '/' in invoice_date:
                parts = invoice_date.split('/')
                if len(parts) == 3:
                    invoice_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
            
            ref = f"{doc_data.get('serial', {}).get('value', '')}-{doc_data.get('number', {}).get('value', '')}"
            
            move_vals = {
                'move_type': 'in_invoice', # Vendor Bill
                'partner_id': partner_id,
                'invoice_date': invoice_date,
                'ref': ref,
                'invoice_line_ids': [(0, 0, invoice_line)],  # Magic command (0,0,{vals}) to create linked record
            }
            
            move_id = self.create('account.move', move_vals)
            return move_id

        except Exception as e:
            raise Exception(f"Odoo Injection Failed: {str(e)}")


# Singleton
_odoo_client: OdooClient | None = None


def get_odoo() -> OdooClient:
    """Get or create Odoo client singleton."""
    global _odoo_client
    if _odoo_client is None:
        _odoo_client = OdooClient()
    return _odoo_client
