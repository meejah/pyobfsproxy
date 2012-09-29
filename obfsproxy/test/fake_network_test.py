from twisted.trial import unittest
from twisted.test import proto_helpers
from twisted.internet import reactor, defer
from twisted.internet.protocol import Factory, BaseProtocol

import obfsproxy.network.network as network
import obfsproxy.transports.dummy as dummy

TEST_FILE = '''some
data
on
multiple lines'''

class ObfsCircuitTests(unittest.TestCase):

    def setUp(self):
        self.server_transport = proto_helpers.StringTransport()
        self.client_transport = proto_helpers.StringTransport()

        ## this could be made more-better if
        ## StaticDestinationServerFactory took the reactor (and
        ## really, all it wants is IReactorTCP) as a parameter. Then,
        ## I could pass in a fake one (an instance of this class,
        ## even, implementing IReactorTCP) which just calls
        ## buildProtocol as soon as connectTCP is called
        
        factory = network.StaticDestinationServerFactory(('127.0.0.1', 0), 'server', dummy.DummyServer())
        # print "TRANS", factory.transport
        self.obfs_server_proto = factory.buildProtocol(('127.0.0.1', 0))
        self.obfs_client_proto = network.StaticDestinationClientFactory(self.obfs_server_proto.circuit, 'server').buildProtocol(('127.0.0.1', 0))

        self.obfs_server_proto.makeConnection(self.server_transport)
        self.obfs_client_proto.makeConnection(self.client_transport)

    def test_client_transfer(self):
        self.assertTrue(self.obfs_server_proto.circuit.circuitIsReady())
        self.obfs_server_proto.dataReceived(TEST_FILE)
        self.assertEqual(self.client_transport.value(), TEST_FILE)

    def test_chunked_client_transfer(self):
        self.assertTrue(self.obfs_server_proto.circuit.circuitIsReady())
        for i in range(0, len(TEST_FILE), 5):
            self.obfs_server_proto.dataReceived(TEST_FILE[i:i+5])
        self.assertEqual(self.client_transport.value(), TEST_FILE)
