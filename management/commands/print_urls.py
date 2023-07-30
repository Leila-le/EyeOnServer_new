from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import URLPattern
from django.urls.resolvers import RegexPattern, URLResolver


class Command(BaseCommand):
    help = 'Prints all URL patterns'

    def handle(self, *args, **options):
        urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])
        patterns = self.get_patterns('', urlconf.urlpatterns)
        for pattern in patterns:
            self.stdout.write(str(pattern))

    def get_patterns(self, prefix, patterns):
        result = []
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                result.append(RegexPattern(f'^{prefix}{pattern.pattern}$', pattern.callback.__name__))
            elif isinstance(pattern, URLResolver):
                result += self.get_patterns(f'{prefix}{pattern.pattern}', pattern.url_patterns)
        return result
