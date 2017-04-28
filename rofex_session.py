

#RestfulClient.py

import requests
import json
from getpass import getpass 

class RofexSessionException(Exception):
    pass

class CannotLogin(RofexSessionException):
    pass

class ErrorInRequest(RofexSessionException):
    def __init__(self, url, params):
        super(ErrorInRequest, self).__init__("Error in request. Path: %s. Params: %s" % (url, params) )
        self.url = url
        self.params = params
        
class ServerReportedError(RofexSessionException):
    def __init__(self, url, params, response):
        super(ServerReportedError, self).__init__("Server reported error. Path: %s. Params: %s Json: %s" % (url, params, json.dumps(response)) )
        self.url = url
        self.params = params
        self.response = response
        


class RofexSession(object):
    
    @classmethod
    def params_to_argpaser(cls, arg_parser):
        arg_parser.add_argument(
            "--endpoint", "-e",
            default=None,
            help="Endpoint to connect to (demo, prod or URL) (default: ask)"
        )
        arg_parser.add_argument(
            "--username", "-u",
            default=None,
            help="Username to connect (default: ask)"
        )
        arg_parser.add_argument(
            "--account", "-a",
            default=None,
            help="Account to connect (default: ask)"
        )

    
    @classmethod
    def interactive(cls, args=None, endpoint=None, username=None, account=None, password=None):
        
        if not args is None:
            return cls.interactive(endpoint=args.endpoint, username=args.username, account=args.account)
        
        if endpoint is None:
            endpoint = raw_input('Endpoint (demo, prod or URL): ')
        
        if 'demo' == endpoint:
            endpoint = 'http://demo-api.primary.com.ar:8081/pbcp/'
        elif 'prod' == endpoint:
            endpoint = 'https://api.primary.com.ar/'
        
        if username is None:
            username = raw_input('User: ')
        
        if account is None:
            account = raw_input('Account: ')
        
        if password is None:
            password = getpass('Password: ')
        
        return cls(endpoint=endpoint, userName=username, account=account, password=password)
        
    
    def __init__(self, userName, password, account, endpoint):
        
        self.userName = userName
        self.password = password
        self.account = account
        self.endpoint = endpoint
        self.s = requests.Session()
        self.login()

    def __repr__(self):
        if self.endpoint == 'https://api.primary.com.ar/':
            demoOrProd = 'produccion'
        else: demoOrProd = 'demo'        
        return 'User: {u}\nAccount number: {a}\nProd or demo: {d}\n'.format(u=self.userName, a=self.account, d=demoOrProd)

    def login(self):    
        loginResponse = self.s.post(self.endpoint + "j_spring_security_check", params=dict(j_username=self.userName, j_password=self.password))
        if(loginResponse.ok):
            # Checkeamos si nos pudimos loguear correctamente
            if not ('WebSocket Chat Client' in loginResponse.text):
                raise CannotLogin('Incorrect user or password')
        else:
            raise CannotLogin('Request error')   

    def mass_cancel(self):
        """Cancel all active orders."""
        for order in self.order_actives():
            try:
                print self.order_cancelById(

                    clientId=order['clOrdId'],
                    proprietary=order['proprietary']
                    )
                
            except Exception, e:
                print 'Exception raised: %r' %e


    def segment_all(self):
        """Devuelve todos los segmentos disponibles"""
        
        return self.do_api_call("rest/segment/all", "segments")

    def instruments_all(self):
        """Devuelve instrumentos disponibles"""

        return self.do_api_call("rest/instruments/all", "instruments")

    def instruments_details(self): #instDispDetail
        """Devuelve instrumentos disponibles con detalle"""
        
        return self.do_api_call("rest/instruments/details", "instruments")

    def instruments_detail(self, symbol, market_id="ROFX"): #instDetail
        """Devuelve detalles del instrumento representado por symbol"""
        
        return self.do_api_call(
            "rest/instruments/detail", 
            "instrument",
            dict(symbol=symbol, marketId=market_id)
        )

    def instruments_byCFICode(self, CFICode): # instCFI
        """Devuelve instrumentos con codigo CFI codCFI.
            DBXXXX: Titulos Publicos
            OCXXXS: ?
            FXXXSX: Futuros?
            OXXXPS: Opciones
            ESXXXX: Acciones"""
            
        return self.do_api_call(
            "rest/instruments/byCFICode", 
            "instruments",
            dict(CFICode=CFICode)
        )

    def instruments_bySegment(self, MarketSegmentID, market_id="ROFX"): # instPorSeg
        """Devuelve instrumentos disponibles por segmento MarketSegmentID"""
        return self.do_api_call(
            "rest/instruments/bySegment",
            "instruments",
            dict( MarketSegmentID = MarketSegmentID, MarketId = market_id)
        )


    def marketdata_get(self, symbol, entries, depth=1, market_id="ROFX"): # pedirMD
        
        return self.do_api_call(
            "rest/marketdata/get",
            "marketData",
            dict(
                marketId=market_id,
                symbol=symbol,
                entries=entries,
                depth=str(depth)
            )
        )

    def order_actives(self): # activas
        
        return self.do_api_call("rest/order/actives", "orders", dict(accountId=self.account))

    def order_all(self): # allOrders
        
        return self.do_api_call("rest/order/all", "orders", dict(accountId=self.account))
                         
    def order_filleds(self): # filled
        
        return self.do_api_call("rest/order/filleds", "orders", dict(accountId=self.account))
    
    def order_id(self, clientId, proprietary): #cl_ord_id
        
        return self.do_api_call("rest/order/id", "order", dict(clOrdId=clientId, proprietary=proprietary))
    
    def order_allById(self, clientId, proprietary):
        
        return self.do_api_call("rest/order/allById", "orders", dict(clOrdId=clientId, proprietary=proprietary))
    
    def order_cancelById(self, clientId, proprietary):
        return self.do_api_call("rest/order/cancelById", "order", dict(clOrdId=clientId, proprietary=proprietary))
    
    def insWithMHD(self): # Why is this connecting to a different server? (Aureliano, 2016-08-27)
        url = 'http://h-api.primary.com.ar/MHD/instruments/all'
        r = self.requestAPI(url)
        return json.loads(r.content)
  
    def order_newSingleOrder(self, symbol, price, orderQty, side, market_id='ROFX', ord_type='LIMIT', time_in_force='Day', cancel_previous=False): #newSingleOrder
        
        return self.do_api_call(
            "rest/order/newSingleOrder",
            "order",
            dict(
                marketId=market_id,
                symbol=symbol,
                price=str(price),
                orderQty=orderQty,
                ordType=ord_type,
                side=side,
                timeInForce=time_in_force,
                account=self.account,
                cancelPrevious=str(cancel_previous).lower()
            )
        )
        
    def do_api_call(self, path, result_field, params={}):
        url = self.endpoint + path
        r = self.s.get(url, params=params)
        if r.ok:
            response = json.loads(r.content)
            if "OK" <> response["status"]:
                raise ServerReportedError(url, params, response) 
            return response[result_field]
        else:
            raise ErrorInRequest(url, params)
            
    

    
