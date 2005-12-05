#!/usr/bin/env python2.1

# Original code by Guido Westorp <guido@infrae.com>
# enhanced/rewritten by holger krekel <hpk@devel.trillke.net>
# public domain

import os, sys
import transaction

def ignore_dir(fullfn):
    """ filter function for ignoring certain directories """
    bn = os.path.basename(fullfn)
    return bn=='CVS' or bn[:1]=='.'

def ensure_folder(node, name, title = None):
    """ return folder object (and creates it if neccessry """
    try:
        return getattr(node, name)
    except:
        title = title or "from %s" % name
        node.manage_addFolder(name, title)
        print "diradd", title
        return getattr(node, name)
    
def fs_to_zodb(fsdirname, target):
    """ Copy file system contents of fsdirname to zope target """
    for fn in os.listdir(fsdirname):
    	fullfn = os.path.join(fsdirname, fn)
        if os.path.isdir(fullfn):
            if ignore_dir(fullfn):
                print "ignore",fullfn
            else:
                fs_to_zodb(fullfn, ensure_folder(target, fn, fullfn))
        else:
            method = 'addfile'
            try:
                target.manage_addFile(fn, open(fullfn).read()) 
            except:
                if not force_overwrite:
                    print "could not copy %s to Zope Database" % repr(fullfn)
                    print "please specify -f to force overwrite"
                    raise SystemExit(1)
                target.manage_delObjects([fn])
                target.manage_addFile(fn, open(fullfn).read())
                method = 'replacefile'

            print method, fullfn, "to", '.../'+target.id+'/'+fn

def usage():
    print "Usage: %s [-f] <dirname> <ZODBtarget path>" % sys.argv[0]
    print "-f       force overwrite if file already exists"
    print "-i path  set INSTANCE_HOME to path"
    print "         (and SOFTWARE_HOME to path/lib/python) if not specified explicitely"
    print "-s path  set SOFTWARE_HOME to path"
    raise SystemExit(1)

if __name__=='__main__':
    import getopt
    optlist,args = getopt.getopt(sys.argv[1:], 'fi:s:')
    force_overwrite = None
    instance_home = os.environ.get('INSTANCE_HOME')
    software_home = os.environ.get('SOFTWARE_HOME')

    for option, value in optlist:
        if option=='-f':
            force_overwrite = 1
        elif option=='-i':
            instance_home=value
        elif option=='-s':
            software_home=value

    if not instance_home:
        print "ERROR: INSTANCE_HOME not set"
        usage()
    if not os.path.exists(instance_home):
        print "ERROR: not existing INSTANCE_HOME directory:", str(instance_home)
        usage()
    if not software_home:
        software_home = os.path.join(instance_home, 'lib', 'python')
        if not os.path.exists(software_home):
            print "ERROR: not existing SOFTWARE_HOME", software_home
            usage()

    os.putenv('INSTANCE_HOME', instance_home)
    os.environ['INSTANCE_HOME']= instance_home
    os.putenv('SOFTWARE_HOME', software_home)
    os.environ['SOFTWARE_HOME']= software_home
    sys.path.insert(0, software_home)

    print "importing zope"
    print "using INSTANCE_HOME =", instance_home
    print "      SOFTWARE_HOME =", software_home
    try:
        import Zope2
    except ImportError:  	# for Zope 2.7
        import Zope as Zope2
    Zope2.startup()

    print "beginning transaction"
    transaction.begin()
    connection = Zope2.DB.open()
    target = connection.root()['Application']

    sourcefn, targetpath = args

    # first walk to the targetfolder, creating folders if they do not exist yet
    for part in filter(None, targetpath.split('/')):
        target = ensure_folder(target, part, part)

    fs_to_zodb(sourcefn, target)

    transaction.commit()
    print "Committed, Finished"
