from sqlalchemy.orm import scoped_session, sessionmaker
from pylons import config
import elixir

Session = scoped_session (
  sessionmaker (
    autoflush=True,
    transactional=True
  )
)
elixir.session = Session
elixir.options_defaults.update ({"shortnames" : True})
  
metadata = elixir.metadata
metadata.bind = config['pylons.g'].default_engine

#~ def init_model (engine):
  #~ metadata.bind = engine
  
from entities import *
elixir.setup_all ()
