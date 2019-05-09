#
# This file is part of FreedomBox.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
FreedomBox app for monkeysphere.
"""

from django.utils.translation import ugettext_lazy as _

from plinth import app as app_module
from plinth import menu

from .manifest import backup

version = 1

managed_packages = ['monkeysphere']

name = _('Monkeysphere')

description = [
    _('With Monkeysphere, an OpenPGP key can be generated for each configured '
      'domain serving SSH. The OpenPGP public key can then be uploaded to the '
      'OpenPGP keyservers. Users connecting to this machine through SSH can '
      'verify that they are connecting to the correct host.  For users to '
      'trust the key, at least one person (usually the machine owner) must '
      'sign the key using the regular OpenPGP key signing process.  See the '
      '<a href="http://web.monkeysphere.info/getting-started-ssh/"> '
      'Monkeysphere SSH documentation</a> for more details.'),
    _('Monkeysphere can also generate an OpenPGP key for each Secure Web '
      'Server (HTTPS) certificate installed on this machine. The OpenPGP '
      'public key can then be uploaded to the OpenPGP keyservers. Users '
      'accessing the web server through HTTPS can verify that they are '
      'connecting to the correct host. To validate the certificate, the user '
      'will need to install some software that is available on the '
      '<a href="https://web.monkeysphere.info/download/"> Monkeysphere '
      'website</a>.')
]

manual_page = "Monkeysphere"

reserved_usernames = ['monkeysphere']

app = None


class MonkeysphereApp(app_module.App):
    """FreedomBox app for Monkeysphere."""

    def __init__(self):
        """Create components for the app."""
        super().__init__()
        menu_item = menu.Menu('menu-monkeysphere', name, None,
                              'fa-certificate', 'monkeysphere:index',
                              parent_url_name='system')
        self.add(menu_item)


def init():
    """Initialize the monkeysphere module."""
    global app
    app = MonkeysphereApp()
    app.set_enabled(True)


def setup(helper, old_version=None):
    """Install and configure the module."""
    helper.install(managed_packages)
