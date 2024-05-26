import requests
from requests.adapters import HTTPAdapter, Retry

def requests_retry_session(retries=5, backoff_factor=0.3, status_forcelist=(500, 502, 503, 504), session=None):
    session = session or requests.Session() 
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["POST"]
    )
    adapter = HTTPAdapter(max_retries=retry) #configures a session with retry logic for handling request failures
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
