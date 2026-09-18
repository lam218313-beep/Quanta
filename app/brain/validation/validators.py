"""
Validation Engine for Peruvian Accounting Rules.
Implements SUNAT RUC validation, bancarization checks, and linking rules.
"""
import re
import httpx
from typing import Optional
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""
    rule: str
    passed: bool
    message: str
    severity: str  # 'error', 'warning', 'info'
    
    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "passed": self.passed,
            "message": self.message,
            "severity": self.severity
        }


class RUCValidator:
    """
    Validates Peruvian RUC (Registro Único de Contribuyentes).
    Uses SUNAT consultation API for real-time validation.
    """
    
    # RUC types
    RUC_TYPES = {
        '10': 'Persona Natural',
        '15': 'Persona Natural (no domiciliada)',
        '17': 'Persona Natural (no domiciliada)',
        '20': 'Persona Jurídica',
    }
    
    def validate_format(self, ruc: str) -> ValidationResult:
        """Validate RUC format (11 digits, starts with 10 or 20)."""
        ruc = ruc.strip() if ruc else ""
        
        if not ruc:
            return ValidationResult(
                rule="ruc_format",
                passed=False,
                message="RUC no proporcionado",
                severity="error"
            )
        
        if not re.match(r'^\d{11}$', ruc):
            return ValidationResult(
                rule="ruc_format",
                passed=False,
                message=f"RUC debe tener 11 dígitos (tiene {len(ruc)})",
                severity="error"
            )
        
        prefix = ruc[:2]
        if prefix not in self.RUC_TYPES:
            return ValidationResult(
                rule="ruc_format",
                passed=False,
                message=f"RUC debe comenzar con 10 o 20, no {prefix}",
                severity="error"
            )
        
        return ValidationResult(
            rule="ruc_format",
            passed=True,
            message=f"RUC válido - {self.RUC_TYPES[prefix]}",
            severity="info"
        )
    
    def validate_checksum(self, ruc: str) -> ValidationResult:
        """
        Validate RUC using Peru's checksum algorithm.
        The last digit is a verification digit calculated from the first 10.
        """
        ruc = ruc.strip()
        if len(ruc) != 11:
            return ValidationResult(
                rule="ruc_checksum",
                passed=False,
                message="RUC debe tener 11 dígitos",
                severity="error"
            )
        
        # Weights for checksum calculation
        weights = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        
        try:
            # Calculate weighted sum
            total = sum(int(ruc[i]) * weights[i] for i in range(10))
            remainder = total % 11
            check_digit = 11 - remainder if remainder != 0 else 0
            
            # Handle special cases
            if check_digit == 10:
                check_digit = 0
            elif check_digit == 11:
                check_digit = 1
            
            actual_check = int(ruc[10])
            
            if check_digit == actual_check:
                return ValidationResult(
                    rule="ruc_checksum",
                    passed=True,
                    message="Dígito verificador válido",
                    severity="info"
                )
            else:
                return ValidationResult(
                    rule="ruc_checksum",
                    passed=False,
                    message=f"Dígito verificador inválido (esperado: {check_digit}, actual: {actual_check})",
                    severity="error"
                )
        except (ValueError, IndexError):
            return ValidationResult(
                rule="ruc_checksum",
                passed=False,
                message="Error al calcular dígito verificador",
                severity="error"
            )
    
    async def validate_sunat(self, ruc: str) -> ValidationResult:
        """
        Validate RUC against SUNAT's public API.
        Note: Uses a free public API proxy as direct SUNAT requires captcha.
        """
        # First validate format and checksum locally
        format_result = self.validate_format(ruc)
        if not format_result.passed:
            return format_result
        
        checksum_result = self.validate_checksum(ruc)
        if not checksum_result.passed:
            return checksum_result
        
        # Query public API (using apis.net.pe - free tier)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"https://api.apis.net.pe/v1/ruc?numero={ruc}",
                    headers={"Accept": "application/json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    nombre = data.get('nombre', 'Desconocido')
                    estado = data.get('estado', 'Desconocido')
                    
                    if estado.upper() == 'ACTIVO':
                        return ValidationResult(
                            rule="ruc_sunat",
                            passed=True,
                            message=f"RUC activo: {nombre}",
                            severity="info"
                        )
                    else:
                        return ValidationResult(
                            rule="ruc_sunat",
                            passed=False,
                            message=f"RUC no activo ({estado}): {nombre}",
                            severity="warning"
                        )
                else:
                    # API failed, but local validation passed
                    return ValidationResult(
                        rule="ruc_sunat",
                        passed=True,
                        message="RUC válido (verificación SUNAT no disponible)",
                        severity="warning"
                    )
        except Exception as e:
            # API unavailable, rely on local validation
            return ValidationResult(
                rule="ruc_sunat",
                passed=True,
                message=f"RUC válido localmente (SUNAT API error: {str(e)[:50]})",
                severity="warning"
            )
    
    def validate(self, ruc: str) -> ValidationResult:
        """Synchronous validation (format + checksum only)."""
        format_result = self.validate_format(ruc)
        if not format_result.passed:
            return format_result
        return self.validate_checksum(ruc)


class BancarizationValidator:
    """
    Validates bancarization requirements per SUNAT regulations.
    
    Key rules:
    - Transactions >= S/ 2,000 (or $500 USD) must use banking methods
    - Cash payments above threshold are not deductible
    """
    
    THRESHOLD_PEN = 2000.00  # S/ 2,000
    THRESHOLD_USD = 500.00   # $500
    
    def validate(self, amount: float, has_voucher: bool, currency: str = "PEN") -> ValidationResult:
        """
        Check if transaction requires bancarization proof.
        
        Args:
            amount: Transaction amount
            has_voucher: Whether a bank voucher is linked
            currency: PEN or USD
        """
        threshold = self.THRESHOLD_PEN if currency == "PEN" else self.THRESHOLD_USD
        
        if amount < threshold:
            return ValidationResult(
                rule="bancarization",
                passed=True,
                message=f"Monto ({currency} {amount:,.2f}) menor al límite de bancarización",
                severity="info"
            )
        
        if has_voucher:
            return ValidationResult(
                rule="bancarization",
                passed=True,
                message=f"Bancarización cumplida (voucher vinculado)",
                severity="info"
            )
        else:
            return ValidationResult(
                rule="bancarization",
                passed=False,
                message=f"REQUIERE BANCARIZACIÓN: Monto {currency} {amount:,.2f} >= {currency} {threshold:,.2f}",
                severity="warning"
            )


class DocumentLinkingValidator:
    """
    Validates and suggests document linking (invoice <-> voucher).
    Uses amount and date matching heuristics.
    """
    
    def find_matches(self, documents: list) -> list:
        """
        Find potential matches between invoices and vouchers.
        
        Returns list of suggested links with confidence scores.
        """
        invoices = [d for d in documents if d.get('doc_type') == 'invoice']
        vouchers = [d for d in documents if d.get('doc_type') == 'voucher']
        
        matches = []
        
        for inv in invoices:
            inv_data = inv.get('extracted_data', {})
            inv_total = self._get_amount(inv_data.get('total', {}))
            inv_date = inv_data.get('date', {}).get('value', '')
            
            if not inv_total:
                continue
            
            for voucher in vouchers:
                voucher_data = voucher.get('extracted_data', {})
                voucher_amount = self._get_amount(voucher_data.get('amount', {}))
                voucher_date = voucher_data.get('date', {}).get('value', '')
                
                if not voucher_amount:
                    continue
                
                # Calculate match score
                score = self._calculate_match_score(
                    inv_total, voucher_amount,
                    inv_date, voucher_date
                )
                
                if score >= 0.7:  # Threshold for suggesting match
                    matches.append({
                        'invoice_id': inv.get('id'),
                        'voucher_id': voucher.get('id'),
                        'invoice_total': inv_total,
                        'voucher_amount': voucher_amount,
                        'confidence': score,
                        'reason': self._match_reason(inv_total, voucher_amount)
                    })
        
        return sorted(matches, key=lambda x: x['confidence'], reverse=True)
    
    def _get_amount(self, amount_field: dict) -> Optional[float]:
        """Extract numeric amount from field."""
        if isinstance(amount_field, dict):
            return amount_field.get('value')
        return None
    
    def _calculate_match_score(
        self, 
        inv_total: float, 
        voucher_amount: float,
        inv_date: str,
        voucher_date: str
    ) -> float:
        """Calculate matching confidence score (0.0 - 1.0)."""
        score = 0.0
        
        # Amount matching (most important)
        if inv_total == voucher_amount:
            score += 0.8  # Exact match
        elif abs(inv_total - voucher_amount) / max(inv_total, voucher_amount) < 0.01:
            score += 0.5  # Within 1%
        elif abs(inv_total - voucher_amount) / max(inv_total, voucher_amount) < 0.05:
            score += 0.3  # Within 5%
        
        # Detraction adjustment (12% or 10% less could indicate detraction)
        detraction_ratios = [0.88, 0.90]  # After 12% or 10% detraction
        for ratio in detraction_ratios:
            if abs(voucher_amount - inv_total * ratio) < 1:
                score += 0.4
                break
        
        # Date proximity bonus (same date = +0.2)
        if inv_date and voucher_date and inv_date == voucher_date:
            score += 0.2
        
        return min(score, 1.0)
    
    def _match_reason(self, inv_total: float, voucher_amount: float) -> str:
        """Generate human-readable match reason."""
        if inv_total == voucher_amount:
            return "Montos exactamente iguales"
        
        diff = abs(inv_total - voucher_amount)
        if diff / max(inv_total, voucher_amount) < 0.05:
            return f"Montos similares (diferencia: S/ {diff:.2f})"
        
        # Check for detraction
        if abs(voucher_amount - inv_total * 0.88) < 1:
            return "Monto coincide con deducción de detracción 12%"
        if abs(voucher_amount - inv_total * 0.90) < 1:
            return "Monto coincide con deducción de detracción 10%"
        
        return f"Posible coincidencia (total: {inv_total}, voucher: {voucher_amount})"


# Singleton instances
_ruc_validator: Optional[RUCValidator] = None
_banc_validator: Optional[BancarizationValidator] = None
_link_validator: Optional[DocumentLinkingValidator] = None


def get_ruc_validator() -> RUCValidator:
    global _ruc_validator
    if _ruc_validator is None:
        _ruc_validator = RUCValidator()
    return _ruc_validator


def get_bancarization_validator() -> BancarizationValidator:
    global _banc_validator
    if _banc_validator is None:
        _banc_validator = BancarizationValidator()
    return _banc_validator


def get_linking_validator() -> DocumentLinkingValidator:
    global _link_validator
    if _link_validator is None:
        _link_validator = DocumentLinkingValidator()
    return _link_validator
