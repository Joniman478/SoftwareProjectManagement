import json
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse

from .models import Shipment, DocumentRecord, Notification, AuditTrail, Message
from .services import DutyCalculator, CryptoLedgerService, WorkflowEngine


class NCISCPBackendComprehensiveTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_all_page_views_render_successfully(self):
        views_to_test = [
            ('home', 'National Car Import Platform'),
            ('dashboard', 'Import Operations Dashboard'),
            ('shipments', 'Vehicle Import Shipments'),
            ('workflow', 'Import Supply Chain Workflow Pipeline'),
            ('documents', 'Cryptographic Document Management'),
            ('stakeholders', 'National Automotive Supply Chain Stakeholders'),
            ('notifications', 'Alerts & System Notifications'),
            ('reports', 'Supply Chain Intelligence & Analytics'),
            ('messages', 'Inter-Agency Communications'),
            ('audit', 'Tamper-Evident Cryptographic Audit Ledger'),
            ('settings', 'System Settings & Project Information'),
        ]

        for route_name, expected_text in views_to_test:
            response = self.client.get(reverse(route_name))
            self.assertEqual(response.status_code, 200, f"Route '{route_name}' failed to return 200 OK")
            self.assertContains(response, expected_text)

    def test_duty_calculator_service(self):
        # 1. Standard ICE Vehicle (2000 cc)
        res_ice = DutyCalculator.calculate_duty(
            cif_etb=1000000.0,
            engine_cc=2000,
            fuel_type='petrol',
            year_manufactured=2024
        )
        self.assertEqual(res_ice['customs_duty']['amount'], 350000.0)  # 35% of 1M
        self.assertGreater(res_ice['total_duty_payable_etb'], 1000000.0)
        self.assertFalse(res_ice['is_ev_incentivized'])

        # 2. Electric Vehicle (EV)
        res_ev = DutyCalculator.calculate_duty(
            cif_etb=1000000.0,
            engine_cc=0,
            fuel_type='electric',
            year_manufactured=2024
        )
        self.assertEqual(res_ev['customs_duty']['amount'], 0.0)  # 0% Customs Duty for EV
        self.assertEqual(res_ev['surtax']['amount'], 0.0)       # 0% Surtax for EV
        self.assertTrue(res_ev['is_ev_incentivized'])
        self.assertLess(res_ev['total_duty_payable_etb'], res_ice['total_duty_payable_etb'])

    def test_duty_calculator_api(self):
        payload = {
            'cif_etb': 2000000,
            'engine_cc': 2500,
            'fuel_type': 'diesel',
            'year_manufactured': 2023,
            'is_commercial': False
        }
        response = self.client.post(
            '/api/duty-calculator/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('calculation', data)
        self.assertIn('formatted_total', data['calculation'])

    def test_crypto_ledger_service_and_api(self):
        # 1. Test hash computation
        digest = CryptoLedgerService.sha256('TestPayload')
        self.assertEqual(len(digest), 64)

        # 2. Test audit recording
        entry = CryptoLedgerService.record_audit(
            actor='Customs Officer',
            action='Test Verified Audit Event',
            metadata={'test': True}
        )
        self.assertIsNotNone(entry.id)
        self.assertIn('...', entry.sha256_digest)

        # 3. Test verification API
        res_verify = self.client.get('/api/audit/verify/')
        self.assertEqual(res_verify.status_code, 200)
        self.assertTrue(res_verify.json()['is_valid'])

    def test_workflow_engine_state_machine(self):
        shipment = Shipment.objects.create(
            shipment_id='SHP-TEST-999',
            vehicle='Toyota Land Cruiser Test',
            vin='VINTEST99988877766',
            port='Port of Yokohama -> Djibouti',
            destination='Modjo Dry Port',
            status='Booking Confirmed',
            progress=15
        )

        # Advance 1: Booking -> In Transit (Allowed for forwarder)
        ok, msg, data = WorkflowEngine.advance(
            shipment=shipment,
            actor_name='ESLSE Forwarder',
            actor_role='forwarder'
        )
        self.assertTrue(ok)
        self.assertEqual(shipment.status, 'In Transit')
        self.assertEqual(shipment.progress, 35)

        # Advance 2: In Transit -> Arrived Port (Allowed for port operator)
        ok, msg, data = WorkflowEngine.advance(
            shipment=shipment,
            actor_name='Modjo Yard Master',
            actor_role='port'
        )
        self.assertTrue(ok)
        self.assertEqual(shipment.status, 'Arrived at Port')

    def test_shipment_full_crud_api(self):
        # 1. CREATE (POST)
        payload = {
            'vehicle': 'Toyota RAV4 Hybrid 2024',
            'vin': 'JTMBTEST123456789',
            'port': 'Port of Nagoya -> Djibouti',
            'destination': 'Kality Dry Port, Addis Ababa',
            'importer_name': 'GT Motors Ltd.',
            'duty_amount': 'ETB 1,450,000',
            'eta': '2024-07-01'
        }
        res_create = self.client.post(
            '/api/shipments/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res_create.status_code, 201)
        shp_id = res_create.json()['shipment']['id']

        # 2. READ (GET by ID)
        res_get = self.client.get(f'/api/shipments/{shp_id}/')
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.json()['shipment']['vehicle'], 'Toyota RAV4 Hybrid 2024')

        # 3. UPDATE (PUT/PATCH)
        update_payload = {
            'duty_amount': 'ETB 1,350,000',
            'destination': 'Modjo Dry Port, Ethiopia'
        }
        res_update = self.client.put(
            f'/api/shipments/{shp_id}/',
            data=json.dumps(update_payload),
            content_type='application/json'
        )
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json()['shipment']['duty'], 'ETB 1,350,000')

        # 4. ADVANCE (POST)
        res_advance = self.client.post(
            f'/api/shipments/{shp_id}/advance/',
            data=json.dumps({'actor_role': 'forwarder', 'actor_name': 'ESLSE Forwarder'}),
            content_type='application/json'
        )
        self.assertEqual(res_advance.status_code, 200)
        self.assertEqual(res_advance.json()['status'], 'In Transit')

        # 5. DELETE (DELETE)
        res_delete = self.client.delete(f'/api/shipments/{shp_id}/')
        self.assertEqual(res_delete.status_code, 200)
        self.assertFalse(Shipment.objects.filter(shipment_id=shp_id).exists())

    def test_documents_and_verification_api(self):
        res_get = self.client.get('/api/documents/')
        self.assertEqual(res_get.status_code, 200)

        # Upload doc
        doc_payload = {
            'title': 'Commercial Bill of Lading Test',
            'type': 'Bill of Lading',
            'uploaded_by': 'ESLSE Maritime',
            'hash': 'abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789'
        }
        res_post = self.client.post(
            '/api/documents/',
            data=json.dumps(doc_payload),
            content_type='application/json'
        )
        self.assertEqual(res_post.status_code, 201)
        doc_id = res_post.json()['document']['id']

        # Verify doc
        res_verify = self.client.get(f'/api/documents/{doc_id}/verify/')
        self.assertEqual(res_verify.status_code, 200)
        self.assertTrue(res_verify.json()['is_valid'])

    def test_reports_and_export_api(self):
        res_reports = self.client.get('/api/reports/')
        self.assertEqual(res_reports.status_code, 200)
        self.assertIn('summary', res_reports.json())

        res_json = self.client.get('/api/reports/export/?format=json')
        self.assertEqual(res_json.status_code, 200)
        self.assertIn('shipments', res_json.json())

        res_csv = self.client.get('/api/reports/export/?format=csv')
        self.assertEqual(res_csv.status_code, 200)
        self.assertEqual(res_csv['Content-Type'], 'text/csv')
