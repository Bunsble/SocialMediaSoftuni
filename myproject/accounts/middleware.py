from django.contrib import admin
from django.shortcuts import redirect

class RestrictStaffToPostsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and request.user.is_authenticated and request.user.is_staff and not request.user.is_superuser:
            if not request.path.startswith('/admin/accounts/post/'):
                return redirect('admin:accounts_post_changelist')
        return self.get_response(request)