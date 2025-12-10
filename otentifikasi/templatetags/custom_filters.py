from django import template

register = template.Library()

@register.filter
def intersection(group_list1, group_list2):
    return group_list1 & group_list2

# dashboard/templatetags/custom_filters.py
from django import template
from django.utils import timezone
from datetime import timedelta
import pytz
from dateutil import parser

register = template.Library()


@register.filter
def convert_to_utc_plus_7(value):
    """
    Mengonversi string datetime ke zona waktu UTC+7 dan memformatnya sebagai 'YYYY-MM-DD HH:MM:SS'.
    Jika datetime sudah dalam UTC+7, tidak akan diubah.
    """
    if not value:
        return "N/A"
    try:
        # Parsing string datetime menjadi objek datetime
        dt = parser.isoparse(value)

        # Definisikan zona waktu target UTC+7
        target_tz = pytz.FixedOffset(420)  # 7 * 60 menit

        if dt.tzinfo is None:
            # Jika datetime naive, asumsikan UTC
            dt = timezone.make_aware(dt, timezone.utc)

        # Konversi ke zona waktu target
        dt_converted = dt.astimezone(target_tz)

        # Format datetime
        return dt_converted.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        # Jika terjadi error saat parsing, kembalikan nilai asli
        return value
