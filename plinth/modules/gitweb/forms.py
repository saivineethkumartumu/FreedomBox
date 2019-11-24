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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
"""
Django form for configuring Gitweb.
"""

import re
from urllib.parse import urlparse

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import ugettext_lazy as _

from plinth.modules import gitweb


def get_name_from_url(url):
    """Get a repository name from URL"""
    return urlparse(url).path.split('/')[-1]


def is_repo_url(url):
    """Check if URL is valid."""
    try:
        RepositoryValidator(input_should_be='url')(url)
    except ValidationError:
        return False

    return True


class RepositoryValidator:
    input_should_be = 'name'

    def __init__(self, input_should_be=None):
        if input_should_be is not None:
            self.input_should_be = input_should_be

    def __call__(self, value):
        """Validate that the input is a correct repository name or URL"""
        if self.input_should_be in ('url', 'url_or_name'):
            try:
                URLValidator(schemes=['http', 'https'],
                             message=_('Invalid repository URL.'))(value)
            except ValidationError:
                if self.input_should_be == 'url':
                    raise
            else:
                value = get_name_from_url(value)

        if (not re.match(r'^[a-zA-Z0-9-._]+$', value)) \
                or value.startswith(('-', '.')) \
                or value.endswith('.git.git'):
            raise ValidationError(_('Invalid repository name.'), 'invalid')


class CreateRepoForm(forms.Form):
    """Form to create and edit a new repository."""

    name = forms.CharField(
        label=_(
            'Name of a new repository or URL to import an existing repository.'
        ), strip=True,
        validators=[RepositoryValidator(input_should_be='url_or_name')],
        widget=forms.TextInput(attrs={'autocomplete': 'off'}))

    description = forms.CharField(
        label=_('Description of the repository'), strip=True, required=False,
        help_text=_('Optional, for displaying on Gitweb.'))

    owner = forms.CharField(
        label=_('Repository\'s owner name'), strip=True, required=False,
        help_text=_('Optional, for displaying on Gitweb.'))

    is_private = forms.BooleanField(
        label=_('Private repository'), required=False,
        help_text=_('Allow only authorized users to access this repository.'))

    def __init__(self, *args, **kwargs):
        """Initialize the form with extra request argument."""
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'autofocus': 'autofocus'})

    def clean_name(self):
        """Check if the name is valid."""
        name = self.cleaned_data['name']

        repo_name = name
        if is_repo_url(name):
            repo_name = get_name_from_url(name)

        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]

        for repo in gitweb.app.get_repo_list():
            if repo_name == repo['name']:
                raise ValidationError(
                    _('A repository with this name already exists.'))

        if is_repo_url(name):
            if not gitweb.repo_exists(name):
                raise ValidationError('Remote repository is not available.')

        return name


class EditRepoForm(CreateRepoForm):
    """Form to create and edit a new repository."""

    name = forms.CharField(
        label=_('Name of the repository'),
        strip=True,
        validators=[RepositoryValidator()],
        help_text=_(
            'An alpha-numeric string that uniquely identifies a repository.'),
    )

    def clean_name(self):
        """Check if the name is valid."""
        name = self.cleaned_data['name']
        if 'name' in self.initial and name == self.initial['name']:
            return name

        if name.endswith('.git'):
            name = name[:-4]

        for repo in gitweb.app.get_repo_list():
            if name == repo['name']:
                raise ValidationError(
                    _('A repository with this name already exists.'))

        return name
