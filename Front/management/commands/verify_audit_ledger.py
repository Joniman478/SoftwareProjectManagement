from django.core.management.base import BaseCommand
from Front.services import CryptoLedgerService
from Front.models import AuditTrail


class Command(BaseCommand):
    help = 'Cryptographically validates SHA-256 integrity of the audit ledger against tampering.'

    def handle(self, *args, **options):
        self.stdout.write('Scanning supply chain audit trail ledger...')
        result = CryptoLedgerService.verify_ledger_integrity()
        
        count = AuditTrail.objects.count()
        for idx, entry in enumerate(AuditTrail.objects.order_by('id')[:10], 1):
            ref = entry.shipment.shipment_id if entry.shipment else 'SYS'
            self.stdout.write(f"  [{idx:02d}] {entry.created_at.strftime('%Y-%m-%d %H:%M:%S')} | {entry.actor[:22]:<22} | {entry.action[:35]:<35} | {entry.sha256_digest}")

        if count > 10:
            self.stdout.write(f"  ... and {count - 10} more records.")

        if result['is_valid']:
            self.stdout.write(self.style.SUCCESS(
                f"\n[SUCCESS] VERIFICATION SUCCESSFUL: {result['status']}\n"
                f"  Total records verified: {result['total_records']}\n"
                f"  Algorithm: {result['algorithm']}\n"
                f"  Sealed At: {result['verified_at']}"
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f"\n[FAILED] VERIFICATION FAILED: Tampering detected in audit ledger."
            ))
