class CustomProxyMiddleware(object):
    def __init__(self):
        self.proxy = 'http://177.130.104.118:33333'
    
    def process_request(self, request, spider):
        if 'proxy' not in request.meta:
            request.meta['proxy'] = self.proxy
    
    def get_proxy(self):
        return self.proxy