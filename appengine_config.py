import os
from google.appengine.ext import vendor

vendor.add('lib')

if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    import imp
    import os.path
    import inspect

    # Use the system socket.
    real_os_src_path = os.path.realpath(inspect.getsourcefile(os))
    psocket = os.path.join(os.path.dirname(real_os_src_path), 'socket.py')
    imp.load_source('socket', psocket)

# handle requests_toolbelt's monkeypatch as you see fit.
