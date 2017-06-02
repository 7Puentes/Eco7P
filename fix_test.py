import sys
import argparse
import quickfix as fix

class Application(fix.Application):
    orderID = 0
    execID = 0
    def gen_ord_id(self):
        global orderID
        orderID+=1
        return orderID

    def onCreate(self, sessionID):
        """

        :param sessionID:
        :return:
        """
        return
    def onLogon(self, sessionID):
            self.sessionID = sessionID
            print ("Successful Logon to session '%s'." % sessionID.toString())
            return

    def onLogout(self, sessionID): return

    def toAdmin(self, sessionID, message):
        print "Sent the Admin following message: %s" % message.toString()
        return

    def fromAdmin(self, sessionID, message):
        print "Received the Admin following message: %s" % message.toString()
        return

    def toApp(self, sessionID, message):
        print "Sent the following message: %s" % message.toString()
        return

    def fromApp(self, message, sessionID):
        print "Received the following message: %s" % message.toString()
        return

    def genOrderID(self):
        self.orderID = self.orderID+1
        return `self.orderID`

    def genExecID(self):
        self.execID = self.execID+1
        return `self.execID`

    def put_order(self):
        print("Creating the following order: ")
        trade = fix.Message()
        trade.setField(fix.ClOrdID(self.genExecID())) #11=Unique order
        trade.setField(fix.HandlInst(fix.HandlInst_MANUAL_ORDER_BEST_EXECUTION))
        trade.setField(fix.Symbol('SMBL'))
        trade.setField(fix.Side(fix.Side_BUY))
        trade.setField(fix.OrdType(fix.OrdType_LIMIT))
        trade.setField(fix.OrderQty(100))
        trade.setField(fix.Price(10))
        print trade.toString()
        fix.Session.sendToTarget(trade, self.sessionID)

def main(config_file):
    try:
        settings = fix.SessionSettings("settings.cfg")
        application = Application()
        storeFactory = fix.FileStoreFactory(settings)
        logFactory = fix.FileLogFactory(settings)
        initiator = fix.SocketInitiator(application, storeFactory, settings, logFactory)
        initiator.start()

        while 1:
                input = raw_input()
                if input == '1':
                    print "Putin Order"
                    application.put_order()
                if input == '2':
                    sys.exit(0)
                if input == 'd':
                    import pdb
                    pdb.set_trace()
                else:
                    print "Valid input is 1 for order, 2 for exit"
                    continue
    except (fix.ConfigError, fix.RuntimeError), e:
        print e

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='FIX Client')
    parser.add_argument('file_name', type=str, help='Name of configuration file', default="settings.cfg")
    args = parser.parse_args(args=["settings.cfg"])
    main(args.file_name)