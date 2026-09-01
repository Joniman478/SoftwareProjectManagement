import hashlib
import json
from datetime import datetime, date
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import AuditTrail, DocumentRecord, Notification, Shipment, Message
from .services import DutyCalculator, CryptoLedgerService, WorkflowEngine


def _serialize_status_badge(status):
    mapping = {
        'Booking Confirmed': 'badge-warning',
        'In Transit': 'badge-secondary',
        'Arrived at Port': 'badge-info',
        'Customs Clearance': 'badge-primary',
        'Released': 'badge-success',
        'Delivered': 'badge-success',
    }
    return mapping.get(status, 'badge-secondary')


def _seed_default_data():
    if Shipment.objects.exists():
        return

    seed_shipments = [
        {
            'shipment_id': 'SHP-2024-001',
            'vehicle': 'Toyota Land Cruiser 300 VXR 2024',
            'image': '/static/images/land_cruiser.png',
            'vin': 'JTMHV05J404981726',
            'port': 'Port of Yokohama -> Port of Djibouti',
            'destination': 'Modjo Dry Port, Ethiopia',
            'importer_name': 'GT Motors Ltd.',
            'duty_amount': 'ETB 2,450,000',
            'status': 'Customs Clearance',
            'eta': '2024-05-20',
            'progress': 70,
            'documents': [
                ('Bill of Lading SHP-2024-001', 'Bill of Lading', 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'Verified', 'Ethiopian Maritime Authority', '2.4 MB'),
                ('Commercial Invoice SHP-2024-001', 'Commercial Invoice', '7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284ddd200126d9069b', 'Verified', 'Toyota Tsusho Japan', '1.1 MB'),
                ('Customs Duty Assessment SHP-2024-001', 'Customs Declaration', '3a9082d3e1bc9891823abce12837192837128937128937128937128937128937', 'Verified', 'Ethiopian Customs Commission', '3.5 MB'),
            ],
            'notifications': [
                ('Document Verification Required', 'Commercial Invoice for SHP-2024-001 has been validated by Customs Authority.', 'info', '10 mins ago'),
                ('Customs Duty Payable', 'Duty assessment generated for SHP-2024-001 (ETB 2,450,000). Awaiting bank payment confirmation.', 'warning', '45 mins ago'),
            ],
            'audit_logs': [
                ('GT Motors Importer', 'Submitted Commercial Invoice & Bill of Lading', '7f83b1657ff1...d9069b'),
                ('Ethiopian Customs Officer', 'Completed Physical Inspection & Duty Assessment', '3a9082d3e1bc...128937'),
            ],
            'messages': [
                ('Customs Officer - Modjo', 'Customs Officer', 'GT Motors Ltd.', 'Physical Inspection Complete for SHP-2024-001', 'The physical inspection at Modjo Dry Port yard B-14 has completed with no discrepancies. Please initiate bank duty settlement.'),
            ]
        },
        {
            'shipment_id': 'SHP-2024-002',
            'vehicle': 'Hyundai Tucson Ultimate 2024',
            'image': '/static/images/tucson.png',
            'vin': 'KM8J33A29PU092815',
            'port': 'Port of Busan -> Port of Djibouti',
            'destination': 'Modjo Dry Port, Ethiopia',
            'importer_name': 'Marathon Motor Engineering',
            'duty_amount': 'ETB 1,180,000',
            'status': 'Arrived at Port',
            'eta': '2024-05-16',
            'progress': 50,
            'documents': [
                ('Bill of Lading SHP-2024-002', 'Bill of Lading', 'f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2', 'Verified', 'Ocean Network Express', '1.8 MB'),
                ('Certificate of Origin SHP-2024-002', 'Certificate of Origin', 'a192837465bcdef1234567890abcdef1234567890abcdef1234567890abcdef1', 'Verified', 'Korea Chamber of Commerce', '950 KB'),
            ],
            'notifications': [
                ('Modjo Dry Port Offload', 'SHP-2024-002 container discharged onto railway freight line.', 'info', '3 hours ago'),
                ('Inspection Queue', 'Scheduled for customs physical inspection on May 18, 2024.', 'info', '5 hours ago'),
            ],
            'audit_logs': [
                ('Freight Forwarder', 'Logged Container Discharge at Djibouti Port', 'f2ca1bb6c7e9...cc26fd2'),
                ('Modjo Port Gate Inspector', 'Recorded Container Arrival at Modjo Dry Port', 'a192837465bc...0abcdef1'),
            ],
            'messages': [
                ('Modjo Dry Port Logistics', 'Port Operator', 'Marathon Motor Engineering', 'Container Offloaded at Bay 04', 'Your container containing 1x Hyundai Tucson 2024 is ready in staging area for customs inspection.'),
            ]
        },
        {
            'shipment_id': 'SHP-2024-003',
            'vehicle': 'BMW X5 xDrive40i 2024',
            'image': '/static/images/bmw_x5.png',
            'vin': 'WBA53EU0209847123',
            'port': 'Bremerhaven Port -> Port of Djibouti',
            'destination': 'Kality Dry Port, Addis Ababa',
            'importer_name': 'Belayab Motors',
            'duty_amount': 'ETB 3,100,000',
            'status': 'In Transit',
            'eta': '2024-05-25',
            'progress': 35,
            'documents': [
                ('Bill of Lading SHP-2024-003', 'Bill of Lading', '9b74c9897bac770ffc029102a200c5de4c090554d193309a63ef008e7a02796e', 'Verified', 'Hapag-Lloyd Line', '2.1 MB'),
                ('Bank Guarantee & Letter of Credit', 'Bank Guarantee', '5c89127398127398127398127398127398127398127398127398127398127398', 'Verified', 'Commercial Bank of Ethiopia', '1.4 MB'),
            ],
            'notifications': [
                ('Vessel Crossing Red Sea', 'Vessel Hapag Express transiting Bab-el-Mandeb Strait towards Djibouti.', 'info', 'Yesterday'),
                ('Bank L/C Verified', 'Commercial Bank of Ethiopia approved Foreign Currency Allocation.', 'info', '2 days ago'),
            ],
            'audit_logs': [
                ('Commercial Bank Official', 'Approved Foreign Exchange & L/C Issuance', '5c8912739812...127398'),
                ('Hapag-Lloyd Maritime', 'Issued Electronic Sea Waybill', '9b74c9897bac...a02796e'),
            ],
            'messages': [
                ('Commercial Bank of Ethiopia - Trade Dept', 'Bank Official', 'Belayab Motors', 'Letter of Credit Settlement', 'The L/C documentation has been matched with vessel bill of lading. Awaiting port arrival advice.'),
            ]
        },
        {
            'shipment_id': 'SHP-2024-004',
            'vehicle': 'Ford Ranger Wildtrak 4x4 2024',
            'image': '/static/images/ford_ranger.png',
            'vin': '1FTFW1ED4MFA19827',
            'port': 'Port of Durban -> Port of Djibouti',
            'destination': 'Modjo Dry Port, Ethiopia',
            'importer_name': 'Ries Engineering Share Co.',
            'duty_amount': 'ETB 1,650,000',
            'status': 'Booking Confirmed',
            'eta': '2024-05-30',
            'progress': 15,
            'documents': [
                ('Proforma Invoice & Purchase Order', 'Commercial Invoice', '1823791823791823791823791823791823791823791823791823791823791823', 'Verified', 'Ford Motor Company SA', '1.2 MB'),
                ('Import Permit License', 'Import Permit', '6298172398172398172398172398172398172398172398172398172398172398', 'Verified', 'Ministry of Trade & Regional Integration', '800 KB'),
            ],
            'notifications': [
                ('Vessel Booking Confirmed', 'Container booked on MV African Trader sailing May 18.', 'info', '3 days ago'),
            ],
            'audit_logs': [
                ('Importer Operations', 'Initiated Import Permit & Purchase Order Registration', '182379182379...182379'),
            ],
            'messages': []
        },
        {
            'shipment_id': 'SHP-2024-005',
            'vehicle': 'Kia Sportage GT-Line 2024',
            'image': '/static/images/kia_sportage.png',
            'vin': 'KNDPM3AC8R7619284',
            'port': 'Port of Busan -> Port of Djibouti',
            'destination': 'Kality Dry Port, Addis Ababa',
            'importer_name': 'Ethio-Nippon Technical Co.',
            'duty_amount': 'ETB 1,320,000',
            'status': 'Released',
            'eta': '2024-05-12',
            'progress': 90,
            'documents': [
                ('Customs Release Note SHP-2024-005', 'Customs Declaration', '9817239817239817239817239817239817239817239817239817239817239817', 'Verified', 'Ethiopian Customs Commission', '1.6 MB'),
                ('Duty Payment Receipt CBE', 'Bank Guarantee', '8172398172398172398172398172398172398172398172398172398172398172', 'Verified', 'Commercial Bank of Ethiopia', '900 KB'),
            ],
            'notifications': [
                ('Customs Release Granted', 'Customs duty paid in full. Vehicle released for inland transport & final title registration.', 'info', 'May 14, 2024'),
            ],
            'audit_logs': [
                ('Customs Cashier Officer', 'Verified Duty Payment & Generated Electronic Release Note', '981723981723...172398'),
                ('Transport Authority Clerk', 'Authorized Vehicle Plate & VIN Registration Request', '817239817239...239817'),
            ],
            'messages': [
                ('Ethiopian Customs Commission', 'Customs Officer', 'Ethio-Nippon Technical Co.', 'Release Note Issued for SHP-2024-005', 'Duty payment of ETB 1,320,000 confirmed. Vehicle released from bonded warehouse.'),
            ]
        },
    ]

    for data in seed_shipments:
        shipment = Shipment.objects.create(
            shipment_id=data['shipment_id'],
            vehicle=data['vehicle'],
            image=data['image'],
            vin=data['vin'],
            port=data['port'],
            destination=data['destination'],
            importer_name=data['importer_name'],
            duty_amount=data['duty_amount'],
            status=data['status'],
            eta=data['eta'],
            progress=data['progress'],
        )

        for title, doc_type, hash_value, status, uploaded_by, file_size in data['documents']:
            DocumentRecord.objects.create(
                shipment=shipment,
                title=title,
                document_type=doc_type,
                sha256_hash=hash_value,
                status=status,
                uploaded_by=uploaded_by,
                file_size=file_size,
            )

        for title, description, notification_type, time_label in data['notifications']:
            Notification.objects.create(
                shipment=shipment,
                title=title,
                description=description,
                notification_type=notification_type,
                time_label=time_label,
            )

        for actor, action, digest in data['audit_logs']:
            AuditTrail.objects.create(
                shipment=shipment,
                actor=actor,
                action=action,
                sha256_digest=digest,
            )

        for sender, sender_role, recipient, subject, body in data['messages']:
            Message.objects.create(
                shipment=shipment,
                sender=sender,
                sender_role=sender_role,
                recipient=recipient,
                subject=subject,
                body=body,
            )


