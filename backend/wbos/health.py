from django.db import connection
from django.http import JsonResponse


def healthz(request):
    return JsonResponse({'status': 'ok'})


def readyz(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
    except Exception:
        return JsonResponse({'status': 'unavailable', 'database': 'unavailable'}, status=503)
    return JsonResponse({'status': 'ok', 'database': 'ok'})