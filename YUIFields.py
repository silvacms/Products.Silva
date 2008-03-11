
from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.DummyField import fields
from Products.Formulator.StandardFields import StringField
from Products.Formulator.Validator import StringValidator
from Products.Formulator.Widget import render_element,TextWidget
from Products.Silva.adapters.path import getPathAdapter


# XXX this seems wrong, I need to get a hold of the silva root..
# NOTE: download yui2.5.0 and put the yui/build directory in ./browser/scripts
YUI_BUILD_URL = '++resource++silva_scripts/yui/build/'

class AutoCompleteWidget(TextWidget):
    """YUI Autocomplete Widget
    """

    property_names = TextWidget.property_names +\
                     ['type_ahead',
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
                                

    def render(self, field, key, value, REQUEST):
        """ Render AutoComplete input field.
        """
        
        if field.get_value('source_uri'):
            uri = field.get_value('source_uri')
            ds = 'DS_XHR("%s", %s);' % (uri, field.get_value('schema'))
            ds += '\nds.connMgr = YAHOO.util.Connect;'
            ds += '\nds.responseType = YAHOO.widget.DS_XHR.TYPE_JSON;'
            ds += '\nds.scriptQueryParam = "%s";' % field.get_value(
                'query_param')
            if field.get_value('extra_params'):
                ds += '\nds.scriptQueryAppend="%s";' % field.get_value(
                    'extra_params')
            
        else:
            ds = 'DS_JSArray(%s);' % field.get_value('js_array')
        input_tag = TextWidget.render(self,
                                      field,
                                      key,
                                      value,
                                      REQUEST)

        result = [render_element('script',
                                 type='text/javascript',
                                 src=YUI_BUILD_URL + 'yuiloader/yuiloader-beta.js',
                                 contents='')]
        result.append(input_tag.replace('name=', 'id="%s_input" name=' % key))
        result.append(render_element("div",
                                     id="%s_container" % key, contents=''))
        result.append("""
<script type="text/javascript">
new YAHOO.util.YUILoader({
require: ['autocomplete', 'connection', 'json'],
base: '%(url)s',
onSuccess: function(){
var ds = new YAHOO.widget.%(ds)s
var ac = new YAHOO.widget.AutoComplete("%(id)s_input","%(id)s_container", ds);
ac.typeAhead = %(type_ahead)s;
ac.alwaysShowContainer = %(always_show)s;
ac.maxResultsDisplayed = %(max_results)s;
ac.useShadow = true;
}}).insert()
</script>""" % {'url': YUI_BUILD_URL,
                'id': key,
                'type_ahead': str(field.get_value('type_ahead')).lower(),
                'always_show': str(field.get_value('always_show_container')
                                   ).lower(),
                'max_results': field.get_value('max_results'),
                'ds':ds
                })
                          
        return render_element("div",
                              extra='class="yui-skin-sam"',
                              style="width:%sem;" % field.get_value('display_width'),
                              contents = '<div>%s</div>' % '\n'.join(result))


class AutoCompleteValidator(StringValidator):
    
    def validate(self, field, key, REQUEST):
        # XXX no real validation at the moment
        return StringValidator.validate(self, field, key, REQUEST)
        
class AutoCompleteField(StringField):

    meta_type = 'AutoCompleteField'
    widget = AutoCompleteWidget()
    validator = AutoCompleteValidator()


FieldRegistry.registerField(AutoCompleteField, '../Silva/www/YUIField.gif')
