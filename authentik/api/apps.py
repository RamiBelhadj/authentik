"""authentik API AppConfig"""

from django.apps import AppConfig

test
class AuthentikAPIConfig(AppConfig):
    """authentik API Config"""

    name = "authentik.api"
    label = "authentik_api"
    mountpoint = "api/"
    verbose_name = "authentik API"
