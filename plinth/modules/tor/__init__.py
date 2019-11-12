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
FreedomBox app to configure Tor.
"""

import json

from django.utils.translation import ugettext_lazy as _

from plinth import action_utils, actions
from plinth import app as app_module
from plinth import menu
from plinth.daemon import Daemon
from plinth.modules.firewall.components import Firewall
from plinth.modules.names.components import DomainType
from plinth.signals import domain_added, domain_removed

from . import utils
from .manifest import backup, clients  # noqa, pylint: disable=unused-import

version = 3

depends = ['names']

managed_packages = [
    'tor', 'tor-geoipdb', 'torsocks', 'obfs4proxy', 'apt-transport-tor'
]

managed_services = ['tor@plinth']

name = _('Tor')

short_description = _('Anonymity Network')

description = [
    _('Tor is an anonymous communication system. You can learn more '
      'about it from the <a href="https://www.torproject.org/">Tor '
      'Project</a> website. For best protection when web surfing, the '
      'Tor Project recommends that you use the '
      '<a href="https://www.torproject.org/download/download-easy.html.en">'
      'Tor Browser</a>.')
]

clients = clients

reserved_usernames = ['debian-tor']

manual_page = 'Tor'

app = None


class TorApp(app_module.App):
    """FreedomBox app for Tor."""

    app_id = 'tor'

    def __init__(self):
        """Create components for the app."""
        super().__init__()
        menu_item = menu.Menu('menu-tor', name, short_description, 'tor',
                              'tor:index', parent_url_name='apps')
        self.add(menu_item)

        domain_type = DomainType('domain-type-tor', _('Tor Onion Service'),
                                 'tor:index', can_have_certificate=False)
        self.add(domain_type)

        firewall = Firewall('firewall-tor-socks', _('Tor Socks Proxy'),
                            ports=['tor-socks'], is_external=False)
        self.add(firewall)

        firewall = Firewall('firewall-tor-relay', _('Tor Bridge Relay'),
                            ports=['tor-orport', 'tor-obfs3',
                                   'tor-obfs4'], is_external=True)
        self.add(firewall)

        daemon = Daemon('daemon-tor', managed_services[0], strict_check=True)
        self.add(daemon)


def init():
    """Initialize the module."""
    global app
    app = TorApp()

    setup_helper = globals()['setup_helper']
    needs_setup = setup_helper.get_state() == 'needs-setup'

    if not needs_setup:
        if app.is_enabled():
            app.set_enabled(True)

        # Register hidden service name with Name Services module.
        status = utils.get_status()
        hostname = status['hs_hostname']
        services = [int(port['virtport']) for port in status['hs_ports']]

        if status['enabled'] and status['is_running'] and \
           status['hs_enabled'] and status['hs_hostname']:
            domain_added.send_robust(sender='tor',
                                     domain_type='domain-type-tor',
                                     name=hostname, services=services)


def setup(helper, old_version=None):
    """Install and configure the module."""
    helper.install(managed_packages)
    helper.call(
        'post', actions.superuser_run, 'tor',
        ['setup', '--old-version', str(old_version)])
    if not old_version:
        helper.call('post', actions.superuser_run, 'tor',
                    ['configure', '--apt-transport-tor', 'enable'])

    helper.call('post', update_hidden_service_domain)
    helper.call('post', app.enable)


def update_hidden_service_domain(status=None):
    """Update HS domain with Name Services module."""
    if not status:
        status = utils.get_status()

    domain_removed.send_robust(sender='tor', domain_type='domain-type-tor')

    if status['enabled'] and status['is_running'] and \
       status['hs_enabled'] and status['hs_hostname']:
        services = [int(port['virtport']) for port in status['hs_ports']]
        domain_added.send_robust(sender='tor', domain_type='domain-type-tor',
                                 name=status['hs_hostname'], services=services)


def diagnose():
    """Run diagnostics and return the results."""
    results = []
    results.append(action_utils.diagnose_port_listening(9050, 'tcp4'))
    results.append(action_utils.diagnose_port_listening(9050, 'tcp6'))
    results.append(action_utils.diagnose_port_listening(9040, 'tcp4'))
    results.append(action_utils.diagnose_port_listening(9040, 'tcp6'))
    results.append(action_utils.diagnose_port_listening(9053, 'udp4'))
    results.append(action_utils.diagnose_port_listening(9053, 'udp6'))

    results.extend(_diagnose_control_port())

    output = actions.superuser_run('tor', ['get-status'])
    ports = json.loads(output)['ports']

    results.append([
        _('Tor relay port available'),
        'passed' if 'orport' in ports else 'failed'
    ])
    if 'orport' in ports:
        results.append(
            action_utils.diagnose_port_listening(int(ports['orport']), 'tcp4'))
        results.append(
            action_utils.diagnose_port_listening(int(ports['orport']), 'tcp6'))

    results.append([
        _('Obfs3 transport registered'),
        'passed' if 'obfs3' in ports else 'failed'
    ])
    if 'obfs3' in ports:
        results.append(
            action_utils.diagnose_port_listening(int(ports['obfs3']), 'tcp4'))

    results.append([
        _('Obfs4 transport registered'),
        'passed' if 'obfs4' in ports else 'failed'
    ])
    if 'obfs4' in ports:
        results.append(
            action_utils.diagnose_port_listening(int(ports['obfs4']), 'tcp4'))

    results.append(_diagnose_url_via_tor('http://www.debian.org', '4'))
    results.append(_diagnose_url_via_tor('http://www.debian.org', '6'))

    results.append(_diagnose_tor_use('https://check.torproject.org', '4'))
    results.append(_diagnose_tor_use('https://check.torproject.org', '6'))

    return results


def _diagnose_control_port():
    """Diagnose whether Tor control port is open on 127.0.0.1 only."""
    results = []

    addresses = action_utils.get_ip_addresses()
    for address in addresses:
        if address['kind'] != '4':
            continue

        negate = True
        if address['address'] == '127.0.0.1':
            negate = False

        results.append(
            action_utils.diagnose_netcat(address['address'], 9051,
                                         input='QUIT\n', negate=negate))

    return results


def _diagnose_url_via_tor(url, kind=None):
    """Diagnose whether a URL is reachable via Tor."""
    result = action_utils.diagnose_url(url, kind=kind, wrapper='torsocks')
    result[0] = _('Access URL {url} on tcp{kind} via Tor') \
        .format(url=url, kind=kind)

    return result


def _diagnose_tor_use(url, kind=None):
    """Diagnose whether webpage at URL reports that we are using Tor."""
    expected_output = 'Congratulations. This browser is configured to use Tor.'
    result = action_utils.diagnose_url(url, kind=kind, wrapper='torsocks',
                                       expected_output=expected_output)
    result[0] = _('Confirm Tor usage at {url} on tcp{kind}') \
        .format(url=url, kind=kind)

    return result
