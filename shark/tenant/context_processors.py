def tenant(request):
    return {"tenant": getattr(request, "tenant", None)}
