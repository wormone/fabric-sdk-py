# Copyright O Corp. 2019 All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#

import os
import time
import asyncio
from hfc.fabric import Client

CONNECTION_PROFILE_PATH = 'test/fixtures/network.json'
CONFIG_YAML_PATH = 'test/fixtures/e2e_cli/'
CHAINCODE_PATH = 'test/fixtures/chaincode'

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    cli = Client(net_profile=CONNECTION_PROFILE_PATH)

    # get the admin user from local path
    org1_admin = cli.get_user(org_name='org1.example.com', name='User1')
    
    # Query Peer installed chaincodes
    response = loop.run_until_complete(cli.query_installed_chaincodes(
        requestor=org1_admin,
        peers=['peer0.org1.example.com']
    ))
    print("Query installed chaincode.")
    print(response)

    # query channels joined in by given peers
    response = loop.run_until_complete(cli.query_channels(
        requestor=org1_admin,
        peers=['peer0.org1.example.com']))
    print("Channels: ", response)

    # check if channel named "businesschannel" is already exists
    response = cli.get_channel(name="businesschannel")
    print("Channel named `businesschannel`: ", response)

    # previously created channel must be declared with new_channel() for future using
    response = cli.new_channel(name="businesschannel")
    print("New add channel: ", response)
    response = cli.get_channel(name="businesschannel")
    print("Channel named `businesschannel`: ", response)

    # query channel info of a given channel named "businesschannel"
    response = loop.run_until_complete(cli.query_info(
        requestor=org1_admin,
        channel_name="businesschannel",
        peers=['peer0.org1.example.com']))
    print("Channels: ", response)

    # Get channel config
    response = loop.run_until_complete(cli.get_channel_config(
        requestor=org1_admin,
        channel_name='businesschannel',
        peers=['peer0.org1.example.com']
    ))
    print("Get channel config done.")
    print(response)

    # Invoke a chaincode
    args = ['a', 'b', '100']
    # The response should be true if succeed
    response = loop.run_until_complete(cli.chaincode_invoke(
        requestor=org1_admin,
        channel_name='businesschannel',
        peers=['peer0.org1.example.com'],
        args=args,
        cc_name='example_cc'
    ))
    print("Invoke chaincode done.")
    print(response)

    # Query a chaincode
    args = ['b']
    # The response should be true if succeed
    response = loop.run_until_complete(cli.chaincode_query(
        requestor=org1_admin,
        channel_name='businesschannel',
        peers=['peer0.org1.example.com'],
        args=args,
        cc_name='example_cc',
        fcn='query'  # 'query' as default
    ))
    print("Query chaincode done.")
    print(response)