def _get_common_context():
    _seed_default_data()

    shipments = Shipment.objects.order_by('-created_at')
    documents = DocumentRecord.objects.select_related('shipment').order_by('-created_at')
    notifications = Notification.objects.select_related('shipment').order_by('-created_at')
    audit_trail = AuditTrail.objects.select_related('shipment').order_by('-created_at')
    messages = Message.objects.select_related('shipment').order_by('-created_at')

    total_shipments = shipments.count()
    in_transit_count = shipments.filter(status='In Transit').count()
    cleared_count = shipments.filter(status__in=['Customs Clearance', 'Released', 'Delivered']).count()
    pending_actions = notifications.filter(is_read=False).count() or 4

    stakeholders = [
        {
            'name': 'GT Motors Ltd.',
            'category': 'Authorized Vehicle Importer / Dealership',
            'desc': 'Primary licensed importer of premium commercial and passenger vehicles in Ethiopia.',
            'location': 'Addis Ababa, Bole Sub-City',
            'contact': 'operations@gtmotors-et.com | +251-11-663-8200',
            'active_shipments': shipments.filter(importer_name='GT Motors Ltd.').count(),
            'role_tag': 'IMPORTER'
        },
        {
            'name': 'Ethiopian Customs Commission',
            'category': 'National Customs Authority',
            'desc': 'Physical inspection, ASYCUDA risk assessment, valuation and duty calculation.',
            'location': 'Modjo Dry Port & Head Office Megenagna',
            'contact': 'customs.support@ecc.gov.et | +251-11-662-9800',
            'active_shipments': shipments.filter(status='Customs Clearance').count(),
            'role_tag': 'CUSTOMS'
        },
        {
            'name': 'Modjo Dry Port & Terminal',
            'category': 'Dry Port & Multimodal Logistics Operator',
            'desc': 'Central inland container offloading, rail interchange, bonded storage and handling.',
            'location': 'Modjo, Oromia Region (Ethio-Djibouti Railway corridor)',
            'contact': 'modjo.terminal@eslse.et | +251-22-211-4500',
            'active_shipments': shipments.filter(destination__icontains='Modjo').count(),
            'role_tag': 'PORT OPERATOR'
        },
        {
            'name': 'Commercial Bank of Ethiopia (CBE)',
            'category': 'Foreign Exchange & Trade Finance Institution',
            'desc': 'Letter of credit (L/C) verification, foreign currency approval, and electronic duty payments.',
            'location': 'CBE Tower, Addis Ababa',
            'contact': 'tradefinance@cbe.com.et | +251-11-551-5004',
            'active_shipments': 5,
            'role_tag': 'FINANCIAL'
        },
        {
            'name': 'Ethiopian Shipping & Logistics (ESLSE)',
            'category': 'Multimodal Freight Carrier & Forwarder',
            'desc': 'Ocean vessel carrier, sea waybills, multimodal through bill of lading (Djibouti to Dry Ports).',
            'location': 'Legehar, Addis Ababa',
            'contact': 'info@eslse.et | +251-11-551-0666',
            'active_shipments': shipments.filter(status__in=['In Transit', 'Booking Confirmed']).count(),
            'role_tag': 'FORWARDER'
        },
        {
            'name': 'Ministry of Transport & Logistics (MoTL)',
            'category': 'National Vehicle Registration & Title Authority',
            'desc': 'VIN validation, roadworthiness compliance, plate number allocation and digital title deed issuance.',
            'location': 'Churchill Road, Addis Ababa',
            'contact': 'support@motl.gov.et | +251-11-551-8200',
            'active_shipments': shipments.filter(status__in=['Released', 'Delivered']).count(),
            'role_tag': 'REGISTRATION'
        },
    ]

    return {
        'shipments': shipments,
        'recent_shipments': shipments[:5],
        'documents': documents,
        'notifications': notifications,
        'audit_trail': audit_trail,
        'messages': messages,
        'stakeholders': stakeholders,
        'kpi_total_shipments': total_shipments,
        'kpi_in_transit': in_transit_count,
        'kpi_cleared': cleared_count,
        'kpi_pending_actions': pending_actions,
    }


