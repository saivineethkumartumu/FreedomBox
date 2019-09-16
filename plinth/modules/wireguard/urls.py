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
URLs for the wireguard module.
"""

from django.conf.urls import url

from plinth.modules.wireguard import views

urlpatterns = [
    url(r'^apps/wireguard/$', views.WireguardView.as_view(), name='index'),
    url(r'^apps/wireguard/client/add/$', views.AddClientView.as_view(),
        name='add-client'),
    url(r'^apps/wireguard/client/(?P<public_key>[^/]+)/show/$',
        views.ShowClientView.as_view(), name='show-client'),
    url(r'^apps/wireguard/client/(?P<public_key>[^/]+)/delete/$',
        views.DeleteClientView.as_view(), name='delete-client'),
    url(r'^apps/wireguard/server/add/$', views.AddServerView.as_view(),
        name='add-server'),
    url(r'^apps/wireguard/server/(?P<public_key>[^/]+)/show/$',
        views.ShowServerView.as_view(), name='show-server'),
]