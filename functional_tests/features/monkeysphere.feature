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

@apps @monkeysphere
Feature: Monkeysphere
  Import and publish OpenPGP keys for SSH and HTTPS keys

Background:
  Given I'm a logged in user
  And the monkeysphere application is installed
  And the domain name is set to mydomain.example

Scenario: Import SSH keys
  When I import SSH key for mydomain.example in monkeysphere
  Then the SSH key should imported for mydomain.example in monkeysphere

Scenario: Import HTTPS keys
  When I import HTTPS key for mydomain.example in monkeysphere
  Then the HTTPS key should imported for mydomain.example in monkeysphere

Scenario: Publish SSH keys
  Given the SSH key for mydomain.example is imported in monkeysphere
  Then I should be able to publish SSH key for mydomain.example in monkeysphere

Scenario: Publish HTTPS keys
  Given the HTTPS key for mydomain.example is imported in monkeysphere
  Then I should be able to publish HTTPS key for mydomain.example in monkeysphere
