from django.core.management.base import BaseCommand
from accounts.models import Account


class Command(BaseCommand):
    help = 'Seeds authoritative demo accounts across all supply chain roles.'

    def handle(self, *args, **options):
        demo_users = [
            {
                'email': 'admin@nci.gov.et',
                'username': 'admin_nci',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': Account.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'email': 'importer@gtmotors.et',
                'username': 'gtmotors_importer',
                'first_name': 'GT Motors',
                'last_name': 'Importer Desk',
                'role': Account.Role.IMPORTER,
            },
            {
                'email': 'customs@ecc.gov.et',
                'username': 'ecc_customs_officer',
                'first_name': 'Inspector',
                'last_name': 'Tadesse (ECC)',
                'role': Account.Role.CUSTOMS,
            },
            {
                'email': 'port@modjoport.et',
                'username': 'modjo_yard_master',
                'first_name': 'Modjo Port',
                'last_name': 'Yard Master',
                'role': Account.Role.SHIPPING,
            },
            {
                'email': 'forwarder@eslse.et',
                'username': 'eslse_forwarder',
                'first_name': 'ESLSE',
                'last_name': 'Freight Forwarder',
                'role': Account.Role.FORWARDER,
            },
            {
                'email': 'bank@cbe.com.et',
                'username': 'cbe_trade_finance',
                'first_name': 'CBE',
                'last_name': 'Trade Finance Desk',
                'role': Account.Role.STAKEHOLDER,
            },
        ]

        created_count = 0
        for u in demo_users:
            if not Account.objects.filter(email=u['email']).exists():
                Account.objects.create_user(
                    email=u['email'],
                    username=u['username'],
                    first_name=u['first_name'],
                    last_name=u['last_name'],
                    password='Pass1234',
                    role=u['role'],
                    is_staff=u.get('is_staff', False),
                    is_superuser=u.get('is_superuser', False)
                )
                created_count += 1
                self.stdout.write(f"  + Created {u['role']}: {u['email']}")
            else:
                self.stdout.write(f"  . Exists: {u['email']}")

        self.stdout.write(self.style.SUCCESS(
            f'Demo accounts ready! Default password for all demo accounts is "Pass1234".'
        ))
