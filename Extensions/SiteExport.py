
## Config this should get dumped to a text config file
## instead of python code

import os
from os import path
from Acquisition import aq_base, aq_inner, aq_parent
from Globals import package_home
from Interface import Base
from StringIO import StringIO
from cgi import escape
from Products.Formulator.XMLSerialize import formToXML

class IExporter: 
  
  """
  Interfaces are sugar
  """

  def export(self, object, directory): 
    """
    take an object and put a file system representation
    of that object in directory
    """
  
class DTMLExporter:
  
  __implements__ = (IExporter,)
  
  allowed_endings = ('css', 'js', 'html')
  
  def export(self, object, directory): 

    id = object.getId()

    #if not id[id.rfind('.')+1:] in self.allowed_endings:
    id = id + '.dtml'

    source = object.raw
    
    fh = open(path.join(directory,id), 'w')
    fh.write(source)
    fh.close()

class PtExporter:
   __implements__ = (IExporter,)

   allowed_endings = ('pt', 'zpt')
 
   def export(self, object, directory):
       id = object.getId()

       id = id + '.pt'

       source = object.read()

       fh = open(path.join(directory,id), 'w')
       fh.write(source)
       fh.close()
       
class ScriptExporter:

  __implements__ = (IExporter,)
  
  allowed_endings = ('py',)
  
  def export(self, object, directory):
    
    id = object.getId()
    
    #if not id[id.rfind('.')+1:] in self.allowed_endings:
    id = id + '.py'
    
    source = object.document_src()
    
    fh = open(path.join(directory,id), 'w')
    fh.write(source)
    fh.close()

class ExternalMethodExporter:

  __implements__ = (IExporter,)

  allowed_endings = ('ext',)

  def export (self, object, directory):

    id = object.getId()

    #if not id[id.rfind('.')+1:] in self.allowed_endings:
    id = id + '.ext'

    fh = open(path.join(directory,id),'w')

    print >> fh, '# external method'
    print >> fh, ' title  : %s'%object.title
    print >> fh, ' module : %s'%object._module
    print >> fh, ' function : %s'%object._function

    fh.close()
    
   
class ImageExporter:

  __implements__ = (IExporter,)  
  
  allowed_endings = ('gif','png','jpg','jpeg')
  
  def export(self, object, directory):

    id = object.getId()

    if id[id.rfind('.')+1:] not in self.allowed_endings:
      return
    
    fh = open(path.join(directory,id), 'w')
    
    data = obj.data
    
    if type( data) == type (''):
      fh.write(data)
      
    else:
      while data is not None:
        fh.write(data.data)
        data = data.next

class SQLExporter:

  __implements__ = (IExporter,)  
  
  allowed_endings = ('zsql',)
  
  default_db = 'ardyssdb' ## we need this because of the funky ReadConsistentZSQL

  def export(self, object, directory):
    
    id = object.getId()
    
    #if id[id.rfind('.')+1:] not in self.allowed_endings:
    id = id+'.zsql'
      
    meta_data = {}
    
    meta_data['connection_id'] = getattr(aq_base(object),
                                         'connection_id', 
                                         self.default_db)
    
    meta_data['max_cache']  = getattr(object, 'max_cache_', 100)
    meta_data['max_rows']   = getattr(object, 'max_rows_', 0)
    meta_data['cache_time'] = getattr(object, 'cache_time_', 0)
    meta_data['title']      = getattr(object, 'title', '')
    meta_data['arguments']  = getattr(object, 'arguments_src', '').replace('\n',',')
    
    param_def = """
    <dtml-comment>
    connection_id:%(connection_id)s
    arguments:%(arguments)s
    max_cache:%(max_cache)s
    max_rows:%(max_rows)s
    </dtml-comment>
    """%meta_data

    fh = open(path.join(directory,id), 'w')
    fh.write(param_def+object.src)
    fh.close()
    

class FormulatorFormExporter:
  __implements__ = (IExporter,)

  allowed_endings = ('form',)

  def export(self, object, directory):
    id = object.getId()    
    id = id + '.form'
    source = formToXML(object)
    fh = open(path.join(directory,id), 'w')
    fh.write(source)
    fh.close()   
    
meta_type_mapping = {'Z SQL Method':SQLExporter(),
                     'ReadConsistentZSQL':SQLExporter(),
                     'Script (Python)':ScriptExporter(),
                     'Page Template':PtExporter(),  
                     'DTML Method':DTMLExporter(),
                     'DTML Document':DTMLExporter(),
                     'External Method':ExternalMethodExporter(),
                     'Formulator Form':FormulatorFormExporter(),
                     }


#export_directory = '/home/ender/codeit/Products/SkinZ/export'
export_directory = '/home/faassen/working/export'
#export_directory = '/projects/ardyss/dev/Products/ArdyssSite/export'

def recurse_export(container, directory):

  print  
  print
  print 'exporting', container.getId(), directory
  
  objs = container.objectValues(meta_type_mapping.keys())
  
  print len(objs)
  
  for o in objs:
    print o.getId(), o.meta_type
    handler = meta_type_mapping.get(o.meta_type)
    handler.export(o, directory)
    # # export properties
    # f = open(d + '.properties', 'w')
    # for key, value in c.propertyItems():
    #   f.write('%s=%s\n' % (key, value))
    # f.close()
  print    

  containers = container.objectValues('Folder')
  for c in containers:
    d = path.join(directory,  c.getId())
    try:
      os.mkdir(d)
    except OSError:  # hopefully it already exists ;)
      pass
    
    recurse_export(c, d)
  
def export_container(container, export_directory=export_directory):
  
   #path = package_home(globals())
  directory = export_directory
  
  try:
    os.mkdir(directory)
  except: pass

  recurse_export(container, directory)
            
  return 'something pleasant'

def main():
  
  container = load_container()
  export_container(container)
      
#if __name__ == '__main__':
#  main()
