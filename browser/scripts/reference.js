this.reference = new function() {
    /* handles setting references for the object_lookup window */

    var winwidth = 760;
    var winheight = 500;

    var reference_lib = this;

    this.current_handler = undefined;

        this.getReference = function(handler, startpath, filter, show_add, 
                                        selected_path, possible_container) {
        /* open the reference lookup window 
        
            when the user has selected an item, handler will be called
            with 4 arguments, path (a relative or absolute HTTP path to
            the item), id (the id of the item) and title (the title of
            the item),
            possible_container is a string that may or may not be a
            path to silva content.  If the lookupwindow can resolve the
            path, it is displayed instead.
        */
        reference_lib.setHandler(handler);
        var level = null;
        if (opener && opener.object_lookup_level !== undefined) {
            level = opener.object_lookup_level + 1;
        } else {
            level = 1;
        };
        var leftpos = (screen.width - winwidth) / 2 + ((level - 1) * 10);
        var toppos = (screen.height - winheight) / 2 + ((level - 1) * 10);
        var winname = 'object_lookup_window_' + level;
        var win = window.open(startpath + 
                              '/@@object_lookup?filter=' + filter + '&' +
                              'show_add=' + (show_add ? '1' : '0') + '&' +
                              'selected_path=' + selected_path + '&' + 
                              'possible_container=' + 
                              encodeURI(possible_container), winname,
                              'toolbar=yes,status=yes,scrollbars=yes,' +
                              'resizable=yes,width=' + winwidth +
                              ',height=' + winheight +
                              ',left=' + leftpos + ',top=' + toppos);
        win.focus();
        window.object_lookup_level = level;
    };
    
    this.setReference = function(form, radioname) {
        /* called from the 'place' button */
        var radios = form.ownerDocument.getElementsByName(radioname);
        var radio = undefined;
        for (var i=0; i < radios.length; i++) {
            if (radios[i].checked) {
                radio = radios[i];
                break;
            };
        };
        if (radio === undefined) {
            // XXX should alert something here I think but we don't have JS
            // i18n'ned yet...
            return;
        };
        // the radio must have some special attributes defined
        var path = radio.value;
        var id = radio.getAttribute('lookup:id');
        var title = radio.getAttribute('lookup:title');
        opener.reference.getHandler()(path, id, title);
        window.close();
    };

    this.setReferenceFromElement = function(el) {
        /* call this when the data should be retrieved from non-form els */
        var path = el.getAttribute('lookup:path');
        var id = el.getAttribute('lookup:id');
        var title = el.getAttribute('lookup:title');
        opener.reference.getHandler()(path, id, title);
        window.close();
    };

    this.setHandler = function(handler) {
        /* set the handler for the reference system

            the handler is called when the user has selected an item, and will
            be called with 3 arguments, the path, id and title of the item
            selected (where path is a relative or absolute URL path to the
            object)

            note that only a single handler can be set per window at any given
            time

            internal method, use reference.getReference() to trigger this
        */
        reference_lib.current_handler = handler;
    };

    this.getHandler = function() {
        /* return any set handler 
        
            internal method
        */
        return reference_lib.current_handler;
    };
    this.editReference = function(fieldname,url) {  
    /* NOTE: this functionality currently only works within
       kupu, since it relies on kupu's AJAX abstraction
       (that's actually in sarissa.js) */
        var field = document.getElementById(fieldname);
        if (!field) {
          field = document.getElementsByName(fieldname)[0];
        }
        var value = field.value;
        var ref = value.replace(/\s/g,'');
        if (ref == '') {
            return false;
        }
        var request = new XMLHttpRequest();
        var resolveurl = url + '/resolve_and_redirect_editor?loc='+ref;
        request.open('GET', resolveurl+'&checkonly=y', true);
        var callback = new ContextFixer(function() {
                if (request.readyState == 4) {
                    if (request.status.toString() == '200') {
                        /* if not IE, it is possible to get the *real*
                           window width/height.  use 90% of that for the
                           dimensions, or fall back to 800x600 */
                        w = window.outerWidth?window.outerWidth * 0.9 : 800;
                        h = window.outerHeight?window.outerHeight * 0.9 : 600;
                        openPopup(resolveurl,w,h);
                        return;
                    } else {
                        /* all other cases raise an alert */
                        alert('Reference "' + value + '" is not a valid relative silva reference.  The quick edit interface only works for valid relative silva references');
                    };
                };
            }, this);
        request.onreadystatechange = callback.execute;
        request.send('');
        return false;
    }
}();
