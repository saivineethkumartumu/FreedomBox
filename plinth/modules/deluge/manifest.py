# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import ugettext_lazy as _

from plinth.clients import validate
from plinth.modules.backups.api import validate as validate_backup

clients = validate([{
    'name': _('Deluge'),
    'description': _('Bittorrent client written in Python/PyGTK'),
    'platforms': [{
        'type': 'web',
        'url': '/deluge'
    }]
}])

backup = validate_backup({
    'config': {
        'directories': ['/var/lib/deluged/.config']
    },
    'services': ['deluged', 'deluge-web']
})
