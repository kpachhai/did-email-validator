# -*- coding: utf-8 -*-

from app import config
from app.errors import UnauthorizedError


class AuthMiddleware(object):

    def process_request(self, req, res):
        prefetch_token = req.get_header('ACCESS-CONTROL-REQUEST-METHOD')
        if prefetch_token:
            res.complete = True
            return True
        
        if req.path == "/" or req.path == "/v1/validation/callback":
            return True 

    def process_response(self, req, resp, resource, req_succeeded):
        resp.set_header('Access-Control-Allow-Origin', '*')

        if (req_succeeded
            and req.method == 'OPTIONS'
            and req.get_header('Access-Control-Request-Method')
        ):
            # NOTE(kgriffs): This is a CORS preflight request. Patch the
            #   response accordingly.
            allow = resp.get_header('Allow')
            resp.delete_header('Allow')

            allow_headers = req.get_header(
                'Access-Control-Request-Headers',
                default='*'
            )

            resp.set_headers((
                ('Access-Control-Allow-Methods', allow),
                ('Access-Control-Allow-Headers', allow_headers),
                ('Access-Control-Max-Age', '86400'),  # 24 hours
            ))
