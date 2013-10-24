'''
Created on Aug 9, 2011
'''
import logging

from django.forms import Widget
from django.utils.safestring import mark_safe
from django.forms.widgets import flatatt
from django.contrib.contenttypes.models import ContentType


logger = logging.getLogger(__name__)

class GenericForeignKeyWidget(Widget):
    """
    Widget that can be used for generic foreign keys.  This widget will
    take the content types that are allowed as well as the querysets for each
    content type to produce a widget that is user-friendly.
    """
    
    WIDGET_FORMAT_STRING = \
        """
        <div id="%(name)s-wrapper-div">
        
            <script type="text/javascript">
            
                $(document).ready(function() {
                   
                   $('#%(name)s-content-type-select').change(function(){
                   
                       $('.%(name)s-select-class').css('display', 'none');
                       $('#%(name)s-select-object-' + $(this).attr('value')).css('display', 'inline')
                       
                   });
                   
                   selected_content_type = %(sel-content-type)s
                   selected_object = %(sel-object)s
                   
                   if ( selected_content_type != null )
                   {
                       $('#%(name)s-content-type-select').val(selected_content_type);
                       $('#%(name)s-select-object-%(sel-content-type)s').val(selected_object);
                       $('.%(name)s-select-class').css('display', 'none');
                       $('#%(name)s-select-object--%(sel-content-type)s').css('display', 'inline')
                   }
                   
                });
                
            </script>
            
            <div id="%(name)s-field-wrapper" class="generic-fk-wrapper" >
            
                <select id="%(name)s-content-type-select" name="%(name)s-content-type-select">
                    %(content-types)s
                </select>
                
                %(object-selects)s
            
            </div> <!-- %(name)s-field-wrapper div -->
            
        </div> <!-- %(name)s wrapper div -->
        """
    
    OBJECT_SELECT_STRING = \
        """
        <select id="%(name)s-select-object-%(contype)s" name="%(name)s-select-object-%(contype)s" 
                class="%(name)s-select-class"
                style="display: %(display)s"> 
            %(options)s
        </select>
        """
    
    OPTION_STRING = """<option value="%(value)s">%(name)s</option>"""
    
    def __init__(self, content_types=None, querysets={}, attrs=None):
        if not content_types:
            self.content_types = ContentType.objects.all()
        else:
            self.content_types = content_types
            
        self.querysets = querysets
        
        super(GenericForeignKeyWidget, self).__init__(attrs=attrs)
            
    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """
        
        object_type = data.get(name + '-content-type-select')
        object_id = data.get(name + '-select-object-' + str(object_type))
        return object_type, object_id
    
    def render(self, name, value, attrs=None):
        """Renders this widget into an html string

        args:
        name  (str)  -- name of the field
        value (str)  -- a json string of a two-tuple list automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """
        try:
            final_attrs = self.build_attrs(attrs)
            classes = flatatt(final_attrs)
            content_types = "\n".join([self.OPTION_STRING % {'value':contype.id, 
                                                             'name':contype.name} 
                                       for contype in self.content_types])
            
            object_selects = []
            for idx, con_type in enumerate(self.content_types):
                objects = self.querysets[con_type.id]
                options = "\n".join([self.OPTION_STRING % {'name': obj.name,
                                                           'value': obj.id}
                                     for obj in objects])
                
                display = "none" if idx > 0 else "inline"
                object_selects.append(self.OBJECT_SELECT_STRING % {'name': name,
                                                                   'contype':con_type.id,
                                                                   'options':options,
                                                                   'display':display})
            if value is None:
                self._selected_content_type = "null"
                self._selected_object = "null"
            else:
                if type(value) == tuple:
                    self._selected_content_type = value[0]
                    self._selected_object = value[1]
                else:
                    self._selected_content_type = value.split(',')[0]
                    self._selected_object = value.split(',')[1]
                
            ret = self.WIDGET_FORMAT_STRING % \
                {'name':name, 'value':value, 'classes':classes,
                 'content-types': content_types, 'object-selects':"\n".join(object_selects), 
                 'sel-content-type': self._selected_content_type, 'sel-object': self._selected_object,
                }
            
            return mark_safe(ret)
        except:
            logger.exception("An exception occurred while trying to render"
                             " a GenericForeignKeyWidget.")
            return ""
            
class RadioToggleWidget(Widget):
    """
    Widget that can wrap other widgets using a radio button.  This can be used to allow
    for a user to fill in one of x number of fields depending on which widget is selected
    """
    
    class Media:
        js = ('https://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js', )
        
    WIDGET_FORMAT_STRING = \
        """
        <div id="%(name)s-wrapper-div">
        
            <script type="text/javascript">
                $(document).ready(function() {
                   input = $( '#%(name)s-field-wrapper input' )
                   if (input.attr("value") == "")
                   {
                       input.attr("disabled", "disabled")
                       $( '#%(name)s-field-wrapper img' ).css('visibility', 'hidden');
                   }
                });
            </script>
            
            <input type="radio" name="%(radio-group)s" value="%(name)s-radio-select" 
                   %(checked)s %(classes)s onchange="
                   $( '.%(radio-group)s-select-div input' ).attr('disabled', 'disabled');
                   $( '.%(radio-group)s-select-div img' ).css('visibility', 'hidden');
                   $( '#%(name)s-field-wrapper input' ).removeAttr('disabled');
                   $( '#%(name)s-field-wrapper img' ).css('visibility', 'visible');
                    "/> 
                %(radio-text)s

            <div id="%(name)s-field-wrapper" class="%(radio-group)s-select-div" >
            
                %(wrapped-field)s
            
            </div> <!-- %(name)s-field-wrapper div -->
            
        </div> <!-- %(name)s wrapper div -->
        """
        
    def __init__(self, wrap_widget, radio_group, radio_text, attrs=None):
        self._wrap_widget = wrap_widget
        self._radio_text = radio_text
        self._radio_group = radio_group
        super(RadioToggleWidget, self).__init__(attrs=attrs)
            
    def render(self, name, value, attrs=None):
        """Renders this widget into an html string

        args:
        name  (str)  -- name of the field
        value (str)  -- a json string of a two-tuple list automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """
        final_attrs = self.build_attrs(attrs)
        final_attrs['id'] = "%s-radio-button" % name
        classes = flatatt(final_attrs)
        
        checked = "" if not value else 'checked="checked"'
        disabled = "" if value else 'disabled=disabled'
        wrapped_field = self._wrap_widget.render(name, value, attrs=attrs)
        
        ret = self.WIDGET_FORMAT_STRING % \
            {'name':name, 'value':value, 'classes':classes,
             'radio-text': self._radio_text, 'radio-group':self._radio_group, 
             'wrapped-field':wrapped_field, 'checked':checked, 'disabled':disabled}
        
        return mark_safe(ret)

        
class JQueryCalendar(Widget):
    """
    Base JQuery UI Calendar Widget
    """
    
    class Media:
        css = {'all': ('http://ajax.googleapis.com/ajax/libs/jqueryui/'
                       '1.8.15/themes/smoothness/jquery-ui.css',)}
        js = ('https://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js', 
              'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.15/jquery-ui.min.js',)
        
    JQUERY_OPTIONS_KEY = 'jquery-options'

    WIDGET_FORMAT_STRING = \
        """
        <div id="%(name)s-wrapper-div">

            <script type="text/javascript">
                $(function() {
                    $( "#%(name)s-wrapper-div #%(id)s" ).datepicker();
                    %(options)s
                });
            </script>
            
            <input type="text" name="%(name)s" value="%(value)s" %(classes)s></input>
            
        </div> <!-- %(name)s wrapper div -->
        """
        
    def render(self, name, value, attrs=None):
        """Renders this widget into an html string

        args:
        name  (str)  -- name of the field
        value (str)  -- a json string of a two-tuple list automatically passed in by django
        attrs (dict) -- automatically passed in by django (unused in this function)
        """

        final_attrs = self.build_attrs(attrs)
        jquery_opts = final_attrs.pop(self.JQUERY_OPTIONS_KEY, None)
        
        value = value.strftime('%m/%d/%Y') if value else ''
        # Build the date picker options from the attrs if JQUERY_OPTIONS_KEY exists.
        # JQUERY_OPTIONS_KEY key in attrs should have a value that is a dictionary of the
        # options that the datepicker supports
        date_options = self._build_datepicker_options(name, value, jquery_opts)
        classes = flatatt(final_attrs)
        ret = self.WIDGET_FORMAT_STRING % \
            {'name':name, 'options':date_options, 'classes':classes, 
             'id':final_attrs.get('id', name), 'value':value}
        
        return mark_safe(ret)

    def _build_datepicker_options(self, name, value, jquery_options):
        """
        Builds the options used for this JQuery UI control into a string that will be
        included in the return value for the render method
         
        RETURNS: 
            newline delimited strings for setting the jquery options passed in to the widget,
            empty string if no options are passed in.
         
        PARAMS:
            name(string):
                The name of the widget
            jquery_options(dict):
                Dictionary containing key = option name, value = option value to set for the control
        """
        
        if not jquery_options:
            return ''
        
        date_options = []
        if jquery_options:
            for k,v in jquery_options.iteritems():
                date_options.append('$( "#%(name)s-wrapper-div #%(name)s" ).datepicker( "option", "%(key)s", "%(value)s" );' % \
                                    {'name':name, 'key':k, 'value':v})
            
        return '\n'.join(date_options)
    
    def value_from_datadict(self, data, files, name):
        """
        Given a dictionary of data and this widget's name, returns the value
        of this widget. Returns None if it's not provided.
        """
        return data.get(name, None)
    
class JQueryInlineCalendar(JQueryCalendar):
    """
    Base JQuery Inline UI Calendar Widget
    """
    
    WIDGET_FORMAT_STRING = \
        """
        <div id="%(name)s-wrapper-div">

            <script type="text/javascript">
                $(function() {
                    $( "#%(name)s-wrapper-div #%(name)s-cal-div" ).datepicker({
                        onSelect: function(dateText, inst) {
                            $( "#%(id)s" ).attr("value", dateText)
                        },
                        defaultDate: '%(value)s',
                    });
                    %(options)s
                });
            </script>
        
            <input type="hidden" name="%(name)s"  value="%(value)s" %(classes)s></input>
            <div id="%(name)s-cal-div"></div>
        </div> <!-- %(name)s wrapper div -->
        """
        
