class FixHostHeaderMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if ',' in request.META.get('HTTP_HOST', ''):
            # Fix the problematic header
            request.META['HTTP_HOST'] = request.META['HTTP_HOST'].split(',')[0]
        return self.get_response(request)