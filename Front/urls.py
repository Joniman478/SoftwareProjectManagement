from django.urls import path
from . import views

urlpatterns = [
    # Template Views
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('shipments/', views.shipments_page, name='shipments'),
    path('workflow/', views.workflow_page, name='workflow'),
    path('documents/', views.documents_page, name='documents'),
    path('stakeholders/', views.stakeholders_page, name='stakeholders'),
    path('notifications/', views.notifications_page, name='notifications'),
    path('reports/', views.reports_page, name='reports'),
    path('messages/', views.messages_page, name='messages'),
    path('audit/', views.audit_page, name='audit'),
    path('settings/', views.settings_page, name='settings'),

    # REST APIs
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'),
    path('api/shipments/', views.shipments_api, name='shipments_api'),
    path('api/shipments/<str:shipment_id>/', views.shipment_detail_api, name='shipment_detail_api'),
    path('api/shipments/<str:shipment_id>/advance/', views.advance_shipment_api, name='advance_shipment_api'),
    path('api/track/', views.track_api, name='track_api'),
    path('api/documents/', views.documents_api, name='documents_api'),
    path('api/documents/<int:doc_id>/verify/', views.verify_document_api, name='verify_document_api'),
    path('api/duty-calculator/', views.duty_calculator_api, name='duty_calculator_api'),
    path('api/audit/verify/', views.audit_verify_api, name='audit_verify_api'),
    path('api/messages/', views.messages_api, name='messages_api'),
    path('api/notifications/', views.notifications_api, name='notifications_api'),
    path('api/reports/', views.reports_api, name='reports_api'),
    path('api/reports/export/', views.export_report_api, name='export_report_api'),
]