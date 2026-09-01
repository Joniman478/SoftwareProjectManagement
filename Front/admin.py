from django.contrib import admin
from .models import Shipment, DocumentRecord, Notification, AuditTrail, Message


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipment_id', 'vehicle', 'vin', 'port', 'status', 'eta', 'progress', 'created_at')
    list_filter = ('status', 'port')
    search_fields = ('shipment_id', 'vehicle', 'vin', 'port', 'importer_name')


@admin.register(DocumentRecord)
class DocumentRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'shipment', 'document_type', 'status', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'status')
    search_fields = ('title', 'sha256_hash', 'shipment__shipment_id')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'shipment', 'notification_type', 'time_label', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'description')


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('actor', 'action', 'shipment', 'sha256_digest', 'created_at')
    search_fields = ('actor', 'action', 'sha256_digest', 'shipment__shipment_id')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'sender_role', 'recipient', 'shipment', 'is_read', 'created_at')
    list_filter = ('sender_role', 'is_read')
    search_fields = ('subject', 'body', 'sender', 'recipient')