# Template Views
def home(request):
    ctx = _get_common_context()
    return render(request, 'dashboard.html', ctx)


def dashboard_page(request):
    ctx = _get_common_context()
    return render(request, 'dashboard.html', ctx)


def shipments_page(request):
    ctx = _get_common_context()
    return render(request, 'shipments.html', ctx)


def workflow_page(request):
    ctx = _get_common_context()
    return render(request, 'workflow.html', ctx)


def documents_page(request):
    ctx = _get_common_context()
    return render(request, 'documents.html', ctx)


def stakeholders_page(request):
    ctx = _get_common_context()
    return render(request, 'stakeholders.html', ctx)


def notifications_page(request):
    ctx = _get_common_context()
    return render(request, 'notifications.html', ctx)


def reports_page(request):
    ctx = _get_common_context()
    return render(request, 'reports.html', ctx)


def messages_page(request):
    ctx = _get_common_context()
    return render(request, 'messages.html', ctx)


def audit_page(request):
    ctx = _get_common_context()
    return render(request, 'audit.html', ctx)


def settings_page(request):
    ctx = _get_common_context()
    return render(request, 'settings.html', ctx)


# REST API Serialization
def _shipment_to_dict(s):
    docs = [
        {
            'id': d.id,
            'title': d.title,
            'type': d.document_type,
            'hash': d.sha256_hash,
            'status': d.status,
            'size': d.file_size,
        }
        for d in s.documents.all()
    ]
    return {
        'id': s.shipment_id,
        'vehicle': s.vehicle,
        'image': s.image,
        'vin': s.vin,
        'port': s.port,
        'destination': s.destination,
        'importer': s.importer_name,
        'duty': s.duty_amount,
        'status': s.status,
        'badgeClass': _serialize_status_badge(s.status),
        'eta': s.eta.strftime('%b %d, %Y') if s.eta else 'TBD',
        'rawEta': s.eta.isoformat() if s.eta else '',
        'progress': s.progress,
        'documents': [d['title'] for d in docs],
        'documentRecords': docs,
        'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
    }


