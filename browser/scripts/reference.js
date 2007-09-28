this.reference = new function() {
    /* handles setting references for the object_lookup window */

    var winwidth = 760;
    var winheight = 500;

    var reference_lib = this;

    this.current_handler = undefined;

        this.getReference = function(handler, startpath, filter, show_add, selected_path) {
        /* open the reference lookup window 
        
            when the user has selected an item, handler will be called
            with 4 arguments, path (a relative or absolute HTTP path to
            the item), id (the id of the item) and title (the title of
            the item)
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
                              'selected_path=' + selected_path, winname,
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
}();
