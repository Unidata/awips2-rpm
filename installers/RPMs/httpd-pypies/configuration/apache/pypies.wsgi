import site
site.addsitedir('/awips2/python/lib/python3.11/site-packages')

import pypies.handlers
application = pypies.handlers.pypies_response
