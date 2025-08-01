#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2022, Fynn Chen <ethan.cfchen@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
module: keycloak_clientsecret_info

short_description: Retrieve client secret using Keycloak API

version_added: 6.1.0

description:
  - This module allows you to get a Keycloak client secret using the Keycloak REST API. It requires access to the REST API
    using OpenID Connect; the user connecting and the client being used must have the requisite access rights. In a default
    Keycloak installation, admin-cli and an admin user would work, as would a separate client definition with the scope tailored
    to your needs and a user having the expected roles.
  - When retrieving a new client secret, where possible provide the client's O(id) (not O(client_id)) to the module. This
    removes a lookup to the API to translate the O(client_id) into the client ID.
  - 'Note that this module returns the client secret. To avoid this showing up in the logs, please add C(no_log: true) to
    the task.'
attributes:
  action_group:
    version_added: 10.2.0

options:
  realm:
    type: str
    description:
      - They Keycloak realm under which this client resides.
    default: 'master'

  id:
    description:
      - The unique identifier for this client.
      - This parameter is not required for getting or generating a client secret but providing it reduces the number of API
        calls required.
    type: str

  client_id:
    description:
      - The O(client_id) of the client. Passing this instead of O(id) results in an extra API call.
    aliases:
      - clientId
    type: str


extends_documentation_fragment:
  - community.general.keycloak
  - community.general.keycloak.actiongroup_keycloak
  - community.general.attributes
  - community.general.attributes.info_module

author:
  - Fynn Chen (@fynncfchen)
  - John Cant (@johncant)
"""

EXAMPLES = r"""
- name: Get a Keycloak client secret, authentication with credentials
  community.general.keycloak_clientsecret_info:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    auth_realm: master
    auth_username: USERNAME
    auth_password: PASSWORD
  delegate_to: localhost
  no_log: true

- name: Get a new Keycloak client secret, authentication with token
  community.general.keycloak_clientsecret_info:
    id: '9d59aa76-2755-48c6-b1af-beb70a82c3cd'
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost
  no_log: true

- name: Get a new Keycloak client secret, passing client_id instead of id
  community.general.keycloak_clientsecret_info:
    client_id: 'myClientId'
    realm: MyCustomRealm
    auth_client_id: admin-cli
    auth_keycloak_url: https://auth.example.com/auth
    token: TOKEN
  delegate_to: localhost
  no_log: true
"""

RETURN = r"""
msg:
  description: Textual description of whether we succeeded or failed.
  returned: always
  type: str

clientsecret_info:
  description: Representation of the client secret.
  returned: on success
  type: complex
  contains:
    type:
      description: Credential type.
      type: str
      returned: always
      sample: secret
    value:
      description: Client secret.
      type: str
      returned: always
      sample: cUGnX1EIeTtPPAkcyGMv0ncyqDPu68P1
"""

from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak import (
    KeycloakAPI, KeycloakError, get_token)
from ansible_collections.community.general.plugins.module_utils.identity.keycloak.keycloak_clientsecret import (
    keycloak_clientsecret_module, keycloak_clientsecret_module_resolve_params)


def main():
    """
    Module keycloak_clientsecret_info

    :return:
    """

    module = keycloak_clientsecret_module()

    # Obtain access token, initialize API
    try:
        connection_header = get_token(module.params)
    except KeycloakError as e:
        module.fail_json(msg=str(e))

    kc = KeycloakAPI(module, connection_header)

    id, realm = keycloak_clientsecret_module_resolve_params(module, kc)

    clientsecret = kc.get_clientsecret(id=id, realm=realm)

    result = {
        'clientsecret_info': clientsecret,
        'msg': 'Get client secret successful for ID {id}'.format(id=id)
    }

    module.exit_json(**result)


if __name__ == '__main__':
    main()
