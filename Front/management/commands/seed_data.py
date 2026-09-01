from django.core.management.base import BaseCommand
from Front.views import _seed_default_data
from Front.models import Shipment, DocumentRecord, Notification, AuditTrail, Message


class Command(BaseCommand):
    help = 'Seeds initial vehicle import consignments, documents, audit logs, and messages.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-seeding by clearing existing records first.',
        )

    def handle(self, *args, **options):
        if options.get('force'):
            self.stdout.write(self.style.WARNING('Clearing existing supply chain records...'))
            Shipment.objects.all().delete()
            DocumentRecord.objects.all().delete()
            Notification.objects.all().delete()
            AuditTrail.objects.all().delete()
            Message.objects.all().delete()

        _seed_default_data()

        count = Shipment.objects.count()
        doc_count = DocumentRecord.objects.count()
        audit_count = AuditTrail.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded supply chain database:\n'
            f'  - Shipments: {count}\n'
            f'  - Verified Documents: {doc_count}\n'
            f'  - Audit Trail Entries: {audit_count}'
        ))
