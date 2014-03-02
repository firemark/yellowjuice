from .models import Language


def langs(request):
    return {"langs": Language.objects.filter(visible=True)}