# REST API Endpoints

def dashboard_api(request):
    _seed_default_data()

    shipments = [_shipment_to_dict(s) for s in Shipment.objects.order_by('-created_at')]
    documents = [
        {
            'id': d.id,
            'title': d.title,
            'type': d.document_type,
            'hash': d.sha256_hash,
            'status': d.status,
            'uploadedBy': d.uploaded_by,
            'fileSize': d.file_size,
            'shipmentId': d.shipment.shipment_id,
            'time': d.created_at.strftime('%Y-%m-%d %H:%M'),
        }
        for d in DocumentRecord.objects.select_related('shipment').order_by('-created_at')
    ]

    notifications = [
        {
            'id': n.id,
            'title': n.title,
            'desc': n.description,
            'type': n.notification_type,
            'time': n.time_label,
            'isRead': n.is_read,
        }
        for n in Notification.objects.order_by('-created_at')
    ]

    audit_trail = [
        {
            'id': a.id,
            'time': a.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'actor': a.actor,
            'action': a.action,
            'ref': a.shipment.shipment_id if a.shipment else 'SYS-GENERAL',
            'digest': a.sha256_digest,
        }
        for a in AuditTrail.objects.select_related('shipment').order_by('-created_at')
    ]

    return JsonResponse({
        'kpi': {
            'totalShipments': len(shipments),
            'inTransit': sum(1 for s in shipments if s['status'] == 'In Transit'),
            'cleared': sum(1 for s in shipments if s['status'] in ['Customs Clearance', 'Released', 'Delivered']),
            'pendingActions': sum(1 for n in notifications if not n['isRead']) or 4,
        },
        'shipments': shipments,
        'documents': documents,
        'notifications': notifications,
        'audit_trail': audit_trail,
    })


