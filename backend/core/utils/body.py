async def read_json(request):
    try:
        return await request.json()
    except ValueError:
        return None
