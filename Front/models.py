from django.db import models


class Shipment(models.Model):
    class Status(models.TextChoices):
        BOOKING = 'Booking Confirmed', 'Booking Confirmed'
        IN_TRANSIT = 'In Transit', 'In Transit'
        ARRIVED = 'Arrived at Port', 'Arrived at Port'
        CUSTOMS = 'Customs Clearance', 'Customs Clearance'
        RELEASED = 'Released', 'Released'
        DELIVERED = 'Delivered', 'Delivered'

    shipment_id = models.CharField(max_length=30, unique=True)
    vehicle = models.CharField(max_length=200)
    image = models.CharField(max_length=255, default='/static/images/land_cruiser.png', blank=True)
    vin = models.CharField(max_length=80, unique=True)
    port = models.CharField(max_length=200)
    destination = models.CharField(max_length=200, default='Modjo Dry Port, Ethiopia', blank=True)
    importer_name = models.CharField(max_length=150, default='GT Motors Ltd.', blank=True)
    duty_amount = models.CharField(max_length=60, default='ETB 1,250,000', blank=True)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.BOOKING)
    eta = models.DateField(blank=True, null=True)
    progress = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.shipment_id} - {self.vehicle}"


class DocumentRecord(models.Model):
    shipment = models.ForeignKey(Shipment, related_name='documents', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    document_type = models.CharField(max_length=80)
    sha256_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=30, default='Verified')
    uploaded_by = models.CharField(max_length=100, default='GT Motors Ltd.', blank=True)
    file_size = models.CharField(max_length=30, default='1.8 MB', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.document_type})"


class Notification(models.Model):
    shipment = models.ForeignKey(Shipment, related_name='notifications', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    notification_type = models.CharField(max_length=20, default='info')
    time_label = models.CharField(max_length=50, default='Just now')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AuditTrail(models.Model):
    shipment = models.ForeignKey(Shipment, related_name='audit_logs', on_delete=models.SET_NULL, null=True, blank=True)
    actor = models.CharField(max_length=200)
    action = models.CharField(max_length=250)
    sha256_digest = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.actor} — {self.action}'


class Message(models.Model):
    sender = models.CharField(max_length=150)
    sender_role = models.CharField(max_length=100, default='Customs Officer')
    recipient = models.CharField(max_length=150, default='GT Motors Ltd.')
    subject = models.CharField(max_length=250)
    body = models.TextField()
    shipment = models.ForeignKey(Shipment, related_name='messages', on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.subject}"
