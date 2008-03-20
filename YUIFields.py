
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.DummyField import fields
from Products.Formulator.StandardFields import StringField
from Products.Formulator.Validator import ValidatorBase
from Products.Formulator.Widget import (render_element,
                                        TextWidget,
                                        MultiCheckBoxWidget)
from Products.Silva.adapters.path import getPathAdapter


# XXX this seems wrong, I need to get a hold of the silva root..
# NOTE: download yui2.5.0 and put the yui/build directory in ./browser/scripts
YUI_BUILD_URL = '++resource++silva_scripts/yui/build/'

class AutoCompleteWidget(TextWidget):
    """YUI Autocomplete Widget
    """

    property_names = TextWidget.property_names + ['type_ahead',
                                                  'always_show_container',
                                                  'max_results',
                                                  'js_array',
                                                  'source_uri',
                                                  'query_param',
                                                  'extra_params',
                                                  'schema']

    type_ahead = fields.CheckBoxField('type_ahead',
                                      title="Type ahead",
                                      description=(
        "causes input to be automatically completed with the first query"
        "result in the container list."),
                                      default=False)
    
    always_show_container = fields.CheckBoxField('always_show_container',
                                                 title="Always show container",
                                                 description=(
        "display the suggestion container, even when the user is not "
        "interacting directly with it"),
                                                 default=False)

    max_results = fields.IntegerField('max_results',
                                title='Maximum Results Displayed',
                                description=(
        "Maximum Results Displayed"),
                                default=20,
                                required=1)

    js_array = fields.LinesField('js_array',
                                 title='inline javascript array',
                                 description=(
        "populate the autocomplete widget with values from an"
        "inline javascript array. Each line will become a value"
        "Note that this parameter should be a valid Javascript"
        "array, not a python array"),
                                 width=20, height=3,
                                 default=[],
                                 required=0)
        
    source_uri = fields.LinkField('source_uri',
                                  title='json source url',
                                  width=20,
                                  description=(
        "Url to load json data from"),
                                  required=0)
                                 
    query_param = fields.StringField('query_param',
                                     title='Query parameter',
                                     description=(
        "parameter name used in request for query"),
                                     width=20,
                                     default='query')

    extra_params = fields.StringField('extra_params',
                                     title='Extra parameters',
                                     required=0,
                                     description=(
        "Additional parameters that will be sent to the server"),
                                     width=20)
    
    schema = fields.StringField('schema',
                                title="JSON Schema",
                                description=(
        "A JS array, where the first item points to the list of result"
        "objects returned from the server, the additional items will be"
        "displayed as column data. F.E if the resulting json is:"
        "{resultSet{total:100, results:[{title:'A result'}, {title:'Another'}]}}"
        "then the schama would be ['resultSet.results', 'title']"),
                                default = '["resultSet.results", "title"]',
                                width=20)
                                

    def render(self, field, key, value, REQUEST,
               autocomplete_id=None,
               initial_load=True):
        """ Render AutoComplete input field.
        """

        if autocomplete_id is None:
            autocomplete_id = key

        input_tag = TextWidget.render(self,
                                      field,
                                      key,
                                      value,                                  
                                      REQUEST)

        loader = ''
        if initial_load:
            # add the yui javascript and autocomplete functions
            loader = self.render_yui_loader(field, autocomplete_id, value, REQUEST)
        
        

        html = render_element("div",
                              id = key,
                              extra='class="yui-skin-sam"',
                              style="width:%sem;" % field.get_value('display_width'),
                              contents='')
        
        script =  self.render_autocompleter(field,
                                            autocomplete_id,
                                            value,
                                            REQUEST)
        
        return '%s\n%s\n%s' % (loader, html, script)
        

    def is_multi_widget(self):
        return False
    
    def render_autocompleter(self, field, key, value, REQUEST):
        result = []
        
        if type(value) == list:
            values = value
        elif not value:
            values = ['']
        else:
            values = [value]
        
        JS ="""
new YAHOO.util.YUILoader({
require: ['autocomplete', 'connection', 'json', 'element'],
base: '%s',
onSuccess: function(){formulator_autocomplete('%s', %s, %s, %s)}
}).insert()
""" % (YUI_BUILD_URL,
       key,
       values,
       str(self.is_multi_widget()).lower(),
       field.get_value('display_width'))

        result.append(render_element("script",
                                     type="text/javascript",
                                     contents=JS))
        return '\n'.join(result)
    
    def render_yui_loader(self, field, key, value, REQUEST):
        
        if field.get_value('source_uri'):
            uri = field.get_value('source_uri')
            ds = 'DS_XHR("%s", %s);' % (uri, field.get_value('schema'))
            ds += '\n  ds.connMgr = YAHOO.util.Connect;'
            ds += '\n  ds.responseType = YAHOO.widget.DS_XHR.TYPE_JSON;'
            ds += '\n  ds.scriptQueryParam = "%s";' % field.get_value(
                'query_param')
            if field.get_value('extra_params'):
                ds += '\n  ds.scriptQueryAppend="%s";' % field.get_value(
                    'extra_params')
            
        else:
            ds = 'DS_JSArray(%s);' % field.get_value('js_array')
        
        result = [render_element('script',
                                 type='text/javascript',
                                 src=YUI_BUILD_URL + 'yuiloader/yuiloader-beta.js',
                                 contents='')]
        result.append("""
<script type="text/javascript">
function formulator_remove_autocomplete(event){
  var div  = event.target.parentNode;
  var pdiv =  event.target.parentNode.parentNode;
  if (div.nextSibling && div.nextSibling.tagName == 'BR'){
    pdiv.removeChild(div.nextSibling);
  }
  pdiv.removeChild(div);

}

function formulator_autocomplete(id, values, multi, size){

  if (values == undefined) values = [''];
  if (size == undefined) size = 20;

  for (i=0;i<values.length;i++){
    var value = values[i];
    var pdiv = document.getElementById(id);
    var div = document.createElement('div');
    div.className = 'yui-skin-sam';
    var indiv = document.createElement('div');
    var input = document.createElement('input');
    input.type = 'text';
    input.name = id;
    input.value = value;
    container = document.createElement('div');

    pdiv.appendChild(div);
    div.appendChild(indiv);
    indiv.appendChild(input);
    indiv.appendChild(container);

    ds = new YAHOO.widget.%(ds)s
    var ac = new YAHOO.widget.AutoComplete(input, container, ds);
    ac.typeAhead = %(type_ahead)s;
    ac.alwaysShowContainer = %(always_show)s;
    ac.maxResultsDisplayed = %(max_results)s;
    ac.animVert = false;
    ac.animHoriz = false;
    ac.animSpeed = 2;
    ac.useShadow = true;

    if (multi){
       var minbut = document.createElement('input')
       minbut.type = 'button';
       minbut.value = '-';
       minbut.className = 'autocomplete-remove';
       var elbut = new YAHOO.util.Element(minbut)
       elbut.on('click', formulator_remove_autocomplete);
       elbut.setStyle('float', 'right');
       new YAHOO.util.Element(indiv).setStyle('width', (size-2)+'em');
       div.appendChild(minbut);
    }
    
    if ( i < (values.length-1)){
       var br = document.createElement('br');
       new YAHOO.util.Element(br).setStyle('clear', 'both');
       pdiv.appendChild(br);
    }

  }
  if (multi){
    var br = document.createElement('br');
    new YAHOO.util.Element(br).setStyle('clear', 'both');
    pdiv.appendChild(br);
    var addbut = document.createElement('input')
    addbut.type = 'button';
    addbut.value = 'Add';
    new YAHOO.util.Element(addbut).on('click', formulator_add_autocomplete, size);
    pdiv.appendChild(addbut);
  }
 
}


function formulator_add_autocomplete(event, size){
  var but = event.target;
  var pdiv = but.parentNode;
  var id = pdiv.id;
  pdiv.removeChild(but);
  formulator_autocomplete(id, [''], true, size);

}

</script>""" % {'url': YUI_BUILD_URL,
                'type_ahead': str(field.get_value('type_ahead')).lower(),
                'always_show': str(field.get_value('always_show_container')
                                   ).lower(),
                'max_results': field.get_value('max_results'),
                'ds':ds
                })
        return '\n'.join(result)
    
class MutltiAutoCompleteWidget(AutoCompleteWidget):
    
    property_names = AutoCompleteWidget.property_names
    
    default = fields.LinesField('default',
                                title='Default',
                                description=(
        "The initial selections of the widget. This is a list of "
        "zero or more values. If you override this property from Python "
        "your code should return a Python list."),
                                width=20, height=3,
                                default=[],
                                required=0)

    def is_multi_widget(self):
        return True
    
class AutoCompleteValidator(ValidatorBase):
    
    def validate(self, field, key, REQUEST):
        # XXX no real validation at the moment
        return ValidatorBase.validate(self, field, key, REQUEST)

        
class AutoCompleteField(StringField):

    meta_type = 'AutocompleteField'
    widget = AutoCompleteWidget()
    validator = AutoCompleteValidator()

class MutltiAutoCompleteField(AutoCompleteField):
    
    meta_type = 'MutltiAutoCompleteField'
    widget =MutltiAutoCompleteWidget()
    validator = AutoCompleteValidator()

FieldRegistry.registerField(AutoCompleteField, '../Silva/www/YUIField.gif')
FieldRegistry.registerField(MutltiAutoCompleteField,
                            '../Silva/www/YUIField.gif')
