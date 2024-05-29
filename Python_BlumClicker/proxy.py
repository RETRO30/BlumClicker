from mitmproxy import http

def response(flow: http.HTTPFlow) -> None:
    if "https://telegram.blum.codes" in flow.request.pretty_url:
        headers_to_remove = ["Content-Security-Policy", "X-Frame-Options", "content-security-policy", "x-frame-options",]
        for header in headers_to_remove:
            if header in flow.response.headers:
                flow.response.headers.pop(header)