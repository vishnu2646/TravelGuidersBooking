from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(TravelPlace)
admin.site.register(TravelUser)
admin.site.register(Guide)
admin.site.register(ReportUser)

class BookGuidePanel(admin.ModelAdmin):
    model = BookGuide
    list_display = ('travel_user', 'guide_user', 'travel_location', 'booking_date', 'status')
    list_filter = ('travel_user', 'guide_user', 'travel_location', 'status', 'booking_date')
    
admin.site.register(BookGuide, BookGuidePanel)