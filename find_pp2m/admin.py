from django.contrib import admin
from .models import City, Department, Journey


class CityAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'num_department', 'is_pref', 'is_sous_pref')
    list_filter = ('num_department', 'is_pref', 'is_sous_pref')
    ordering = ('num_department', '-is_pref', 'name')
    search_fields = ('name', 'num_department')


class JourneyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'departure', 'arrival', 'car_distance', 'car_duration')
    list_filter = ('departure', 'arrival')
    ordering = ('departure', 'arrival')
    search_fields = ('departure', 'arrival')


admin.site.register(City, CityAdmin)
admin.site.register(Department)
admin.site.register(Journey, JourneyAdmin)
