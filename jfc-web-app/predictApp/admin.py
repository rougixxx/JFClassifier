from django.contrib import admin
from .models import PredictionHistory

# Register your models here.
@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "java_code",
        "prediction",
        "timestamp"
    ]
    readonly_fields = ["timestamp"]
    list_filter = [
        "prediction",
        "timestamp"
    ]
    search_fields = [
        "prediction",
        "java_code"
    ]