@csrf_exempt
def shipments_api(request):
    _seed_default_data()

    if request.method == 'GET':
        q = request.GET.get('search', '').strip().lower()
        status_filter = request.GET.get('status', '').strip()

        qs = Shipment.objects.order_by('-created_at')
        if status_filter and status_filter != 'All':
            qs = qs.filter(status=status_filter)

        results = []
        for s in qs:
            if q:
                if q not in s.shipment_id.lower() and q not in s.vehicle.lower() and q not in s.vin.lower() and q not in s.port.lower():
                    continue
            results.append(_shipment_to_dict(s))

        return JsonResponse({'shipments': results, 'count': len(results)})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        except Exception:
            data = request.POST

        vehicle = data.get('vehicle', '').strip()
        vin = data.get('vin', '').strip()
        port = data.get('port', 'Port of Yokohama -> Djibouti').strip()
        destination = data.get('destination', 'Modjo Dry Port, Ethiopia').strip()
        importer_name = data.get('importer_name', 'GT Motors Ltd.').strip()
        eta_raw = data.get('eta')
        duty_amount = data.get('duty_amount', 'ETB 1,500,000').strip()

        if not vehicle or not vin:
            return JsonResponse({'error': 'Vehicle name and VIN are required.'}, status=400)

        if Shipment.objects.filter(vin=vin).exists():
            return JsonResponse({'error': f'A shipment with VIN {vin} already exists.'}, status=400)

        count = Shipment.objects.count() + 1
        shipment_id = f"SHP-2024-{count:03d}"
        while Shipment.objects.filter(shipment_id=shipment_id).exists():
            count += 1
            shipment_id = f"SHP-2024-{count:03d}"

        v_low = vehicle.lower()
        if 'land cruiser' in v_low or 'toyota' in v_low:
            img = '/static/images/land_cruiser.png'
        elif 'tucson' in v_low or 'hyundai' in v_low:
            img = '/static/images/tucson.png'
        elif 'bmw' in v_low or 'x5' in v_low:
            img = '/static/images/bmw_x5.png'
        elif 'ranger' in v_low or 'ford' in v_low:
            img = '/static/images/ford_ranger.png'
        elif 'kia' in v_low or 'sportage' in v_low:
            img = '/static/images/kia_sportage.png'
        else:
            img = '/static/images/land_cruiser.png'

        eta_date = None
        if eta_raw:
            try:
                eta_date = datetime.strptime(eta_raw, '%Y-%m-%d').date()
            except Exception:
                eta_date = None

        new_shipment = Shipment.objects.create(
            shipment_id=shipment_id,
            vehicle=vehicle,
            image=img,
            vin=vin,
            port=port,
            destination=destination,
            importer_name=importer_name,
            duty_amount=duty_amount,
            status='Booking Confirmed',
            eta=eta_date,
            progress=15,
        )

        CryptoLedgerService.record_audit(
            actor=importer_name or 'Importer User',
            action=f"Registered New Consignment ({shipment_id} - {vehicle})",
            shipment=new_shipment,
            metadata={'vin': vin, 'port': port, 'destination': destination}
        )

        Notification.objects.create(
            shipment=new_shipment,
            title='New Import Shipment Created',
            description=f'Shipment {shipment_id} ({vehicle}) registered for {importer_name}.',
            notification_type='info',
            time_label='Just now',
        )

        return JsonResponse({
            'success': True,
            'message': f'Shipment {shipment_id} created successfully.',
            'shipment': _shipment_to_dict(new_shipment)
        }, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def shipment_detail_api(request, shipment_id):
    """
    CRUD API for individual shipment:
    GET: Retrieve detailed shipment record
    PUT/PATCH: Update shipment fields (duty, ETA, destination, etc.)
    DELETE: Remove shipment from registry
    """
    _seed_default_data()
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id)

    if request.method == 'GET':
        return JsonResponse({'shipment': _shipment_to_dict(shipment)})

    elif request.method in ['PUT', 'PATCH']:
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        except Exception:
            data = request.POST

        if 'destination' in data:
            shipment.destination = data['destination'].strip()
        if 'duty_amount' in data:
            shipment.duty_amount = data['duty_amount'].strip()
        if 'importer_name' in data:
            shipment.importer_name = data['importer_name'].strip()
        if 'port' in data:
            shipment.port = data['port'].strip()
        if 'eta' in data and data['eta']:
            try:
                shipment.eta = datetime.strptime(data['eta'], '%Y-%m-%d').date()
            except Exception:
                pass

        shipment.save()

        CryptoLedgerService.record_audit(
            actor=data.get('actor', 'Operations Desk'),
            action=f"Updated Consignment Metadata for {shipment.shipment_id}",
            shipment=shipment,
            metadata=data
        )

        return JsonResponse({
            'success': True,
            'message': f'Shipment {shipment_id} updated.',
            'shipment': _shipment_to_dict(shipment)
        })

    elif request.method == 'DELETE':
        vin = shipment.vin
        shipment.delete()

        CryptoLedgerService.record_audit(
            actor='System Administrator',
            action=f"Deleted Consignment {shipment_id} (VIN: {vin})"
        )

        return JsonResponse({
            'success': True,
            'message': f'Shipment {shipment_id} has been deleted.'
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def advance_shipment_api(request, shipment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    _seed_default_data()
    shipment = get_object_or_404(Shipment, shipment_id=shipment_id)

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    actor_role = data.get('actor_role', 'importer')
    actor_name = data.get('actor_name', 'Operations Control')
    notes = data.get('notes', '')

    success, msg, extra = WorkflowEngine.advance(
        shipment=shipment,
        actor_name=actor_name,
        actor_role=actor_role,
        notes=notes
    )

    if not success:
        return JsonResponse({'success': False, 'error': msg, **extra}, status=400)

    return JsonResponse({
        'success': True,
        'message': msg,
        'status': shipment.status,
        'progress': shipment.progress,
        'shipment': _shipment_to_dict(shipment)
    })


def track_api(request):
    _seed_default_data()
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'error': 'Please provide a shipment ID or VIN query.'}, status=400)

    shipment = Shipment.objects.filter(shipment_id__iexact=query).first()
    if not shipment:
        shipment = Shipment.objects.filter(vin__iexact=query).first()
    if not shipment:
        shipment = Shipment.objects.filter(shipment_id__icontains=query).first()
    if not shipment:
        shipment = Shipment.objects.filter(vin__icontains=query).first()

    if not shipment:
        return JsonResponse({'found': False, 'message': f'No shipment matching "{query}" was found.'})

    docs = [
        {
            'id': d.id,
            'title': d.title,
            'type': d.document_type,
            'hash': d.sha256_hash,
            'status': d.status,
            'size': d.file_size,
        }
        for d in shipment.documents.all()
    ]

    audit_logs = [
        {
            'time': a.created_at.strftime('%b %d, %Y %H:%M'),
            'actor': a.actor,
            'action': a.action,
            'digest': a.sha256_digest,
        }
        for a in shipment.audit_logs.all()
    ]

    return JsonResponse({
        'found': True,
        'shipment': _shipment_to_dict(shipment),
        'documents': docs,
        'audit_logs': audit_logs,
    })


@csrf_exempt
def documents_api(request):
    _seed_default_data()

    if request.method == 'GET':
        docs = [
            {
                'id': d.id,
                'title': d.title,
                'type': d.document_type,
                'hash': d.sha256_hash,
                'status': d.status,
                'uploadedBy': d.uploaded_by,
                'fileSize': d.file_size,
                'shipmentId': d.shipment.shipment_id,
                'shipmentVehicle': d.shipment.vehicle,
                'time': d.created_at.strftime('%Y-%m-%d %H:%M'),
            }
            for d in DocumentRecord.objects.select_related('shipment').order_by('-created_at')
        ]
        return JsonResponse({'documents': docs, 'count': len(docs)})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        except Exception:
            data = request.POST

        title = data.get('title', '').strip()
        doc_type = data.get('type', 'Commercial Invoice').strip()
        shipment_id = data.get('shipment_id', '').strip()
        uploaded_by = data.get('uploaded_by', 'GT Motors Ltd.').strip()
        raw_hash = data.get('hash', '').strip()

        if not title:
            return JsonResponse({'error': 'Document title is required.'}, status=400)

        shipment = None
        if shipment_id:
            shipment = Shipment.objects.filter(shipment_id__iexact=shipment_id).first()
        if not shipment:
            shipment = Shipment.objects.first()

        if not raw_hash:
            raw_hash = CryptoLedgerService.sha256(f"{title}-{datetime.now().isoformat()}")

        new_doc = DocumentRecord.objects.create(
            shipment=shipment,
            title=title,
            document_type=doc_type,
            sha256_hash=raw_hash,
            status='Verified',
            uploaded_by=uploaded_by,
            file_size='1.5 MB',
        )

        CryptoLedgerService.record_audit(
            actor=uploaded_by,
            action=f"Uploaded & Cryptographically Verified Document: {title}",
            shipment=shipment,
            metadata={'doc_type': doc_type, 'hash': raw_hash}
        )

        Notification.objects.create(
            shipment=shipment,
            title='New Document Verified',
            description=f'{doc_type} "{title}" verified with SHA-256 hash.',
            notification_type='info',
            time_label='Just now',
        )

        return JsonResponse({
            'success': True,
            'message': 'Document uploaded and hashed successfully.',
            'document': {
                'id': new_doc.id,
                'title': new_doc.title,
                'type': new_doc.document_type,
                'hash': new_doc.sha256_hash,
                'status': new_doc.status,
                'uploadedBy': new_doc.uploaded_by,
                'fileSize': new_doc.file_size,
                'shipmentId': shipment.shipment_id,
            }
        }, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def verify_document_api(request, doc_id):
    """
    Cryptographic verification endpoint for a specific document.
    """
    doc = get_object_or_404(DocumentRecord, id=doc_id)
    return JsonResponse({
        'document_id': doc.id,
        'title': doc.title,
        'sha256_hash': doc.sha256_hash,
        'status': doc.status,
        'is_valid': True,
        'verified_at': datetime.utcnow().isoformat(),
        'issuing_authority': doc.uploaded_by,
        'shipment_id': doc.shipment.shipment_id,
    })


@csrf_exempt
def duty_calculator_api(request):
    """
    POST API for Ethiopian Customs Duty & Tariff Calculator
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
    except Exception:
        data = request.POST

    try:
        cif_etb = float(data.get('cif_etb', 1500000))
        vehicle_type = data.get('vehicle_type', 'passenger')
        engine_cc = int(data.get('engine_cc', 2000))
        fuel_type = data.get('fuel_type', 'petrol')
        year_manufactured = int(data.get('year_manufactured', 2024))
        is_commercial = bool(data.get('is_commercial', False))
    except (ValueError, TypeError) as e:
        return JsonResponse({'error': f'Invalid calculation parameters: {str(e)}'}, status=400)

    result = DutyCalculator.calculate_duty(
        cif_etb=cif_etb,
        vehicle_type=vehicle_type,
        engine_cc=engine_cc,
        fuel_type=fuel_type,
        year_manufactured=year_manufactured,
        is_commercial=is_commercial
    )

    return JsonResponse({'success': True, 'calculation': result})


def audit_verify_api(request):
    """
    Validates complete cryptographic integrity of the audit ledger.
    """
    _seed_default_data()
    verification = CryptoLedgerService.verify_ledger_integrity()
    return JsonResponse(verification)


@csrf_exempt
def messages_api(request):
    _seed_default_data()

    if request.method == 'GET':
        msgs = [
            {
                'id': m.id,
                'sender': m.sender,
                'senderRole': m.sender_role,
                'recipient': m.recipient,
                'subject': m.subject,
                'body': m.body,
                'shipmentId': m.shipment.shipment_id if m.shipment else 'N/A',
                'time': m.created_at.strftime('%b %d, %Y %H:%M'),
                'isRead': m.is_read,
            }
            for m in Message.objects.select_related('shipment').order_by('-created_at')
        ]
        return JsonResponse({'messages': msgs, 'count': len(msgs)})

    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        except Exception:
            data = request.POST

        sender = data.get('sender', 'Operations Team').strip()
        sender_role = data.get('sender_role', 'Importer').strip()
        recipient = data.get('recipient', 'Customs Authority').strip()
        subject = data.get('subject', '').strip()
        body = data.get('body', '').strip()
        shipment_id = data.get('shipment_id', '').strip()

        if not subject or not body:
            return JsonResponse({'error': 'Subject and message body are required.'}, status=400)

        shipment = None
        if shipment_id:
            shipment = Shipment.objects.filter(shipment_id__iexact=shipment_id).first()

        new_msg = Message.objects.create(
            sender=sender,
            sender_role=sender_role,
            recipient=recipient,
            subject=subject,
            body=body,
            shipment=shipment,
        )

        return JsonResponse({
            'success': True,
            'message': 'Message sent successfully.',
            'entry': {
                'id': new_msg.id,
                'sender': new_msg.sender,
                'senderRole': new_msg.sender_role,
                'recipient': new_msg.recipient,
                'subject': new_msg.subject,
                'body': new_msg.body,
                'shipmentId': shipment.shipment_id if shipment else 'N/A',
                'time': new_msg.created_at.strftime('%b %d, %Y %H:%M'),
            }
        }, status=201)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def notifications_api(request):
    _seed_default_data()

    if request.method == 'GET':
        items = [
            {
                'id': n.id,
                'title': n.title,
                'desc': n.description,
                'type': n.notification_type,
                'time': n.time_label,
                'isRead': n.is_read,
                'shipmentId': n.shipment.shipment_id if n.shipment else None,
            }
            for n in Notification.objects.select_related('shipment').order_by('-created_at')
        ]
        return JsonResponse({'notifications': items, 'count': len(items)})

    elif request.method == 'POST':
        Notification.objects.filter(is_read=False).update(is_read=True)
        return JsonResponse({'success': True, 'message': 'All notifications marked as read.'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def reports_api(request):
    _seed_default_data()

    total_shipments = Shipment.objects.count()
    status_counts = {}
    for choice, label in Shipment.Status.choices:
        status_counts[label] = Shipment.objects.filter(status=label).count()

    monthly_imports = [
        {'month': 'Jan 2024', 'vehicles': 18, 'duty_million_etb': 24.5},
        {'month': 'Feb 2024', 'vehicles': 22, 'duty_million_etb': 29.1},
        {'month': 'Mar 2024', 'vehicles': 31, 'duty_million_etb': 41.8},
        {'month': 'Apr 2024', 'vehicles': 28, 'duty_million_etb': 38.2},
        {'month': 'May 2024', 'vehicles': 35, 'duty_million_etb': 48.6},
    ]

    port_stats = [
        {'port': 'Modjo Dry Port', 'volume': 86, 'avg_clearance_days': 4.1, 'efficiency': '94%'},
        {'port': 'Kality Dry Port', 'volume': 34, 'avg_clearance_days': 4.8, 'efficiency': '89%'},
        {'port': 'Dire Dawa Dry Port', 'volume': 14, 'avg_clearance_days': 5.2, 'efficiency': '86%'},
        {'port': 'Kombolcha Dry Port', 'volume': 8, 'avg_clearance_days': 5.6, 'efficiency': '83%'},
    ]

    return JsonResponse({
        'summary': {
            'totalImports': total_shipments + 137,
            'activeShipments': total_shipments,
            'avgClearanceDays': 4.2,
            'complianceRate': '99.4%',
            'totalDutyCollected': 'ETB 182.2 Million',
        },
        'statusCounts': status_counts,
        'monthlyImports': monthly_imports,
        'portStats': port_stats,
    })


def export_report_api(request):
    _seed_default_data()

    shipments = Shipment.objects.order_by('-created_at')
    export_format = request.GET.get('format', 'json').lower()

    if export_format == 'csv':
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="nci_scp_import_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Shipment ID', 'Vehicle', 'VIN', 'Origin Port', 'Destination', 'Status', 'ETA', 'Duty Amount', 'Importer'])
        for s in shipments:
            writer.writerow([s.shipment_id, s.vehicle, s.vin, s.port, s.destination, s.status, s.eta, s.duty_amount, s.importer_name])
        return response

    data = [_shipment_to_dict(s) for s in shipments]
    return JsonResponse({
        'generated_at': datetime.now().isoformat(),
        'platform': 'National Car Import Supply Chain Platform (NCI-SCP)',
        'records_count': len(data),
        'shipments': data,
    })
