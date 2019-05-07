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

@apps @i2p-app
Feature: I2P Anonymity Network
  Manage I2P configuration.

Background:
  Given I'm a logged in user
  Given the i2p application is installed

Scenario: Enable i2p application
  Given the i2p application is disabled
  When I enable the i2p application
  Then the i2p service should be running

Scenario: Disable i2p application
  Given the i2p application is enabled
  When I disable the i2p application
  Then the i2p service should not be running