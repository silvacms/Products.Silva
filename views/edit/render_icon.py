## Script (Python) "render_icon"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=meta_type
##title=
##
dict = { 'Silva Root' : 'silva.gif',
         'Silva Publication' : 'silvapublication.gif',
         'Silva Folder' : 'silvafolder.gif',
         'Silva Document' : 'silvadoc.gif',
         'Silva Ghost' : 'silvaghost.gif',
         'Silva Image' : 'silvaimage.gif',
         'Silva File' : 'silvafile.png',
         'Silva SQL Data Source' : 'silvasqldatasource.png',
         'Silva DemoObject' : 'silvageneric.gif',
         'Silva News NewsSource' : 'silvanewssource.png',
         'Silva News NewsFilter' : 'silvanewsfilter.png',
         'Silva News AgendaFilter' : 'silvaagendafilter.png',
         'Silva News NewsViewer' : 'silvanewsviewer.png',
         'Silva News AgendaViewer' : 'silvaagendaviewer.png',
         'Silva News RSSViewer' : 'silvarssviewer.png',
         'Silva News NewsItem' : 'silvanewsitem.gif',
         'Silva News AgendaItem' : 'silvaagendaitem.png',
         'Silva News Article' : 'silvanewsitem.png',
         'Silva Course' : 'silvacourse.gif',
         'Silva Contact Info' : 'silvacontactinfo.gif',
         }

icon_name = dict.get(meta_type, 'silvageneric.gif')
return '<img src="%s/globals/%s" width="16" height="16" border="0" alt="%s" />' % (context.silva_root(),icon_name, meta_type)
