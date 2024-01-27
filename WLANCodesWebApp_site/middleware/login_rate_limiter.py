from django.core.cache import cache
from django.shortcuts import redirect


class LoginRateLimiterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/accounts/login/' or request.path == '/admin/login/':  # Adjust the login URL as per your project's setup
            # Rate limit per IP
            ip_address = request.META.get('REMOTE_ADDR')
            cache_key_ip = f'login_rate_limit_ip:{ip_address}'
            rate_limit_ip = 60  # Maximum allowed login attempts per IP per minute
            current_attempts_ip = cache.get(cache_key_ip, 0)

            # Rate limit per User
            username = request.POST.get('username')
            cache_key_user = f'login_rate_limit_user:{username}'
            rate_limit_user = 5  # Maximum allowed login attempts per User per minute
            current_attempts_user = cache.get(cache_key_user, 0)
            if current_attempts_ip >= rate_limit_ip or current_attempts_user >= rate_limit_user:
                return redirect('rate_limit_exceeded')
            else:
                if request.method == 'POST':
                    cache.set(cache_key_ip, current_attempts_ip + 1, 60)  # Store attempts per IP for 1 minute
                    cache.set(cache_key_user, current_attempts_user + 1, 60)  # Store attempts per User for 1 minute
        return self.get_response(request)
