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

    print(cli.organizations)  # orgs in the network
    print(cli.peers)  # peers in the network
    print(cli.orderers)  # orderers in the network
    print(cli.CAs)  # ca nodes in the network, TODO

    # get the admin user from local path
    org1_admin = cli.get_user(org_name='org1.example.com', name='Admin')


    # Create a New Channel, the response should be true if succeed
    response = loop.run_until_complete(cli.channel_create(
        orderer='orderer.example.com',
        channel_name='businesschannel',
        requestor=org1_admin,
        config_yaml=CONFIG_YAML_PATH,
        channel_profile='TwoOrgsChannel'
    ))
    if response:
        print("Create channel successful")
    else:
        print("Create channel failed")
        print(response)
        exit(-1)

    # Join Peers into Channel, the response should be true if succeed
    response = loop.run_until_complete(cli.channel_join(
        requestor=org1_admin,
        channel_name='businesschannel',
        peers=['peer0.org1.example.com', 'peer1.org1.example.com'],
        orderer='orderer.example.com'))
    if response:
        print("Join channel successful")
    else:
        print("Join channel failed")
        exit(-1)

    # Join Peers from a different MSP into Channel
    org2_admin = cli.get_user(org_name='org2.example.com', name='Admin')

    # org2_admin is required to operate peers of org2.example.com
    response = loop.run_until_complete(cli.channel_join(
        requestor=org2_admin,
        channel_name='businesschannel',
        peers=['peer0.org2.example.com', 'peer1.org2.example.com'],
        orderer='orderer.example.com'))
    if response:
        print("Join channel successful")
    else:
        print("Join channel failed")
        exit(-1)

    # Install Chaincode to Peers
    # This is only needed if to use the example chaincode inside sdk
    gopath_bak = os.environ.get('GOPATH', '')
    gopath = os.path.normpath(os.path.join(
        os.path.dirname(os.path.realpath('__file__')),
        CHAINCODE_PATH
    ))
    os.environ['GOPATH'] = os.path.abspath(gopath)

    # The response should be true if succeed
    response = loop.run_until_complete(cli.chaincode_install(
        requestor=org1_admin,
        peers=['peer0.org1.example.com', 'peer1.org1.example.com'],
        cc_path='github.com/example_cc',
        cc_name='example_cc',
        cc_version='v1.0'))
    if response:
        print("Install chaincode successful")
    else:
        print("Install chaincode failed")
        exit(-1)

    # Instantiate Chaincode in Channel, the response should be true if succeed
    args = ['a', '200', 'b', '300']
    response = loop.run_until_complete(cli.chaincode_instantiate(
        requestor=org1_admin,
        channel_name='businesschannel',
        peers=['peer0.org1.example.com'],
        args=args,
        cc_name='example_cc',
        cc_version='v1.0'))
    if response:
        print("Instantiate chaincode successful")
    else:
        print("Instantiate chaincode failed")
        exit(-1)


    # The instantiate command after all is a transaction which has to be endorsed, ordered and committed.
    # What probably confuses you is the fact that peer cli succeeded to endorse instantiate transaction and submit it to the ordering service. 
    # While it might not be committed, hence chaincode container not started and as a result you are not able to query your chaincode.
    print(">--- WAITING FOR chaincode container to start after Instantiate! ---<")
    time.sleep(15)
    print(">--- End waiting ---<")


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
        cc_name='example_cc'
    ))
    print("Query chaincode done.")
    print(response)


    ##############################################################################
    # Query Peer installed chaincodes
    response = loop.run_until_complete(cli.query_installed_chaincodes(
        requestor=org1_admin,
        peers=['peer0.org1.example.com']
    ))
    print("Query installed chaincode.")
    print(response)

    # check if channel named "businesschannel" is already exists
    response = cli.get_channel(name="businesschannel")
    print("Channel named `businesschannel`: ", response)

    # query channels joined in by given peers
    response = loop.run_until_complete(cli.query_channels(
        requestor=org1_admin,
        peers=['peer0.org1.example.com']))
    print("Channels: ", response)

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
    ##############################################################################

