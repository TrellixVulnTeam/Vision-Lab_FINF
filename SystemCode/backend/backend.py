'''
Backend Flask App
'''
from importlib import import_module
from app import factory, entities, utils

app = factory.build()

@utils.retry()
def setup():
  entities.init(debug=False)
  try:
    # optional setup.py script
    import_module('app.setup')
  except:
    pass

setup()

if __name__ == '__main__':
  app.run(debug=True)
