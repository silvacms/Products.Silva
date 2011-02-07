/*****************************************************************************
    *
    * Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
    *
    * This software is distributed under the terms of the Kupu
    * License. See LICENSE.txt for license text. For a list of Kupu
    * Contributors see CREDITS.txt.
    *
    **************************************************************************/

// $Id: kupusilvatools.js 25442 2006-04-06 10:29:19Z guido $

function ExternalSourceLoader(div) {
    if (div == null) {
        return;
    };
    this.div = div;
    // Needed for z-index adjustment later
    this.mynumber = ExternalSourceLoader.number--;
    this.source_id = this.div.getAttribute("source_id");
    this.extsourcetool = window.kupueditor.getTool('extsourcetool');
    this.docref = this.extsourcetool.docref;
    this.params = this.extsourcetool._gatherFormDataFromElement(this.div);
    /* the parameter keys all have the data type encoded in them, e.g.
       name__type__string or decision__type__boolean.  Strip off __type__\w*,
       since the ExternalSource's to_html is expecting parameters
       without the data type (it does casting based off of the field's type */
    this.params = this.params.replace(/__type__\w*=/g, '=');
    this.params += "&docref="+this.docref + "&source_id=" + this.source_id;
    // Turn off editing for the previews, because IE won't accept
    // display:none otherwise
    this.div.contentEditable = false;

    this.docurl = document.location.href.replace(/\/edit.*?$/, '/');
};

ExternalSourceLoader.prototype = new ExternalSourceLoader;

/* this is a class variable, which is used by the ESLoader to
   establish z-indexes so that the higher of two adjacent ES will
   have the mousehover display *above* the lower ES */
ExternalSourceLoader.number = 200;

ExternalSourceLoader.prototype.initialize = function() {
    var request = new XMLHttpRequest();
    var url = this.docurl + "@@render_extsource";

    request.open("POST", url, true);
    var callback = new ContextFixer(this.preload_callback, this, request);
    request.onreadystatechange = callback.execute;
    request.setRequestHeader(
        'Content-Type', 'application/x-www-form-urlencoded');
    request.send(this.params);

    /* using a :hover sudo-selector would be nice, but it seems that IE7 can't
       doesn't recognize this selector within designMode */
    addEventHandler(this.div, "mouseover", this.onMouseOverHandler, this);
    addEventHandler(this.div, "mouseout", this.onMouseOutHandler, this);
};

ExternalSourceLoader.prototype.createPreview =
        function(request, previewcreator) {
    /* this function prepares the preview and mousehover.  However,
       the "previewcreator" is a caller-supplied function that actually
       places content in the preview */
    var parentDiv = this.div;

    parentDiv.setAttribute("title","External Source; content is locked");

    /* populate the preview */
    var previewDiv = parentDiv.ownerDocument.createElement("div");
    this.previewDiv = previewDiv;
    previewDiv.className = 'externalsourcepreview';
    /* call supplied function to actually create the preview */
    previewcreator(request,previewDiv);

    /* change the href of anchors so they are not clickable */
    var anchors = previewDiv.getElementsByTagName('a');
    for (var i=0; i<anchors.length; i++) {
        anchors[i].href='javascript:void';
    };
    /* an attempt at preventing images from being selected (and moved around)
        but this approach (moving the selection / focus elsewhere)
        does not work */
    /*var imgs = previewDiv.getElementsByTagName('img');
    for (var i=0; i<imgs.length; i++) {
        addEventHandler(imgs[i], "mousedrag",
            function(event) {
                var e = event || window.event;
                var target = event.srceElement || event.target;
                var selection = window.kupueditor.getSelection();
                selection.selectNodeContents(target.parentNode);
                selection.collapse(true);
            }, this.blurOnFocusHandler, this);
    }*/

    parentDiv.appendChild(previewDiv);
    /* set a lower z-index so IE won't push the hover div under another
       ES preview lower in the document (each DIV has a lower number.
       Cannot be negative. */
    parentDiv.style.zIndex = this.mynumber;
};

ExternalSourceLoader.prototype.preload_callback = function(request) {
    if (request.readyState == 4) {
        var parentDiv = this.div;
        var previewDiv = null;
        /* find the preview div, if present */
        for (var i = 0; i < parentDiv.childNodes.length; i++) {
            var node = parentDiv.childNodes[i];
            if (node.tagName == 'DIV') {
                if (node.className == "externalsourcepreview") {
                    previewDiv = node;
                    break;
                };
            };
        };
        if (request.status == 200 || //HTTP 200: OK; HTTP 204: No content
            request.status == 204 ||
            /* when status is actually 204 no content, IE 7 appears to
               make response.status==1223 (what??) */
            request.status == 1223) {
            if (previewDiv) {
                /* if the externalsourcpreview DIV already exists, replace
                   the content
                   XXX When does this happen?  Clicking `update` in the ES
                   removes and recreates the content of the ES div (so
                   it doesn't happen then)
                */
                previewDiv.getElementsByTagName("div")[2].innerHTML =
                    previewDiv.getElementsByTagName("div")[0].innerHTML;
                if (request.responseText != "") {
                    previewDiv.getElementsByTagName("div")[3].innerHTML =
                        request.responseText;
                } else {
                    var h4 = previewDiv.ownerDocument.createElement("h4");
                    var text = previewDiv.ownerDocument.createTextNode(
                        " [preview is not available]");
                    h4.appendChild(text);
                    previewDiv.appendChild(h4);
                };
            } else {
                var pc = function(request,pd) {
                    if (request.responseText != "") {
                        pd.innerHTML = request.responseText;
                    } else {
                        var h4 = pd.ownerDocument.createElement("h4");
                        var text = pd.ownerDocument.createTextNode(
                            " [preview is not available]");
                        var hiddenh4 = parentDiv.getElementsByTagName("h4")[0];
                        for (var i=0;i<hiddenh4.childNodes.length; i++) {
                            h4.appendChild(
                                hiddenh4.childNodes[i].cloneNode(true));
                        };
                        h4.appendChild(text);
                        pd.appendChild(h4);
                    };
                };
                this.createPreview(request, pc);
            };
        } else {
            var pc = function(request, pd) {
                pd.innerHTML =
                    "<h4>An HTTP " + request.status +
                    " error was encountered when attempting to preview" +
                    " this external source</h4>";
            };
            /* populate the preview */
            this.createPreview(request, pc);
        };
        /* add non-breaking space if the content height is 0. The height
           could be 0 if the preview is a single floated div. This ensures
           that the ES will always be selectable. */
        /* unfortunately, this is hard-coded to the height of the top
           and bottom padding */
        if (this.div.offsetHeight == 4) {
            this.div.appendChild(
                this.div.ownerDocument.createTextNode('\xa0'));
        };
        this.div.style.overflow = 'auto';
        /* ensure height will display the entire 'locked' graphic */
        if (this.div.offsetHeight < 26) {
            this.div.style.height = '33px';
        };
    };
};

ExternalSourceLoader.prototype.onMouseOverHandler = function() {
    /* using a :hover sudo-selector would be nice, but it seems that IE7 can't
       doesn't recognize this selector within designMode */
    var current_source = null;
    if (this.extsourcetool._currentExternalSource) {
        current_source = this.extsourcetool._currentExternalSource.get(0);
    };
    var source = this.div;
    if (!(current_source === source)) {
        $(source).addClass('active');
    };
};

ExternalSourceLoader.prototype.onMouseOutHandler = function(event) {
    /* using a :hover sudo-selector would be nice, but it seems that IE7 can't
       doesn't recognize this selector within designMode */
    var current_source = null;
    if (this.extsourcetool._currentExternalSource) {
        current_source = this.extsourcetool._currentExternalSource.get(0);
    };
    var source = this.div;
    if (!(current_source == source)) {
        $(source).removeClass('active');
    };
};

/* generic toolbox object helper */
var SilvaToolBox = function(toolboxid, activeclass, plainclass) {
    this.toolbox = getFromSelector(toolboxid);
    this.options = $('#'+ toolboxid + '-options');
    this.options.hide();
    this.plainclass = plainclass;
    this.activeclass = activeclass;
};

SilvaToolBox.prototype.open = function () {
    /* open the tool box */
    if (this.toolbox) {
        this.toolbox.className = this.activeclass;
        if (this.toolbox.open_handler) {
            this.toolbox.open_handler();
        };
        this.options.show();
    };
};

SilvaToolBox.prototype.set_title = function(new_title) {
    $(this.toolbox).children('h1').text(new_title);
};

SilvaToolBox.prototype.close = function () {
    /* close the tool box*/
    if (this.toolbox) {
        this.toolbox.className = this.plainclass;
    };
    this.options.hide();
};

SilvaToolBox.prototype.enable = function () {
    $(this.toolbox).slideDown('fast');
};


/* helper to select link targets */
var SilvaLinkTargetSelector = function(targetid) {
    var self = this;
    this.select = $('#'+ targetid + '-select');
    this.input = $('#'+ targetid + '-custom');
    /* initialize and bind event */
    this.select.change(function () {
        if (self.select.val() != 'input') {
            self.input.hide();
        } else {
            self.input.show();
        };
    });
    this.input.hide();
};

SilvaLinkTargetSelector.prototype.retrieve = function() {
    var value = this.select.val();
    if (value == 'input') {
        return this.input.val();
    };
    return value;
};

SilvaLinkTargetSelector.prototype.set = function(target) {
    if (!target) {
        this.select.val('_self');
        this.input.val('');
        this.input.hide();
    } else {
        if ($.inArray(target, ['_self', '_blank', '_parent', '_top']) > -1) {
            this.select.val(target);
            this.input.val('');
            this.input.hide();
        } else {
            this.select.val('input');
            this.input.val(target);
            this.input.show();
        };
    };
};

SilvaLinkTargetSelector.prototype.clear = function () {
    this.select.val('_self');
    this.input.val('');
    this.input.hide();
};

function SilvaLinkTool() {
    /* redefine the contextmenu elements */
};

SilvaLinkTool.prototype = new LinkTool();

SilvaLinkTool.prototype.updateLink = function (
        linkel, url, type, name, target, title) {
    if (type && type == 'anchor') {
        linkel.removeAttribute('href');
        linkel.setAttribute('name', name);
    } else {
        if (type && type == 'internal') {
            /* Internal don't have an url. However it was set to prevent a new link to lose its text */
            url = '';
        };
        if (type && type == 'reference') {
            /* We have a reference. Href is set to something to
             * prevent SilvaIndexTool to get contol over the link */
            linkel.href = 'reference';
            linkel.setAttribute('_silva_target', url);
            var reference = linkel.getAttribute('_silva_reference');
            if (!reference) {
                linkel.setAttribute('_silva_reference', 'new');
            }
            linkel.removeAttribute('_silva_href');
            if (url != '0') {
                linkel.removeAttribute('class');
            } else {
                linkel.setAttribute('class', 'broken-link');
            };
        } else {
            /* We have an old style link*/
            linkel.href = url;
            linkel.setAttribute('_silva_href', url);
            linkel.removeAttribute('_silva_reference');
            linkel.removeAttribute('_silva_target');
            linkel.removeAttribute('class');
        };
        if (linkel.innerHTML == "") {
            var document = this.editor.getInnerDocument();
            linkel.appendChild(document.createTextNode(title || url || name));
        };
        if (title) {
            linkel.title = title;
        } else {
            linkel.removeAttribute('title');
        };
        if (name) {
            /* In case of reference or external link, name is a extra
             * anchor */
            linkel.setAttribute('_silva_anchor', name);
        }
        else {
            linkel.removeAttribute('_silva_anchor');
        }
        if (target && target != '') {
            linkel.setAttribute('target', target);
        } else {
            linkel.removeAttribute('target');
        };
        linkel.style.color = this.linkcolor;
    };
    this.editor.content_changed = true;
};

function SilvaLinkToolBox(
        inputid, optionid, imageid, addbuttonid, updatebuttonid, delbuttonid,
        toolboxid, plainclass, activeclass) {
    /* create and edit links */

    this.content = new ReferencedRemoteObject(inputid);
    this.toolbox = new SilvaToolBox(toolboxid, activeclass, plainclass);
    this.target = new SilvaLinkTargetSelector(optionid + '-target');
    this.title = $('#' + optionid + '-title');
    this.external_href = $('#' + inputid + '-href');
    this.anchor = $('#' + inputid + '-anchor');
    /* the next three options are for image link support */
    this.image = null;
    this.image_options = $('#' + imageid + '-options');
    this.image_hires = $('#' + imageid + '-hires');
    /* buttons */
    this.addbutton = getFromSelector(addbuttonid);
    this.updatebutton = getFromSelector(updatebuttonid);
    this.delbutton = getFromSelector(delbuttonid);
};

SilvaLinkToolBox.prototype = new LinkToolBox();

SilvaLinkToolBox.prototype.initialize = function(tool, editor) {
    var self = this;
    this.tool = tool;
    this.editor = editor;
    this.image_hires.change(function() {
        self.content.toggle();
    });
    this.content.change(function(event, info) {
        if (info['path']) {
            self.external_href.val(info['path']);
            self.external_href.attr('readonly', 'readonly');
            self.external_href.attr('class', 'store readonly');
        } else {
            self.external_href.val('');
            self.external_href.removeAttr('readonly');
            self.external_href.attr('class', 'store');
        };
    });

    addEventHandler(this.addbutton, 'click', this.createLinkHandler, this);
    addEventHandler(this.updatebutton, 'click', this.createLinkHandler, this);
    addEventHandler(this.delbutton, 'click', this.tool.deleteLink, this);
    this.editor.logMessage('Link tool initialized');
};

SilvaLinkToolBox.prototype.createLinkHandler = function(event) {
    if (this.editor.suspended) {
        return;
    };

    var content = this.content;
    var external_href = this.external_href.val();
    var anchor = this.anchor.val();
    var reference = null;
    var target = this.target.retrieve();
    var title = null;

    if (this.image) {
        // We are in an image
        var hires = this.image_hires.attr('checked');
        if (hires) {
            // Reuse content selector from the image tool box if hires selected
            content = this.editor.getTool('imagetool').content;
        };
    }
    reference = content.reference();

    if (!reference && !external_href && !anchor) {
        alert('No content selected as link target, or no anchor!');
        return;
    };
    if (reference && reference != '0') {
        title = this.title.val() || content.title();
        this.tool.createLink(reference, 'reference', anchor, target, title);
    }
    else if (external_href) {
        title = this.title.val();
        this.tool.createLink(external_href, 'external', anchor, target, title);
    }
    else {
        /* Anchor only. Set URL to #anchor otherwise an empty link will be generated. */
        title = this.title.val();
        this.tool.createLink('#' + anchor, 'internal', anchor, target, title);
    };
    this.editor.content_changed = true;
    this.editor.updateState();
};

SilvaLinkToolBox.prototype.resetTool = function() {
    this.addbutton.style.display = 'inline';
    this.updatebutton.style.display = 'none';
    this.delbutton.style.display = 'none';
    this.title.val('');
    this.anchor.val('');
    this.external_href.val('');
    this.toolbox.close();
    this.content.clear();
    this.target.clear();
};

SilvaLinkToolBox.prototype.updateState = function(selNode, event) {
    /* reset image link settings */
    this.content.show();
    this.image = null;
    this.image_options.hide();
    this.image_hires.val(false);

    var extsourcetool = this.editor.getTool('extsourcetool');
    if (extsourcetool != undefined) {
        if (extsourcetool.getNearestExternalSource(selNode, event)) {
            this.resetTool();
            return;
        };
    };
    var self = this;
    var currnode = selNode;

    /* look for a link (or an image) */
    while (currnode) {
        if (currnode.nodeName == 'IMG') {
            this.image = currnode;
            this.image_options.show();
            this.image_hires.attr('checked', '');
        };
        if (currnode.nodeName == 'A' && !currnode.getAttribute('name')) {

            var enableToolBox = (function(self) {
                var target = currnode.getAttribute('target');

                self.toolbox.open();
                self.target.set(target);
                self.addbutton.style.display = 'none';
                self.updatebutton.style.display = 'inline';
                self.delbutton.style.display = 'inline';
                });

            var title = currnode.getAttribute('title') || '';
            this.title.val(title);
            var anchor = currnode.getAttribute('_silva_anchor') || '';
            this.anchor.val(anchor);
            var reference = currnode.getAttribute('_silva_target');
            if (reference) {
                enableToolBox(self);
                if (this.image) {
                    var image_tool = this.editor.getTool('imagetool');
                    if (image_tool.content.reference() == reference) {
                        this.image_hires.attr('checked', 'checked');
                        this.content.hide();
                    };
                };
                this.content.fetch(reference);
                this.external_href.val('');
                return;
            };
            var href = currnode.getAttribute('href') ||
                currnode.getAttribute('_silva_href') ||
                '';
            enableToolBox(self);
            this.content.clear();
            this.external_href.val(href);
            return;
        };
        currnode = currnode.parentNode;
    };
    /* We have no link. Reset the toolbox to add state */
    this.resetTool();
};

function SilvaImageTool(
        inputid, alignid, addbuttonid, updatebuttonid, resizebuttonid,
        toolboxid, plainclass, activeclass) {

    this.content = new ReferencedRemoteObject(inputid);
    this.toolbox = new SilvaToolBox(toolboxid, activeclass, plainclass);
    this.alignment = $('#' + alignid);
    this.resizePollingInterval = null;
    this.image = null;

    this.add_button = $('#' + addbuttonid);
    this.update_button = $('#' + updatebuttonid);
    this.resize_button = $('#' + resizebuttonid);
};

SilvaImageTool.prototype = new ImageTool();

SilvaImageTool.prototype.initialize = function(editor) {
    this.editor = editor;

    var bindButtonEvent = function(button, handler, object) {
        addEventHandler(button.get(0), 'click', handler, object);
    };

    bindButtonEvent(this.add_button, this.createImageHandler, this);
    bindButtonEvent(this.update_button, this.createImageHandler, this);
    bindButtonEvent(this.resize_button, this.confirmResizeHandler, this);
    addEventHandler(this.editor.getInnerDocument(), 'keydown', this.handleKeyPressOnImage, this);

    // Hide all buttons by default
    this.add_button.hide();
    this.update_button.hide();
    this.resize_button.hide();

    // If there is an reference selected display add or update button correspondantly
    var self = this;

    this.content.change(function(event, info) {
        if (info['path']) {
            if (self.image) {
                // We have a new reference and an existing image
                self.add_button.hide();
                self.update_button.show();
            } else {
                self.update_button.hide();
                self.add_button.show();
            };
        } else {
            // Nothing selected
            self.update_button.hide();
            self.add_button.hide();
        };
    });
    this.editor.logMessage('Image tool initialized');
};

SilvaImageTool.prototype.getImageOrLink = function () {
    if (this.image == null) {
        return $([]);
    }
    var element = $(this.image);
    if (element.parent().get(0).nodeName == 'A') {
        // If a link is wrapped around the image, return the link.
        return element.parent();
    };
    return element;
};

SilvaImageTool.prototype.handleKeyPressOnImage = function(event) {
    var current = this.getImageOrLink();
    if (!current.length) {
        return;
    };
    var keyCode = event.keyCode;

    if (keyCode == 8 || keyCode == 46) {
        /* 8=backspace, 46=delete */
        if (confirm("Are you sure you want to delete this image?")) {
            this.deleteImage();
        };
    }
    else {
        var collapseToEnd = false;
        var next =  $([]);

        if (keyCode == 9 || keyCode == 13 || keyCode == 34 || keyCode == 39 || keyCode == 40) {
            /* 9 = tab; 13 = enter; 34 = page down; 39 = right; 40 = down; */
            next = current.next();
            if (!next.length) {
                next = $('<p>&nbsp;</p>');
                next.insertAfter(current);
                next = current.next();
                this.editor.content_changed = true;
            };
            this.resetTool();
        } else if (keyCode == 37 || keyCode == 38) {
            /* 33=page up; 37=left arrow, 38=up arrow */
            next = current.prev();
            if (!next.length) {
                next = $('<p>&nbsp;</p>');
                next.insertBefore(current);
                next = current.prev();
                this.editor.content_changed = true;
            };
            collapseToEnd = true;
            this.resetTool();
        };
        if (next.length) {
            var item = next.get(0);
            var selection = this.editor.getSelection();

            selection.selectNodeContents(item);
            selection.collapse(collapseToEnd);
        };
    };
    if (event.preventDefault) {
        event.preventDefault();
    };
    event.returnValue = false;
    return false;
};

SilvaImageTool.prototype.deleteImage = function() {
    var current = this.getImageOrLink();
    if (!current.length) {
        return;
    };
    var next = current.next();
    current.remove();
    if (next.length) {
        var selection = this.editor.getSelection();

        selection.selectNodeContents(next.get(0));
        selection.collapse();
    };
    this.editor.content_changed = true;
    this.resetTool();
};

SilvaImageTool.prototype.createContextMenuElements = function(selNode, event) {
    return new Array(new ContextMenuElement('Create image', this.createImageHandler, this));
};

SilvaImageTool.prototype.createImageHandler = function(event) {
    if (this.editor.suspended) {
        return;
    };

    /* create an image */
    var reference = this.content.reference();
    if (!reference) {
        alert("First select an image.");
        return;
    }

    var default_title = this.content.title();
    var url = this.content.url();
    var self = this;

    var update_attributes = function(image) {
        /* set image information */
        image.removeAttribute('height');
        image.removeAttribute('width');
        image.removeAttribute('style');
        image.setAttribute('_silva_target', reference);
        reference = image.getAttribute('_silva_reference');
        if (!reference) {
            image.setAttribute('_silva_reference', 'new');
        };
        image.setAttribute('alt', default_title);
        image.setAttribute('alignment', self.alignment.val());
        image.setAttribute('src', url);
    };

    if (this.image) {
        // It will restart on update when updateState is called. We
        // don't hide the button as it might have been resized.
        this.stopResizePolling();

        update_attributes(this.image);

        this.editor.content_changed = true;
        this.editor.updateState();
    } else {
        var cache_image = new Image();

        $(cache_image).bind('load', function () {
            var image = self.editor.getInnerDocument().createElement('img');

            update_attributes(image);

            self.editor.insertNodeAtSelection(image, 1);

            self.editor.content_changed = true;
            self.editor.updateState();
        });
        cache_image.src = url;
    }
};

SilvaImageTool.prototype.resetTool = function () {
    this.stopResizePolling();

    if (this.resize_button.is(':visible') && this.image) {
        /* image has been resized, so prompt user to
           confirm resizing */
        this.resize_button.hide();
        if (confirm(
            "Image has been resized in kupu, but not confirmed. " +
                "Really resize?")) {
            this.resizeImage(false);
        };
    };
    this.toolbox.close();
    this.content.clear();
    this.image = null;
};

SilvaImageTool.prototype.updateState = function(selNode, event) {
    var extsourcetool = this.editor.getTool('extsourcetool');
    if (extsourcetool != undefined) {
        if (extsourcetool.getNearestExternalSource(selNode, event)) {
            this.resetTool();
            return;
        };
    };
    var image = this.editor.getNearestParentOfType(selNode, 'img');
    if (image) {
         /* the rest of the image tool was originally designed to
            getNearestparentOfType(img), but the 'confirm resizing'
            feature needs to know what image was active, after is it
            no longer selected.  So store it as a property of the image
            tool */
        this.image = image;
        this.toolbox.open();

        var reference = image.getAttribute('_silva_target');
        var alignment = image.getAttribute('alignment');

        if (reference) {
            this.content.fetch(reference);
        }
        if (alignment) {
            this.alignment.val(alignment);
        }
        this.startResizePolling(image);
    } else {
        this.resetTool();
    };
};

SilvaImageTool.prototype.confirmResizeHandler = function() {
    this.resizeImage(true);
};

SilvaImageTool.prototype.resizeImage = function(continue_polling) {
    var image = this.image;

    if (!image) {
        this.editor.logMessage('No image selected!  unable to resize.');
        return;
    };
    /* Pause polling during resize */
    this.stopResizePolling();
    this.resize_button.hide();

    var self = this;
    var width = image.width;
    var height = image.height;
    var image_url = image.src.replace(/\?.*/,'');

    $.post(
        image_url + '/++rest++image.resize',
        {"width": width,
         "height": height},
        function(data) {
            // Load the new resized image into a cache
            var cache_image = new Image();

            $(cache_image).bind('load', function () {
                image.onload = "this.removeAttribute('style')";
                image.src = cache_image.src;
                if (continue_polling) {
                    // Start polling when the image is loaded.
                    self.startResizePolling(image);
                };
            });
            // Add with and height to prevent image being cached by the browser
            cache_image.src = image.src.replace(/\?.*/,'') + '?' + width + 'x' + height;
        });
};

SilvaImageTool.prototype.startResizePolling = function(image) {
    if (this.resizePollingInterval)
        return;

    var image_size = [image.width, image.height];
    var self = this;

    function polling() {
        var new_image_size = [image.width, image.height];

        if (!(image_size[0] == new_image_size[0] &&
              image_size[1] == new_image_size[1])) {
            // The image have just been resized.
            self.resize_button.show();
            image_size = new_image_size;
        };
    };
    this.resizePollingInterval = setInterval(polling, 300);
};

SilvaImageTool.prototype.stopResizePolling = function() {
    if (this.resizePollingInterval) {
        clearInterval(this.resizePollingInterval);
        this.resizePollingInterval = null;
    };
};


SilvaImageTool.prototype.setAlign = function() {
    var selNode = this.editor.getSelectedNode();
    var image = this.editor.getNearestParentOfType(selNode, 'img');
    if (!image) {
        this.editor.logMessage('Not inside an image', 1);
        return;
    };
    var align = this.alignselect.options[this.alignselect.selectedIndex].value;
    image.setAttribute('alignment', align);
    this.editor.content_changed = true;
};

function SilvaTableTool() {
    /* Silva specific table functionality

       overrides most of the table functionality, required because Silva
       requires a completely different format for tables
    */
};

SilvaTableTool.prototype = new TableTool;

SilvaTableTool.prototype.createTable = function(
        rows, cols, makeHeader, tableclass) {
    /* add a Silvs specific table, with an (optional) header with colspan */
    var doc = this.editor.getInnerDocument();

    var table = doc.createElement('table');
    table.style.width = "100%";
    table.className = tableclass;

    var tbody = doc.createElement('tbody');

    if (makeHeader) {
        this._addRowHelper(doc, tbody, 'th', -1, cols, true);
    };

    for (var i=0; i < rows; i++) {
        this._addRowHelper(doc, tbody, 'td', -1, cols);
    };

    table.appendChild(tbody);

    // make that Silva's column info attribute is calculated and set
    var colinfo = this._getColumnInfo(table);
    this._setColumnInfo(table, colinfo);

    var iterator = new NodeIterator(table);
    var currnode = null;
    var contentcell = null;
    while (currnode = iterator.next()) {
        if (currnode.nodeName.search(/^(TD|TH)$/) > -1) {
            contentcell = currnode;
            break;
        };
    };

    /* put the selection inside the first cell in the table,
       this way the selected content will not get lost */
    var selection = this.editor.getSelection();
    var docfrag = selection.cloneContents();
    if (contentcell && docfrag.hasChildNodes()) {
        while (contentcell.hasChildNodes()) {
            contentcell.removeChild(contentcell.firstChild);
        };
        while (docfrag.hasChildNodes()) {
            contentcell.appendChild(docfrag.firstChild);
        };
    };

    this.editor.insertNodeAtSelection(table);

    this._setTableCellHandlers(table);

    this.editor.content_changed = true;
    this.editor.logMessage('Table added');
    this.editor.updateState();
};

SilvaTableTool.prototype.addTableRow = function(currnode) {
    /* add a table row or header */
    var doc = this.editor.getInnerDocument();
    var tbody = this.editor.getNearestParentOfType(currnode, 'tbody');
    if (!tbody) {
        this.editor.logMessage('No table found!', 1);
        return;
    };
    var cols = this._countColumns(tbody);
    var currrow = this.editor.getNearestParentOfType(currnode, 'tr');
    if (!currrow) {
        this.editor.logMessage('Not inside a row!', 1);
        return;
    };
    var index = this._getRowIndex(currrow) + 1;
    // should check what to add as well
    this._addRowHelper(doc, tbody, 'td', index, cols);
    this.editor.getDocument().getWindow().focus();

    this.editor.content_changed = true;
    this.editor.logMessage('Table row added');
};

SilvaTableTool.prototype.delTableRow = function(currnode) {
    /* delete a table row or header */
    var currtr = this.editor.getNearestParentOfType(currnode, 'tr');

    if (!currtr) {
        this.editor.logMessage('Not inside a row!', 1);
        return;
    };

    currtr.parentNode.removeChild(currtr);

    this.editor.content_changed = true;
    this.editor.getDocument().getWindow().focus();
    this.editor.logMessage('Table row removed');
};

SilvaTableTool.prototype.changeCellColspan = function(newcolspan) {
    var currNode = this.editor.getSelectedNode();
    var currCell = this.editor.getNearestParentOfType(currNode, 'td');
    if (!currCell) {
       currCell = this.editor.getNearestParentOfType(currNode,'th');
    }
    if (!currCell) {
        this.editor.logMessage('Not inside a cell!', 1);
        return;
    }
    this.editor.content_changed = true;
    currCell.setAttribute('colspan',newcolspan);
}

SilvaTableTool.prototype.changeCellType = function(newtype) {
    /* change a single cell's type between <th> and <td> */
    var currNode = this.editor.getSelectedNode();
    var currCell = this.editor.getNearestParentOfType(currNode, 'td');
    if (!currCell) {
       var currCell = this.editor.getNearestParentOfType(currNode,'th');
    }
    if (!currCell) {
        this.editor.logMessage('Not inside a cell!', 1);
        return;
    }

    if (newtype.toUpperCase() == currCell.nodeName) {
        this.editor.logMessage('Table cell unchanged');
    } else {
    var doc = this.editor.getInnerDocument();
    var newCell = doc.createElement(newtype);
    for (var i=0; i < currCell.childNodes.length; i++) {
        newCell.appendChild(currCell.firstChild);
    }
    if (currCell.getAttribute('class'))
        newCell.setAttribute('class',currCell.getAttribute('class'));
    if (currCell.getAttribute('align'))
        newCell.setAttribute('align',currCell.getAttribute('align'));
    if (currCell.getAttribute('width'))
        newCell.setAttribute('width',currCell.getAttribute('width'));
    if (currCell.getAttribute('colspan'))
        newCell.setAttribute('colspan',currCell.getAttribute('colspan'));
    currCell.parentNode.replaceChild(newCell,currCell);
        this.editor.content_changed = true;
    }
    var selection = this.editor.getSelection();
    selection.selectNodeContents(newCell);
    selection.collapse(true);
    this.editor.content_changed = true;
};

SilvaTableTool.prototype.addCell = function(before, widthinput) {
    /* add a table cell before or after the cell containing the current
       selection */
    var currnode = this.editor.getSelectedNode();
    var doc = this.editor.getInnerDocument();
    var table = this.editor.getNearestParentOfType(currnode, 'table');
    if (!table) {
        this.editor.logMessage('Not inside a table!');
        return;
    };
    var currcell = this.editor.getNearestParentOfType(currnode, 'td');
    if (!currcell) {
        var currcell = this.editor.getNearestParentOfType(currnode, 'th');
        if (!currcell) {
            this.editor.logMessage('Not inside a row!', 1);
            return;
        }
    }
    var newcell = doc.createElement(currcell.tagName);
    newcell.appendChild(doc.createTextNode('\u00a0'));
    if (before) {
    currcell.parentNode.insertBefore(newcell, currcell);
    } else {
    currcell.parentNode.insertBefore(newcell, currcell.nextSibling);
    }
    var selection = this.editor.getSelection();
    selection.selectNodeContents(newcell);
    selection.collapse(true);

    table.removeAttribute('_silva_column_info');
    this._getColumnInfo();
    widthinput.value = this.getColumnWidths(table);
    this.editor.content_changed = true;
    this.editor.logMessage('cell added');
};

SilvaTableTool.prototype.removeCell = function(widthinput) {
    /* remove a  table cell before or after the cell containing the current
       selection */
    var currnode = this.editor.getSelectedNode();
    var doc = this.editor.getInnerDocument();
    var table = this.editor.getNearestParentOfType(currnode, 'table');
    if (!table) {
        this.editor.logMessage('Not inside a table!');
        return;
    };
    var currcell = this.editor.getNearestParentOfType(currnode, 'td');
    if (!currcell) {
        currcell = this.editor.getNearestParentOfType(currnode, 'th');
        if (!currcell) {
            this.editor.logMessage('Not inside a row!', 1);
            return;
        }
    }
    var selection = this.editor.getSelection();
    if (currcell.previousSibling) {
        selection.selectNodeContents(currcell.previousSibling);
    } else if (currcell.nextSibling) {
        selection.selectNodeContents(currcell.nextSibling);
    }
    selection.collapse(true);

    var row = currcell.parentNode;
    row.removeChild(currcell);
    if (!row.hasChildNodes())
    row.parentNode.removeChild(row);

    table.removeAttribute('_silva_column_info');
    this._getColumnInfo();
    widthinput.value = this.getColumnWidths(table);
    this.editor.content_changed = true;
    this.editor.getDocument().getWindow().focus();
    this.editor.logMessage('cell removed');
};

SilvaTableTool.prototype.changeCellType = function(newtype) {
    /* change a single cell's type between <th> and <td> */
    var currNode = this.editor.getSelectedNode();
    var currCell = this.editor.getNearestParentOfType(currNode, 'td');
    if (!currCell) {
        currCell = this.editor.getNearestParentOfType(currNode,'th');
    };
    if (!currCell) {
        this.editor.logMessage('Not inside a cell!', 1);
        return;
    };

    if (newtype.toUpperCase() == currCell.nodeName) {
        this.editor.logMessage('Table cell unchanged');
    } else {
        var doc = this.editor.getInnerDocument();
        var newCell = doc.createElement(newtype);
        while (currCell.hasChildNodes()) {
            newCell.appendChild(currCell.firstChild);
        };
        if (currCell.className) {
            newCell.className = currCell.className;
        };
        if (currCell.align && currCell.align != 'left') {
            newCell.align = currCell.align;
        };
        if (currCell.width) {
            newCell.width = currCell.width;
        };
        if (currCell.colSpan && currCell.colSpan > 1) {
            newCell.colSpan = currCell.colSpan;
        };
        currCell.parentNode.replaceChild(newCell, currCell);
        this.editor.content_changed = true;
    };
    var selection = this.editor.getSelection();
    selection.selectNodeContents(newCell);
    selection.collapse(true);
};

SilvaTableTool.prototype.addTableColumn = function(currnode) {
    /* add a table column */
    var doc = this.editor.getInnerDocument();
    var table = this.editor.getNearestParentOfType(currnode, 'table');
    if (!table) {
        this.editor.logMessage('Not inside a table!');
        return;
    };
    var body = table.getElementsByTagName('tbody')[0];
    var currcell = this.editor.getNearestParentOfType(currnode, 'td');
    if (!currcell) {
        currcell = this.editor.getNearestParentOfType(currnode, 'th');
        if (!currcell) {
            this.editor.logMessage('Not inside a cell!', 1);
            return;
        };
    };
    var index = this._getColIndex(currcell) + 1;
    var numcells = this._countColumns(body);
    this._addColHelper(doc, body, index, numcells);

    var widths = this.getColumnWidths(table);
    this.editor.content_changed = true;
    this.editor.logMessage('Column added');

    return widths;
};

SilvaTableTool.prototype.delTableColumn = function(currnode) {
    /* delete a column */
    var table = this.editor.getNearestParentOfType(currnode, 'table');
    if (!table) {
        this.editor.logMessage('Not inside a table body!', 1);
        return;
    };
    var body = table.getElementsByTagName('tbody')[0];
    var currcell = this.editor.getNearestParentOfType(currnode, 'td');
    if (!currcell) {
        currcell = this.editor.getNearestParentOfType(currnode, 'th');
        if (!currcell) {
            this.editor.logMessage('Not inside a cell!');
            return;
        };
    };

    if (this._getAllColumns(currcell.parentNode).length == 1) {
        this.editor.logMessage('Can not delete the last cell of a table!');
        return;
    };

    var index = this._getColIndex(currcell);
    this._delColHelper(body, index);

    var widths = this.getColumnWidths(table);
    this.editor.content_changed = true;
    this.editor.logMessage('Column deleted');

    return widths;
};

SilvaTableTool.prototype.mergeTableCell =
            function mergeTableCell(currnode) {
    // I think it's safe to assume every table will have a tbody...
    var cell = this.editor.getNearestParentOfType(currnode, 'td') ||
        this.editor.getNearestParentOfType(currnode, 'th');
    var tr = this.editor.getNearestParentOfType(cell, 'tr');
    var table = this.editor.getNearestParentOfType(tr, 'table');
    var index = this._getColIndex(cell);

    var tbody = table.getElementsByTagName('tbody')[0];
    var currindex = 0;
    for (var j=0; j < tr.childNodes.length; j++) {
        var child = tr.childNodes[j];
        if (child.nodeType != 1) {
            continue;
        };
        if (child.nodeName != 'TH' && child.nodeName != 'TD') {
            // unexpected child name, log and continue
            this.editor.logMessage(
                'unexpected child ' + child.nodeName +
                ' for table row');
            continue;
        };
        if (currindex == index) {
            // merge with next cell
            var havenext = true;
            var next = child;
            do {
                next = next.nextSibling;
                if (next === undefined || next === null) {
                    this.editor.logMessage(
                        'not enough children in row to apply merge');
                    havenext = false;
                    break;
                };
            } while (next.nodeName != 'TD' && next.nodeName != 'TH');
            if (!havenext) {
                continue;
            };
            var colspan = child.colSpan || 1;
            child.colSpan = colspan + 1;
            child.appendChild(child.ownerDocument.createElement('br'));
            while (next.hasChildNodes()) {
                child.appendChild(next.firstChild);
            };
            next.parentNode.removeChild(next);
            break;
        };
        currindex += child.colSpan || 1;
    };

    var widths = this.getColumnWidths(table);
    this.editor.content_changed = true;
    this.editor.logMessage('Cell merged');

    return widths;
};

SilvaTableTool.prototype.splitTableCell =
        function splitTableCell(currnode) {
    var cell = this.editor.getNearestParentOfType(currnode, 'td') ||
        this.editor.getNearestParentOfType(currnode, 'th');
    var index = this._getColIndex(cell);
    var tr = this.editor.getNearestParentOfType(cell, 'tr');
    var table = this.editor.getNearestParentOfType(cell, 'table');

    var currindex = 0;
    for (var j=0; j < tr.childNodes.length; j++) {
        var child = tr.childNodes[j];
        if (child.nodeType != 1) {
            continue;
        };
        if (child.nodeName != 'TH' && child.nodeName != 'TD') {
            // unexpected child name, log and continue
            this.editor.logMessage(
                'unexpected child ' + child.nodeName +
                ' for table row');
            continue;
        };
        var colspan = child.colSpan || 1;
        if (currindex == index) {
            if (colspan == 1) {
                this.editor.logMessage(
                    'can not split cell without colspan');
                continue;
            };
            if (colspan > 2) {
                child.colSpan = colspan - 1;
            } else {
                child.colSpan = 1;
                child.removeAttribute('colspan'); // just to clean up a bit
            };
            var newchild = child.ownerDocument.createElement(
                child.nodeName);
            if (child.className) {
                newchild.className = child.className;
            };
            if (child.align && child.align != 'left') {
                newchild.align = child.align;
            };
            newchild.appendChild(
                child.ownerDocument.createTextNode('\ufeff'));
            if (child.nextSibling) {
                child.parentNode.insertBefore(newchild, child.nextSibling);
            } else {
                child.parentNode.appendChild(newchild);
            };
        };
        currindex += colspan;
    };

    var widths = this.getColumnWidths(table);
    this.editor.content_changed = true;
    this.editor.logMessage('Cell split');

    return widths;
};

SilvaTableTool.prototype.setColumnWidths = function(widths) {
    /* sets relative column widths */
    var selNode = this.editor.getSelectedNode();
    var table = this.editor.getNearestParentOfType(selNode, 'table');

    if (!table) {
        this.editor.logMessage('not a table');
        return;
    };

    var colinfo = this._getColumnInfo(table);
    if (widths.length != colinfo.length) {
        alert('number of widths doesn\'t match number of columns!');
        return;
    };
    for (var i=0; i < widths.length; i++) {
        colinfo[i][1] = widths[i];
    };
    this._setColumnInfo(table, colinfo);
    this._updateTableFromInfo(table);
    this.editor.content_changed = true;
    this.editor.logMessage('table column widths adjusted');
};

SilvaTableTool.prototype.getColumnWidths = function(table) {
    var colinfo = this._getColumnInfo(table);
    var widths = [];
    for (var i=0; i < colinfo.length; i++) {
        widths.push(colinfo[i][1]);
    };
    widths = this._factorWidths(widths);
    return widths;
};

SilvaTableTool.prototype.setColumnAlign = function(align) {
    var currnode = this.editor.getSelectedNode();
    var currtd = this.editor.getNearestParentOfType(currnode, 'td');
    if (!currtd) {
        var currtd = this.editor.getNearestParentOfType(currnode, 'th');
    };
    var index = 0;
    if (!currtd) {
        return; // might be we're not inside a table
    } else {
        var cols = this._getAllColumns(currtd.parentNode);
        for (var i=0; i < cols.length; i++) {
            if (cols[i] == currtd) {
                index = i;
                break;
            };
        };
    };
    var table = this.editor.getNearestParentOfType(currnode, 'table');
    var infos = this._getColumnInfo(table);
    infos[index][0] = align;
    this._setColumnInfo(table, infos);
    this._updateTableFromInfo(table);
    this.editor.content_changed = true;
};

SilvaTableTool.prototype._factorWidths = function(widths) {
    var highest = 0;
    for (var i=0; i < widths.length; i++) {
        if (widths[i] > highest) {
            highest = widths[i];
        };
    };
    var factor = 1;
    for (var i=0; i < highest; i++) {
        var testnum = highest - i;
        var isfactor = true;
        for (var j=0; j < widths.length; j++) {
            if (widths[j] % testnum != 0) {
                isfactor = false;
                break;
            };
        };
        if (isfactor) {
            factor = testnum;
            break;
        };
    };
    if (factor > 1) {
        for (var i=0; i < widths.length; i++) {
            widths[i] = widths[i] / factor;
        };
    };
    return widths;
};

SilvaTableTool.prototype._addRowHelper = function(
        doc, body, celltype, index, numcells, colspan_all) {
    /* actually adds a row to the table */
    var row = doc.createElement('tr');

    // fill the row with cells
    if (colspan_all) {
        var cell = doc.createElement(celltype);
        cell.appendChild(doc.createTextNode("\ufeff"));
        cell.colSpan = numcells;
        row.appendChild(cell);
    } else {
        for (var i=0; i < numcells; i++) {
            var cell = doc.createElement(celltype);
            cell.appendChild(doc.createTextNode("\ufeff"));
            row.appendChild(cell);
        };
    };

    // now append it to the tbody
    var rows = this._getAllRows(body);
    if (index == -1 || index >= rows.length) {
        body.appendChild(row);
    } else {
        var nextrow = rows[index];
        body.insertBefore(row, nextrow);
    };

    return row;
};

SilvaTableTool.prototype._addColHelper =
        function _addColHelper(doc, body, index, numcells) {
    /* actually adds a column to a table */
    var table = this.editor.getNearestParentOfType(body, 'table');
    this._updateTableFromInfo(table);
    var colinfo = this._getColumnInfo(table);
    var rows = this._getAllRows(body);
    for (var i=0; i < rows.length; i++) {
        var row = rows[i];
        var cols = this._getAllColumns(row);
        var currindex = 0;
        var added = false;
        var col = null;
        for (var j=0; j < cols.length; j++) {
            col = cols[j];
            var cell = doc.createElement(col.nodeName);
            cell.appendChild(doc.createTextNode('\ufeff'));
            if (index <= currindex) {
                row.insertBefore(cell, col);
                added = true;
                break;
            };
            currindex += col.colSpan || 1;
        };
        if (!added) {
            var cell = doc.createElement(col.nodeName || 'td');
            cell.appendChild(doc.createTextNode('\ufeff'));
            row.appendChild(cell);
        };
    };
    colinfo.splice(index, 0, ['left', 1]);
    this._setColumnInfo(table, colinfo);
    this._updateTableFromInfo(table, colinfo);
};

SilvaTableTool.prototype._delColHelper = function(body, index) {
    /* actually delete all cells in a column */
    /* needs to be smarter when deleting rows containing th's */
    var current = this.editor.getSelectedNode();
    var currcell = this.editor.getNearestParentOfType(current, 'td') ||
        this.editor.getNearestParentOfType(current, 'th');
    var rows = this._getAllRows(body);
    var numcols = this._countColumns(body);
    var table = this.editor.getNearestParentOfType(body, 'table');
    var colinfo = this._getColumnInfo(table);
    var toselect = current;
    for (var i=0; i < rows.length; i++) {
        var row = rows[i];
        var cols = this._getAllColumns(row);
        var currindex = 0;
        for (var j=0; j < cols.length; j++) {
            var col = cols[j];
            if (currindex == index ||
                    (col.colSpan && index < currindex + col.colSpan)) {
                if (col.colSpan && col.colSpan > 1) {
                    if (col.colSpan > 2) {
                        col.colSpan = col.colSpan - 1;
                    } else {
                        col.colSpan = 1;
                        col.removeAttribute('colspan');
                    };
                } else {
                    if (col == currcell) {
                        // we're going to remove the cell that contains the
                        // current selection - need to find a new location to
                        // select
                        var toselect = currcell.previousSibling;
                        var sel = this.editor.getSelection();
                        while (toselect && toselect.nodeType != 1) {
                            toselect = toselect.previousSibling;
                        };
                        if (!toselect) {
                            // must have been the first column, perhaps the
                            // next works better...
                            toselect = currcell.nextSibling;
                            while (toselect && toselect.nodeType != 1) {
                                toselect = toselect.nextSibling;
                            };
                            if (toselect) {
                                sel.selectNodeContents(toselect);
                            };
                        } else {
                            sel.selectNodeContents(toselect);
                        };
                    };
                    col.parentNode.removeChild(col);
                };
                break;
            };
            currindex += col.colSpan || 1;
        };
    };
    colinfo.splice(index, 1);
    this._setColumnInfo(table, colinfo);
    this._updateTableFromInfo(table, colinfo);
};

SilvaTableTool.prototype._getRowIndex = function(row) {
    /* get the current rowindex */
    var rowindex = 0;
    var prevrow = row.previousSibling;
    while (prevrow) {
        if (prevrow.nodeName == 'TR') {
            rowindex++;
        };
        prevrow = prevrow.previousSibling;
    };
    return rowindex;
};

SilvaTableTool.prototype._countColumns = function(body) {
    /* get the current column count
    */
    var row = this._getAllRows(body)[0];
    var cols = this._getAllColumns(row);
    var numcols = 0;
    for (var i=0; i < cols.length; i++) {
        numcols += cols[i].colSpan || 1;
    };
    return numcols;
};

SilvaTableTool.prototype._getAllRows = function(body) {
    /* returns an Array of all available rows */
    var rows = new Array();
    for (var i=0; i < body.childNodes.length; i++) {
        var node = body.childNodes[i];
        if (node.nodeName == 'TR') {
            rows.push(node);
        };
    };
    return rows;
};

SilvaTableTool.prototype._getAllColumns = function(row) {
    /* returns an Array of all columns in a row */
    var cols = new Array();
    for (var i=0; i < row.childNodes.length; i++) {
        var node = row.childNodes[i];
        if (node.nodeName.search(/^(TD|TH)$/) > -1) {
            cols.push(node);
        };
    };
    return cols;
};

SilvaTableTool.prototype._getColumnInfo =
        function _getColumnInfo(table, ignore_attribute) {
    var mapping = {'C': 'center', 'L': 'left', 'R': 'right'};
    var revmapping = {'center': 'C', 'left': 'L', 'right': 'R'};
    if (!table) {
        var selNode = this.editor.getSelectedNode();
        var table = this.editor.getNearestParentOfType(selNode, 'table');
    };
    if (!table) {
        return;
    };
    var silvacolinfo = table.getAttribute('_silva_column_info');
    if (!ignore_attribute && silvacolinfo) {
        var infos = silvacolinfo.split(' ');
        var ret = [];
        for (var i=0; i < infos.length; i++) {
            var tup = infos[i].split(':');
            ret.push([mapping[tup[0]], tup[1]]);
        };
        return ret;
    } else {
        var iterator = new NodeIterator(table);
        var body;
        do {
            body = iterator.next();
        } while (body.nodeName != 'TBODY');
        var rows = this._getAllRows(body);
        var ret = [];
        var colinfo = [];
        for (var i=0; i < rows.length; i++) {
            var cols = this._getAllColumns(rows[i]);
            var widths = [];
            var aligns = [];
            var usedata = true;
            for (var j=0; j < cols.length; j++) {
                // if we have a colspan, this row is useless, skip to the
                // next _unless_ this is the last row already, in which case
                // it's the best we've got...
                var col = cols[j];
                var colspan = col.colSpan || 1;
                if (colspan > 1 && i < rows.length - 1) {
                    usedata = false;
                    break;
                };
                var align = 'left';
                var className = cols[j].className;
                if (className.indexOf('align-') == 0) {
                    align = className.substr(6);
                };
                var width = cols[j].width;
                width = !width ? 1 : parseInt(width);
                width = Math.ceil(width / (colspan * 1.0));
                aligns.push(align);
                widths.push(width);
                // if we have colspan > 1 here, we're the last row and we need
                // to make something up for the colspanned cells
                for (var k=1; k < colspan; k++) {
                    aligns.push('left');
                    widths.push(width);
                };
            };
            if (!usedata) {
                // we skip this row
                colinfo = [];
                continue;
            };
            widths = this._factorWidths(widths);
            for (var j=0; j < widths.length; j++) {
                ret.push([aligns[j], widths[j]]);
                colinfo.push(revmapping[aligns[j]] + ':' + widths[j]);
            };
            // we're done here
            break;
        };
        return ret;
    };
};

SilvaTableTool.prototype._setColumnInfo = function(table, info) {
    var mapping = {'center': 'C', 'left': 'L', 'right': 'R'};
    var str = [];
    for (var i=0; i < info.length; i++) {
        str.push(mapping[info[i][0]] + ':' + info[i][1]);
    };
    table.setAttribute('_silva_column_info', str.join(' '));
};

SilvaTableTool.prototype._updateTableFromInfo =
        function _updateTableFromInfo(table, colinfo) {
    if (colinfo === undefined || colinfo === null) {
        colinfo = this._getColumnInfo(table);
    };

    // convert the relative widths to percentages first
    var totalunits = 0;
    for (var i=0; i < colinfo.length; i++) {
        if (colinfo[i][1] == '*') {
            totalunits += 1;
        } else {
            totalunits += parseInt(colinfo[i][1]);
        };
    };

    // if all colinfo widths are 1, replace them all with *
    var allone = true;
    for (var i=0; i < colinfo.length; i++) {
        var width = colinfo[i][1];
        if (width != 1 && width != '*') {
            allone = false;
            break;
        };
    };
    if (allone) {
        for (var i=0; i < colinfo.length; i++) {
            colinfo[i][1] = '*';
        };
    };

    var percent_per_unit = 100.0 / totalunits;

    // find the rows containing cells
    var rows = this._getAllRows(table.getElementsByTagName('tbody')[0]);
    for (var i=0; i < rows.length; i++) {
        var cols = this._getAllColumns(rows[i]);
        var index = 0;
        for (var j=0; j < cols.length; j++) {
            var col = cols[j];
            var align = colinfo[index][0];
            var colspan = col.colSpan || 1;
            if (align != 'left') {
                col.className = 'align-' + align;
            };
            var colwidth = 0;
            for (var k=0; k < colspan; k++) {
                var width = colinfo[index + k][1];
                if (width == '*') {
                    colwidth = '*';
                    break;
                } else {
                    colwidth += parseInt(width);
                };
            };
            if (colwidth == '*') {
                col.removeAttribute('width');
            } else {
                col.setAttribute(
                    'width', '' + (colwidth * percent_per_unit) + '%');
            };
            index += col.colSpan || 1;
        };
    };
};

function SilvaTableToolBox(addtabledivid, edittabledivid, newrowsinputid,
        newcolsinputid, makeheaderinputid, classselectid,
        alignselectid, widthinputid, addtablebuttonid,
        addrowbuttonid, delrowbuttonid, addcolbuttonid,
        delcolbuttonid, mergecellbuttonid, splitcellbuttonid,
        fixbuttonid, delbuttonid, toolboxid,
        plainclass, activeclass, celltypeid) {
    /* Silva specific table functionality
        overrides most of the table functionality, required because Silva
        requires a completely different format for tables
    */

    this.addtablediv = getFromSelector(addtabledivid);
    this.edittablediv = getFromSelector(edittabledivid);
    this.newrowsinput = getFromSelector(newrowsinputid);
    this.newcolsinput = getFromSelector(newcolsinputid);
    this.makeheaderinput = getFromSelector(makeheaderinputid);
    this.classselect = getFromSelector(classselectid);
    this.alignselect = getFromSelector(alignselectid);
    this.widthinput = getFromSelector(widthinputid);
    this.addtablebutton = getFromSelector(addtablebuttonid);
    this.addrowbutton = getFromSelector(addrowbuttonid);
    this.delrowbutton = getFromSelector(delrowbuttonid);
    this.addcolbutton = getFromSelector(addcolbuttonid);
    this.delcolbutton = getFromSelector(delcolbuttonid);
    this.mergecellbutton = getFromSelector(mergecellbuttonid);
    this.splitcellbutton = getFromSelector(splitcellbuttonid);
    this.fixbutton = getFromSelector(fixbuttonid);
    this.delbutton = getFromSelector(delbuttonid);
    this.toolboxel = getFromSelector(toolboxid);
    this.celltypesel = getFromSelector(celltypeid);
    this.plainclass = plainclass;
    this.activeclass = activeclass;
};

SilvaTableToolBox.prototype = new TableToolBox;

SilvaTableToolBox.prototype.initialize = function(tool, editor) {
    /* attach the event handlers */
    this.tool = tool;
    this.editor = editor;
    addEventHandler(this.addtablebutton, "click", this.addTable, this);
    addEventHandler(this.addrowbutton, "click", this.addTableRow, this);
    addEventHandler(this.delrowbutton, "click", this.delTableRow, this);
    addEventHandler(this.addcolbutton, "click", this.addTableColumn, this);
    addEventHandler(this.delcolbutton, "click", this.delTableColumn, this);
    addEventHandler(this.mergecellbutton, 'click', this.mergeTableCell, this);
    addEventHandler(this.splitcellbutton, 'click', this.splitTableCell, this);
    addEventHandler(this.fixbutton, "click", this.fixTable, this);
    addEventHandler(this.delbutton, "click", this.delTable, this);
    addEventHandler(this.alignselect, "change", this.setColumnAlign, this);
    addEventHandler(this.classselect, "change", this.setTableClass, this);
    addEventHandler(this.widthinput, "change", this.setColumnWidths, this);
    addEventHandler(this.celltypesel, "change", this.changeCellType, this);
    this.edittablediv.style.display = "none";
    this.editor.logMessage('Table tool initialized');
};

SilvaTableToolBox.prototype.delTable = function() {
    this.tool.delTable();
    this.editor.getDocument().getWindow().focus();
    this.editor.updateState();
};

SilvaTableToolBox.prototype.addTableRow = function addTableRow() {
    var current = this.editor.getSelectedNode();
    this.tool.addTableRow(current);
};

SilvaTableToolBox.prototype.delTableRow = function delTableRow() {
    var current = this.editor.getSelectedNode();
    this.tool.delTableRow(current);
};

SilvaTableToolBox.prototype.resetTool = function() {
    this.edittablediv.style.display = "none";
    this.addtablediv.style.display = "block";
    this.alignselect.selectedIndex = 0;
    this.classselect.selectedIndex = 0;
    if (this.toolboxel) {
        this.toolboxel.className = this.plainclass;
    };
};

SilvaTableToolBox.prototype.updateState = function(selNode) {
    /* update the state (add/edit) and update the pulldowns (if required) */
    var extsourcetool = this.editor.getTool('extsourcetool');
    if (extsourcetool != undefined) {
        if (extsourcetool.getNearestExternalSource(selNode)) {
            this.resetTool();
            return;
        };
    };
    var table = this.editor.getNearestParentOfType(selNode, 'table');
    if (table) {
        this.addtablediv.style.display = "none";
        this.edittablediv.style.display = "block";
        var td = this.editor.getNearestParentOfType(selNode, 'td');
        if (!td) {
            td = this.editor.getNearestParentOfType(selNode, 'th');
        };

        if (td) {
            var align = td.className.split('-')[1];
            if (align == 'center' || align == 'left' || align == 'right') {
                selectSelectItem(this.alignselect, align);
            };
            /* XXX setup the tc type switching */
            selectSelectItem(this.celltypesel, td.nodeName.toLowerCase());
            this.widthinput.value = this.tool.getColumnWidths(table);

            if (td.colSpan && td.colSpan > 1) {
                // show split button
                this.splitcellbutton.style.display = 'inline';
            } else {
                this.splitcellbutton.style.display = 'none';
            };

            if (this.tool._getColIndex(td) <
                    this.tool._getAllColumns(td.parentNode).length - 1) {
                this.mergecellbutton.style.display = 'inline';
            } else {
                this.mergecellbutton.style.display = 'none';
            };
            // XXX would be nice to hide the tr entirely when neither of the
            // buttons are displayed, but later...
        };
        selectSelectItem(this.classselect, table.className);
        if (this.toolboxel) {
            if (this.toolboxel.open_handler) {
                this.toolboxel.open_handler();
            };
            this.toolboxel.className = this.activeclass;
        };
    } else {
        this.resetTool();
    };
};

SilvaTableToolBox.prototype.addTable = function() {
    /* add a Silvs specific table, with an (optional) header with colspan */
    var rows = parseInt(this.newrowsinput.value||1);
    var cols = parseInt(this.newcolsinput.value||3);
    var makeHeader = this.makeheaderinput.checked;
    var classchooser = getFromSelector("kupu-table-classchooser-add");
    var tableclass = this.classselect.options[
        this.classselect.selectedIndex].value;
    this.tool.createTable(rows, cols, makeHeader, tableclass);
    this.editor.content_changed = true;
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.setTableClass = function() {
    var cls = this.classselect.options[this.classselect.selectedIndex].value;
    this.tool.setTableClass(cls);
    this.editor.content_changed = true;
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.changeCellType = function() {
    this.tool.changeCellType(
        this.celltypesel.options[this.celltypesel.selectedIndex].value);
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.delTableColumn = function() {
    var currnode = this.editor.getSelectedNode();
    var widths = this.tool.delTableColumn(currnode);
    this.widthinput.value = widths;
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.addTableColumn = function() {
    var currnode = this.editor.getSelectedNode();
    var widths = this.tool.addTableColumn(currnode);
    this.widthinput.value = widths;
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.mergeTableCell = function mergeTableCell() {
    var currnode = this.editor.getSelectedNode();
    var widths = this.tool.mergeTableCell(currnode);
    this.widthinput.value = widths;
    this.editor.updateState();
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.splitTableCell = function splitTableCell() {
    var currnode = this.editor.getSelectedNode();
    var widths = this.tool.splitTableCell(currnode);
    this.widthinput.value = widths;
    this.editor.updateState();
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.setColumnWidths = function() {
    var swidths = this.widthinput.value.split(',');
    var widths = [];
    for (var i=0; i < swidths.length; i++) {
        var width = parseInt(swidths[i]);
        if (isNaN(width)) {
            alert('width ' + (i + 1) + ' is not a number');
            return;
        };
        widths.push(width);
    };
    this.tool.setColumnWidths(widths);
    this.editor.content_changed = true;
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.setColumnAlign = function() {
    var align = this.alignselect.options[
        this.alignselect.selectedIndex].value;
    this.tool.setColumnAlign(align);
    this.editor.content_changed = true;
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.fixTable = function(event) {
    /* fix the table so it is Silva (and this tool) compliant */
    // since this can be quite a nasty creature we can't just use the
    // helper methods
    // first we create a new tbody element
    var currnode = this.editor.getSelectedNode();
    var table = this.editor.getNearestParentOfType(currnode, 'TABLE');
    if (!table) {
        this.editor.logMessage('Not inside a table!');
        return;
    };
    var doc = this.editor.getInnerDocument();
    var tbody = doc.createElement('tbody');

    var allowed_classes = new Array(
        'plain', 'grid', 'list', 'listing', 'data');
    if (!allowed_classes.contains(table.getAttribute('class'))) {
        table.setAttribute('class', 'plain');
    };

    // now get all the rows of the table, the rows can either be
    // direct descendants of the table or inside a 'tbody', 'thead'
    // or 'tfoot' element
    var rows = new Array();
    var parents = new Array('THEAD', 'TBODY', 'TFOOT');
    for (var i=0; i < table.childNodes.length; i++) {
        var node = table.childNodes[i];
        if (node.nodeName == 'TR') {
            rows.push(node);
        } else if (parents.contains(node.nodeName)) {
            for (var j=0; j < node.childNodes.length; j++) {
                var inode = node.childNodes[j];
                if (inode.nodeName == 'TR') {
                    rows.push(inode);
                };
            };
        };
    };

    // now walk through all rows to clean them up
    for (var i=0; i < rows.length; i++) {
        var row = rows[i];
        var newrow = doc.createElement('tr');
        var currcolnum = 0;
        while (row.childNodes.length > 0) {
            var node = row.childNodes[0];
            if (node.nodeName == 'TH') {
                /* if row only has one element, then we can say
                 it is "inhead", otherwise it isn't */
                numcells = row.getElementsByTagName('td').length +
                    row.getElementsByTagName('th').length;
                if (numcells==1) {
                    newrow.appendChild(node);
                    node.setAttribute('colspan', '1');
                    node.setAttribute('rowspan', '1');
                    continue;
                }
            } else if (node.nodeName != 'TD') {
                row.removeChild(node);
                continue;
            };
            node.setAttribute('rowspan', '1');
            var colspan = node.getAttribute('colspan');
            if (!colspan) {
                node.setAttribute('colspan', '1');
            };
            newrow.appendChild(node);
        };
        if (newrow.childNodes.length) {
            tbody.appendChild(newrow);
        };
    };

    // now remove all the old stuff from the table and add the new tbody
    var tlength = table.childNodes.length;
    for (var i=0; i < tlength; i++) {
        table.removeChild(table.childNodes[0]);
    };
    table.appendChild(tbody);

    this.editor.getDocument().getWindow().focus();

    // now fix table widths if numcols is incorrect
    var colinfo = this.tool._getColumnInfo(table, true);
    this.tool._setColumnInfo(table, colinfo);
    this.widthinput.value = this.tool.getColumnWidths(table);

    this.editor.content_changed = true;
    this.editor.logMessage('Table cleaned up');
};

SilvaTableToolBox.prototype._fixAllTables = function() {
    /* fix all the tables in the document at once */
    return;
    var tables = this.editor.getInnerDocument().getElementsByTagName('table');
    for (var i=0; i < tables.length; i++) {
        this.fixTable(tables[i]);
    };
};

function SilvaIndexTool(
        titleinputid, nameinputid, addbuttonid, updatebuttonid,
        deletebuttonid, toolboxid, plainclass, activeclass) {
    /* a tool to manage index items (named anchors) for Silva */
    this.nameinput = getFromSelector(nameinputid);
    this.titleinput = getFromSelector(titleinputid);
    this.addbutton = getFromSelector(addbuttonid);
    this.updatebutton = getFromSelector(updatebuttonid);
    this.deletebutton = getFromSelector(deletebuttonid);
    this.toolbox = new SilvaToolBox(toolboxid, activeclass, plainclass);
};

SilvaIndexTool.prototype = new KupuTool;

SilvaIndexTool.prototype.initialize = function(editor) {
    /* attach the event handlers */
    this.editor = editor;
    addEventHandler(this.addbutton, 'click', this.addIndex, this);
    addEventHandler(this.updatebutton, 'click', this.updateIndex, this);
    addEventHandler(this.deletebutton, 'click', this.deleteIndex, this);
    if (this.editor.getBrowserName() == 'IE') {
        // need to catch some additional events for IE
        addEventHandler(
            editor.getInnerDocument(), 'keyup', this.handleKeyPressOnIndex,
            this);
        addEventHandler(
            editor.getInnerDocument(), 'keydown', this.handleKeyPressOnIndex,
            this);
    };
    addEventHandler(
        editor.getInnerDocument(), 'keypress', this.handleKeyPressOnIndex,
        this);
    this.updatebutton.style.display = 'none';
    this.deletebutton.style.display = 'none';
};

SilvaIndexTool.prototype.addIndex = function() {
    /* create an index */
    var name = this.nameinput.value;
    name = name.replace(/[^a-zA-Z0-9_:\-\.]/g, "_");
    var title = this.titleinput.value;
    var currnode = this.editor.getSelectedNode();
    var indexel = this.editor.getNearestParentOfType(currnode, 'A');

    if (indexel && indexel.getAttribute('href')) {
        this.editor.logMessage('Can not add index items in anchors');
        return;
    };

    if (!indexel) {
        var doc = this.editor.getDocument();
        var docel = doc.getDocument();
        indexel = docel.createElement('a');
        var text = docel.createTextNode('[' + name + ': ' + title + ']');
        indexel.appendChild(text);
        indexel = this.editor.insertNodeAtSelection(indexel, true);
        indexel.className = 'index';
    };
    indexel.setAttribute('name', name);
    indexel.setAttribute('title', title);
    var sel = this.editor.getSelection();
    sel.collapse(true);
    this.editor.content_changed = true;
    this.editor.logMessage('Index added');
};

SilvaIndexTool.prototype.updateIndex = function() {
    /* update an existing index */
    var currnode = this.editor.getSelectedNode();
    var indexel = this.editor.getNearestParentOfType(currnode, 'A');
    if (!indexel) {
        return;
    };

    if (indexel && indexel.getAttribute('href')) {
        this.editor.logMessage('Can not add an index element inside a link!');
        return;
    };

    var name = this.nameinput.value;
    var title = this.titleinput.value;
    indexel.setAttribute('name', name);
    indexel.setAttribute('title', title);
    while (indexel.hasChildNodes()) {
        indexel.removeChild(indexel.firstChild);
    };
    var text = this.editor.getInnerDocument().createTextNode(
        '[' + name + ': ' + title + ']')
    indexel.appendChild(text);
    this.editor.content_changed = true;
    this.editor.logMessage('Index modified');
};

SilvaIndexTool.prototype.deleteIndex = function() {
    var selNode = this.editor.getSelectedNode();
    var a = this.editor.getNearestParentOfType(selNode, 'a');
    if (!a || a.getAttribute('href')) {
        this.editor.logMessage('Not inside an index element!');
        return;
    };
    a.parentNode.removeChild(a);
    this.editor.content_changed = true;
    this.editor.logMessage('Index element removed');
};

SilvaIndexTool.prototype.handleKeyPressOnIndex = function(event) {
    var selNode = this.editor.getSelectedNode();
    var a = this.editor.getNearestParentOfType(selNode, 'a');
    if (!a || a.getAttribute('href')) {
        return;
    };
    var keyCode = event.keyCode;
    if (keyCode == 8 || keyCode == 46) {
        a.parentNode.removeChild(a);
    } else if (keyCode == 9 || keyCode == 39) {
        var next = a.nextSibling;
        while (next && next.nodeName == 'BR') {
            next = next.nextSibling;
        };
        if (!next) {
            var doc = this.editor.getInnerDocument();
            next = doc.createTextNode('\xa0');
            a.parentNode.appendChild(next);
            this.editor.content_changed = true;
        };
        var selection = this.editor.getSelection();
        // XXX I fear I'm working around bugs here... because of a bug in
        // selection.moveStart() I can't use the same codepath in IE as in Moz
        if (this.editor.getBrowserName() == 'IE') {
            selection.selectNodeContents(a);
            // XXX are we depending on a bug here? shouldn't we move the
            // selection one place to get out of the anchor? it works,
            // but seems wrong...
            selection.collapse(true);
        } else {
            selection.selectNodeContents(next);
            selection.collapse();
            var selection = this.editor.getSelection();
        };
        this.editor.updateState();
    };
    if (event.preventDefault) {
        event.preventDefault();
    } else {
        event.returnValue = false;
    };
    return false;
};

SilvaIndexTool.prototype.resetTool = function() {
    this.toolbox.close();
    this.nameinput.value = '';
    this.titleinput.value = '';
    this.updatebutton.style.display = 'none';
    this.deletebutton.style.display = 'none';
    this.addbutton.style.display = 'inline';
};

SilvaIndexTool.prototype.updateState = function(selNode, event) {
    var extsourcetool = this.editor.getTool('extsourcetool');
    if (extsourcetool != undefined) {
        if (extsourcetool.getNearestExternalSource(selNode, event)) {
            this.resetTool();
            return;
        };
    };
    var indexel = this.editor.getNearestParentOfType(selNode, 'A');
    if (indexel && !indexel.getAttribute('href') && indexel.getAttribute('name')) {
        this.toolbox.open();
        this.nameinput.value = indexel.getAttribute('name');
        this.titleinput.value = indexel.getAttribute('title');
        this.addbutton.style.display = 'none';
        this.updatebutton.style.display = 'inline';
        this.deletebutton.style.display = 'inline';
    } else {
        this.resetTool();
    };
};

SilvaIndexTool.prototype.createContextMenuElements = function(selNode, event) {
    var indexel = this.editor.getNearestParentOfType(selNode, 'A');
    if (indexel && !indexel.getAttribute('href')) {
        return new Array(
            new ContextMenuElement('Delete index', this.deleteIndex, this));
    } else {
        return new Array();
    };
};

function SilvaAbbrTool(
        abbrradioid, acronymradioid, titleinputid, addbuttonid,
        updatebuttonid, delbuttonid,
    toolboxid, plainclass, activeclass) {
    /* tool to manage Abbreviation elements */
    this.abbrradio = getFromSelector(abbrradioid);
    this.acronymradio = getFromSelector(acronymradioid);
    this.titleinput = getFromSelector(titleinputid);
    this.addbutton = getFromSelector(addbuttonid);
    this.updatebutton = getFromSelector(updatebuttonid);
    this.delbutton = getFromSelector(delbuttonid);
    this.toolbox = getFromSelector(toolboxid);
    this.plainclass = plainclass;
    this.activeclass = activeclass;
};

SilvaAbbrTool.prototype = new KupuTool;

SilvaAbbrTool.prototype.initialize = function(editor) {
    this.editor = editor;
    addEventHandler(this.addbutton, 'click', this.addElement, this);
    addEventHandler(this.updatebutton, 'click', this.updateElement, this);
    addEventHandler(this.delbutton, 'click', this.deleteElement, this);

    this.updatebutton.style.display = 'none';
    this.delbutton.style.display = 'none';
};

SilvaAbbrTool.prototype.updateState = function(selNode, event) {
    var extsourcetool = this.editor.getTool('extsourcetool');
    if (extsourcetool != undefined) {
        if (extsourcetool.getNearestExternalSource(selNode, event)) {
            return;
        };
    };
    var element = this.getNearestAbbrAcronym(selNode);
    if (element) {
        this.addbutton.style.display = 'none';
        this.updatebutton.style.display = 'inline';
        this.delbutton.style.display = 'inline';
        this.titleinput.value = element.getAttribute('title');
        if (element.nodeName.toLowerCase() == 'abbr') {
            this.abbrradio.checked = true;
            this.acronymradio.checked = false;
        } else {
            this.abbrradio.checked = false;
            this.acronymradio.checked = true;
        };
        if (this.toolbox) {
            if (this.toolbox.open_handler) {
                this.toolbox.open_handler();
            };
            this.toolbox.className = this.activeclass;
        };
    } else {
        this.addbutton.style.display = 'inline';
        this.updatebutton.style.display = 'none';
        this.delbutton.style.display = 'none';
        this.titleinput.value = '';
        this.abbrradio.checked = true;
        this.acronymradio.checked = false;
        if (this.toolbox) {
            this.toolbox.className = this.plainclass;
        };
    };
};

SilvaAbbrTool.prototype.getNearestAbbrAcronym = function(selNode) {
    var current = selNode;
    while (current && current.nodeType != 9) {
        if (current.nodeType == 1) {
            var nodeName = current.nodeName.toLowerCase();
            if (nodeName == 'abbr' || nodeName == 'acronym') {
                return current;
            };
        };
        current = current.parentNode;
    };
};

SilvaAbbrTool.prototype.addElement = function() {
    var type = this.abbrradio.checked ? 'abbr' : 'acronym';
    var doc = this.editor.getInnerDocument();
    var selNode = this.editor.getSelectedNode();
    if (this.getNearestAbbrAcronym(selNode)) {
        this.editor.logMessage('Can not nest abbr and acronym elements');
        this.editor.getDocument().getWindow().focus();
        return;
    };
    var element = doc.createElement(type);
    element.setAttribute('title', this.titleinput.value);

    var selection = this.editor.getSelection();
    var docfrag = selection.cloneContents();
    var placecursoratend = false;
    if (docfrag.hasChildNodes()) {
        for (var i=0; i < docfrag.childNodes.length; i++) {
            element.appendChild(docfrag.childNodes[i]);
        };
        placecursoratend = true;
    } else {
        var text = doc.createTextNode('\xa0');
        element.appendChild(text);
    };
    this.editor.insertNodeAtSelection(element, 1);
    var selection = this.editor.getSelection();
    selection.collapse(placecursoratend);
    this.editor.getDocument().getWindow().focus();
    var selNode = selection.getSelectedNode();
    this.editor.updateState(selNode);
    this.editor.content_changed = true;
    this.editor.logMessage('Element ' + type + ' added');
};

SilvaAbbrTool.prototype.updateElement = function() {
    var selNode = this.editor.getSelectedNode();
    var element = this.getNearestAbbrAcronym(selNode);
    if (!element) {
        this.editor.logMessage('Not inside an abbr or acronym element!', 1);
        this.editor.getDocument().getWindow().focus();
        return;
    };
    seltype = this.acronymradio.checked ? 'acronym' : 'abbr';
    if (element.nodeName.toLowerCase() != seltype) {
        var doc = this.editor.getInnerDocument();
        newNode = doc.createElement(seltype);
        while (element.hasChildNodes()) {
            newNode.appendChild(element.childNodes[0]);
        };
        element.parentNode.replaceChild(newNode,element);
        element = newNode;
    };
    var title = this.titleinput.value;
    element.setAttribute('title', title);
    this.editor.content_changed = true;
    this.editor.logMessage(
        'Updated ' + element.nodeName.toLowerCase() + ' element');
    this.editor.getDocument().getWindow().focus();
};

SilvaAbbrTool.prototype.deleteElement = function() {
    var selNode = this.editor.getSelectedNode();
    var element = this.getNearestAbbrAcronym(selNode);
    if (!element) {
        this.editor.logMessage('Not inside an abbr or acronym element!', 1);
        this.editor.getDocument().getWindow().focus();
        return;
    };
    element.parentNode.removeChild(element);
    this.editor.content_changed = true;
    this.editor.logMessage(
        'Deleted ' + element.nodeName.toLowerCase() + ' deleted');
    this.editor.getDocument().getWindow().focus();
};

function SilvaCommentsTool(toolboxid) {
    /* tool to manage editor comments */
    this.toolbox = getFromSelector(toolboxid);
    if (this.toolbox) {
        this.tooltray = this.toolbox.getElementsByTagName("div")[0];
        this.tooltrayContent = this.tooltray.getElementsByTagName("div")[0];
    };
};

SilvaCommentsTool.prototype = new KupuTool;

SilvaCommentsTool.prototype.initialize = function(editor) {
    this.editor = editor;
    if (this.toolbox &&
            this.tooltrayContent.offsetHeight > 0 &&
            this.tooltrayContent.offsetHeight < this.tooltray.offsetHeight) {
        this.tooltray.style.height = this.tooltrayContent.offsetHeight + 'px';
        this.tooltray.style.overflow = 'visible';
    };
};


function SilvaExternalSourceTool(
        idselectid, formcontainerid, addbuttonid, cancelbuttonid,
        updatebuttonid, delbuttonid, toolboxid, plainclass, activeclass,
        isenabledid, disabledtextid, nosourcestextid) {
    this.idselect = getFromSelector(idselectid);
    this.formcontainer = getFromSelector(formcontainerid);
    this.addbutton = getFromSelector(addbuttonid);
    this.cancelbutton = getFromSelector(cancelbuttonid);
    this.updatebutton = getFromSelector(updatebuttonid);
    this.delbutton = getFromSelector(delbuttonid);
    this.toolbox = new SilvaToolBox(toolboxid, activeclass, plainclass);
    this.is_enabled = getFromSelector(isenabledid).value == 'True';
    this.disabled_text = getFromSelector(disabledtextid);
    this.nosources_text = getFromSelector(nosourcestextid);
    this.nosources = false;
    this._editing = false;
    this._url = null;
    this._id = null;
    this._form = null;
    this._currentExternalSource = null;

    /* no external sources found, so hide add and select */
    if (this.idselect.options.length==1) {
        this.nosources = true;
        this.idselect.style.display="none";
        this.addbutton.style.display="none";
        this.nosources_text.style.display="block";
    };

    // store the base url, this will be prepended to the id to form the url to
    // get the codesource from (Zope's acquisition will make sure it ends up on
    // the right object)
    var urlparts = document.location.pathname.toString().split('/')
    var urlparts_to_use = [];
    for (var i=0; i < urlparts.length; i++) {
        var part = urlparts[i];
        if (part == 'edit') {
            break;
        };
        urlparts_to_use.push(part);
    };
    this._baseurl = urlparts_to_use.join('/');
};

SilvaExternalSourceTool.prototype = new KupuTool;

SilvaExternalSourceTool.prototype.initialize = function(editor) {
    this.editor = editor;
    addEventHandler(
        this.addbutton, 'click', this.startExternalSourceAddEdit, this);
    addEventHandler(this.cancelbutton, 'click', this.resetTool, this);
    addEventHandler(
        this.updatebutton, 'click', this.startExternalSourceAddEdit, this);
    addEventHandler(this.delbutton, 'click', this.deleteExternalSource, this);
    addEventHandler(this.editor.getInnerDocument(), 'keydown', this.handleKeyPressOnExternalSource, this);

    // search for a special serialized identifier of the current document
    // which is used to send to the ExternalSource element when sending
    // requests so the ExternalSources know their context
    this.docref = null;
    var metas = this.editor.getInnerDocument().getElementsByTagName('meta');
    for (var i=0; i < metas.length; i++) {
        var meta = metas[i];
        if (meta.getAttribute('name') == 'docref') {
            this.docref = meta.getAttribute('content');
        };
    };

    this.updatebutton.style.display = 'none';
    this.delbutton.style.display = 'none';
    this.cancelbutton.style.display = 'none';
    if (!this.is_enabled) {
        this.disabled_text.style.display='block';
        this.addbutton.style.display = 'none';
        this.idselect.style.display = 'none';
    };
};

SilvaExternalSourceTool.prototype.updateState = function(selNode, event) {
    var source = $(this.getNearestExternalSource(selNode, event));

    if (source.length) {
        if (this._currentExternalSource == source) {
            return;
        };
        if (this._currentExternalSource) {
            this._currentExternalSource.removeClass('active');
        };
        this._currentExternalSource = source;
        this._currentExternalSource.addClass('active');

        var source_id = source.attr('source_id');

        selectSelectItem(this.idselect, source_id);
        this.addbutton.style.display = 'none';
        this.cancelbutton.style.display = 'none';
        this.updatebutton.style.display = 'inline';
        this.delbutton.style.display = 'inline';
        this.disabled_text.style.display = 'none';
        this.toolbox.open();
        //this.editor.suspendEditing();

        this.startExternalSourceUpdate(source_id);

        /* update source title */
        this.toolbox.set_title('es \xab' + source.attr('source_title') + '\xbb');
    } else {
        this.resetTool();
    };
};

SilvaExternalSourceTool.prototype.handleKeyPressOnExternalSource = function(event) {
    if (this._currentExternalSource == null) {
        return;
    };
    var keyCode = event.keyCode;
    var source = this._currentExternalSource;

    if (keyCode == 8 || keyCode == 46) {
        /* 8=backspace, 46=delete */
        if (confirm("Are you sure you want to delete this external source?")) {
            this.deleteExternalSource();
        };
    }
    else {
        var collapseToEnd = false;
        var next =  $([]);

        if (keyCode == 9 || keyCode == 13 || keyCode == 34 || keyCode == 39 || keyCode == 40) {
            /* 9 = tab; 13 = enter; 34 = page down; 39 = right; 40 = down; */
            next = source.next();
            if (!next.length) {
                next = $('<p>&nbsp;</p>');
                next.insertAfter(source);
                next = source.next();
                this.editor.content_changed = true;
            };
            this.resetTool();
        } else if (keyCode == 37 || keyCode == 38) {
            /* 33=page up; 37=left arrow, 38=up arrow */
            next = source.prev();
            if (!next.length) {
                next = $('<p>&nbsp;</p>');
                next.insertBefore(source);
                next = source.prev();
                this.editor.content_changed = true;
            };
            collapseToEnd = true;
            this.resetTool();
        };
        if (next.length) {
            var item = next.get(0);
            var selection = this.editor.getSelection();

            selection.selectNodeContents(item);
            selection.collapse(collapseToEnd);
            if (item.nodeName.toLowerCase() == 'div' && item.className == 'externalsource') {
                this.updateState(item);
            };
        };
    };
    if (event.preventDefault) {
        event.preventDefault();
    };
    event.returnValue = false;
    return false;
};

SilvaExternalSourceTool.prototype.getUrlAndContinue = function(id, handler) {
    if (id == this._id) {
        // return cached
        handler.call(this, this._url);
        return;
    };
    var request = new XMLHttpRequest();
    var url = this._baseurl + '/edit/get_extsource_url?id=' + id;
    request.open('GET', url, true);
    var callback = new ContextFixer(function() {
        if (request.readyState == 4) {
            var status_code = request.status.toString();
            if (status_code == '200') {
                var returl = request.responseText;
                this._id = id;
                this._url = returl;
                handler.call(this, returl);
            } else if (status_code == '204'){
                var text = document.createTextNode('Code source ' + id +
                                                   ' is missing, please select a new one.');
                this.formcontainer.appendChild(text);
            } else {
                alert('problem: url ' + url +
                      ' could not be loaded (status ' +
                      request.status + ')');
            };
        };
    }, this);
    request.onreadystatechange = callback.execute;
    request.send('');
};

SilvaExternalSourceTool.prototype.startExternalSourceAddEdit = function() {
    /* if this._editing is true, we edit a source, if false we add a new one */
    if (!this._editing) {
        /* Source 0 position is 'select source' and not a valid source */
        if (this.idselect.selectedIndex == 0) {
            return;
        };
        var source_id = this.idselect.options[this.idselect.selectedIndex].value;

        /* Verify that the user is not adding a source in a table or an header */
        var node = $(this.editor.getSelectedNode());
        if (node.parents('table').length) {
            alert('Code source are not allowed inside a table.');
            return;
        };
        var not_allowed_header_tags = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'];
        for (var i=0; i < not_allowed_header_tags.length; i++){
            if (node.get(0).tagName == not_allowed_header_tags[i]){
                alert('Code source is not allowed inside an header.');
                return;
            };
        };

        this.getUrlAndContinue(source_id, this._continueStartExternalSourceEdit);
    } else {
        this._validateAndSubmit();
    };
};

SilvaExternalSourceTool.prototype._validateAndSubmit =
        function _validateAndSubmit(ignorefocus) {
    // validate the data and take further actions
    var formdata = this._gatherFormData();
    var doc = window.document;
    var request = new XMLHttpRequest();
    request.open('POST', this._url + '/validate_form_to_request', true);
    var callback = new ContextFixer(
        this._addExternalSourceIfValidated, request, this, ignorefocus);
    request.onreadystatechange = callback.execute;
    request.setRequestHeader(
        'Content-Type', 'application/x-www-form-urlencoded');
    formdata += '&docref='+this.docref;
    request.send(formdata);
};

SilvaExternalSourceTool.prototype._continueStartExternalSourceEdit =
        function(url) {
    url = url + '/get_rendered_form_for_editor?docref=' + this.docref;
    var request = new XMLHttpRequest();
    request.open('GET', url, true);
    var callback = new ContextFixer(this._addFormToTool, request, this);
    request.onreadystatechange = callback.execute;
    request.send(null);
    while (this.formcontainer.hasChildNodes()) {
        this.formcontainer.removeChild(this.formcontainer.firstChild);
    };
    var text = document.createTextNode('Loading...');
    this.formcontainer.appendChild(text);
    this.updatebutton.style.display = 'none';
    this.cancelbutton.style.display = 'inline';
    this.addbutton.style.display = 'inline';
    this._editing = true;
};

SilvaExternalSourceTool.prototype.startExternalSourceUpdate = function(source_id) {
    this.getUrlAndContinue(source_id, this._continueStartExternalSourceUpdate);
};

SilvaExternalSourceTool.prototype._continueStartExternalSourceUpdate =
        function(url) {
    url = url + '/get_rendered_form_for_editor';
    var formdata = this._gatherFormDataFromElement();
    formdata += '&docref=' + this.docref;
    var request = new XMLHttpRequest();
    request.open('POST', url, true);
    request.setRequestHeader(
        'Content-Type', 'application/x-www-form-urlencoded');
    var callback = new ContextFixer(this._addFormToTool, request, this);
    request.onreadystatechange = callback.execute;
    request.send(formdata);
    this._editing = true;
    while (this.formcontainer.hasChildNodes()) {
        this.formcontainer.removeChild(this.formcontainer.firstChild);
    };
    var text = document.createTextNode('Loading...');
    this.formcontainer.appendChild(text);
};

SilvaExternalSourceTool.prototype._addFormToTool = function(object) {
    if (this.readyState == 4) {
        if (this.status != '200') {
            if (this.status == '500') {
                alert(
                    'error on the server. body returned:\n' +
                    this.responseText);
            };
            // element not found, return without doing anythink
            object.resetTool();
            return;
        };
        while (object.formcontainer.hasChildNodes()) {
            object.formcontainer.removeChild(object.formcontainer.firstChild);
        };
        // XXX Somehow appending the XML to the form using DOM doesn't
        // work correctly, it looks like the elements aren't HTMLElements
        // but XML elements, don't know how to fix now so I'll use string
        // insertion for now, needless to say it should be changed to DOM
        // manipulation asap...
        // XXX why is this.responseXML.documentElement.xml sometimes
        // 'undefined'?
        var responseText = this.responseText;
        var form = null;
        if (responseText.indexOf(' class="elaborate"') > -1) {
            object._showFormInWindow(object.formcontainer, responseText);
        } else {
            object.formcontainer.innerHTML = this.responseText;
            object.idselect.style.display = 'none';
            // the formcontainer will contain a table with a form
            var iterator = new NodeIterator(object.formcontainer);
            while (form == null) {
                var next = iterator.next();
                if (next.nodeName.toLowerCase() == 'form') {
                    form = next;
                };
            };
        };
        object._form = form;
    };
};

SilvaExternalSourceTool.prototype._showFormInWindow =
        function _showFormInWindow(formcontainer, responseText) {
    if (this._opened_edit_window) {
        this._opened_edit_window = false;
        return this._form;
    };
    this._opened_edit_window = true;
    var lpos = (screen.width - 760) / 2;
    var tpos = (screen.height - 500) / 2;
    var win = window.open("about:blank",
        "extFormWindow", "toolbar=no," +
        "status=no,scrollbars=yes,resizable=yes," +
        "width=760,height=500,left=" + lpos +
        ",top=" + tpos);
    this._extFormWindowOpened = true;
    var loadme = function() {
        var doc = win.document;
        doc.open();
        doc.write(responseText);
        doc.close();
    };
    addEventHandler(win, 'load', loadme, this);
};

SilvaExternalSourceTool.prototype._addExternalSourceIfValidated =
        function(object, ignorefocus) {
    if (this.readyState == 4) {
        if (this.status == '200') {
            // success, add the external source element to the document
            rxml = this.responseXML.documentElement;
            var selNode = object.editor.getSelectedNode();
            var currsource = object.getNearestExternalSource(selNode);
            var doc = object.editor.getInnerDocument();

            var extsource = doc.createElement('div');
            var source_id = object._id;
            var source_title = object.idselect.options[
                object.idselect.selectedIndex].childNodes[0].data;
            extsource.setAttribute('source_id', source_id);
            extsource.setAttribute('source_title', source_title);
            extsource.className = 'externalsource';
            var sourceinfo = rxml.getElementsByTagName("sourceinfo")[0];
            var metatype = sourceinfo.childNodes[0].childNodes[0].data;
            var desc = sourceinfo.childNodes[3];
            if (desc.childNodes.length) {
                desc = desc.childNodes[0].data;
            } else {
                desc = null;
            };

            var header = doc.createElement('h4');
            header.appendChild(
                doc.createTextNode(metatype + ' \xab' +
                source_title + '\xbb'));
            header.setAttribute('title',source_id);
            extsource.appendChild(header);

            if (desc) {
                var desc_el = doc.createElement('p');
                desc_el.className = "externalsource-description";
                desc_el.appendChild(doc.createTextNode(desc));
                extsource.appendChild(desc_el);
            };

            var params = rxml.getElementsByTagName("parameter");
            var pardiv = doc.createElement('div');
            pardiv.setAttribute('class', 'parameters');
            for (var i=0; i < params.length; i++) {
                var child = params[i];
                var key = child.getAttribute('id');
                var value = '';
                for (var j=0; j < child.childNodes.length; j++) {
                    value += child.childNodes[j].nodeValue;
                };
                if (key == 'metatype') {
                    metatype = value;
                    continue;
                };
                // for presentation only change some stuff
                var displayvalue = value.toString();
                var attrkey = key;
                var strong = doc.createElement('strong');
                strong.appendChild(doc.createTextNode(key + ': '));
                pardiv.appendChild(strong);
                if (child.getAttribute('type') == 'list') {
                    var vallist = eval(value);
                    attrkey = key + '__type__list';
                    if (vallist.length == 0) {
                        var span = doc.createElement('span');
                        span.setAttribute('key', attrkey);
                        pardiv.appendChild(span);
                        var textel = doc.createTextNode('');
                        span.appendChild(textel);
                    } else {
                        for (var k=0; k < vallist.length; k++) {
                            var span = doc.createElement('span');
                            span.setAttribute('key', attrkey);
                            pardiv.appendChild(span);
                            var textel = doc.createTextNode(vallist[k]);
                            span.appendChild(textel);
                            if (k < vallist.length - 1) {
                                pardiv.appendChild(doc.createTextNode(', '));
                            };
                        };
                    };
                } else {
                    if (child.getAttribute('type') == 'bool') {
                        value = (value == "1" ? 1 : 0);
                        attrkey = key + '__type__boolean';
                    };
                    var span = doc.createElement('span');
                    span.setAttribute('key', attrkey);
                    pardiv.appendChild(span);
                    var textel = doc.createTextNode(displayvalue);
                    span.appendChild(textel);
                };
                pardiv.appendChild(doc.createElement('br'));
            };
            extsource.appendChild(pardiv);
            if (!currsource) {
                object.editor.insertNodeAtSelection(extsource);
            } else {
                currsource.parentNode.replaceChild(extsource, currsource);
                var selection = object.editor.getSelection();
                selection.selectNodeContents(extsource);
                selection.collapse(true);
            };
            object.editor.content_changed = true;
            object.resetTool();
            if (!ignorefocus) {
                object.editor.updateState();
            };
            /* reset the extsource select box */
            selectSelectItem(object.idselect, '');

            /* load the external source preview */
            var el = new ExternalSourceLoader(extsource);
            el.initialize();
        } else if (this.status == '400') {
            // failure, provide some feedback and return to the form
            alert(
                'Form could not be validated, error message: ' +
                this.responseText);
        } else {
            alert('POST failed with unhandled status ' + this.status);
            throw(
                'Error handling POST, server returned ' + this.status +
                ' HTTP status code');
        };
    };
};

SilvaExternalSourceTool.prototype.deleteExternalSource = function() {
    var source = this._currentExternalSource;
    if (source == null) {
        return;
    };
    var next = source.next();
    source.remove();
    if (next.length) {
        var selection = this.editor.getSelection();

        selection.selectNodeContents(next.get(0));
        selection.collapse();
    };
    this.editor.content_changed = true;
    this.resetTool();
};

SilvaExternalSourceTool.prototype.resetTool = function() {
    if (this._currentExternalSource) {
        this._currentExternalSource.removeClass('active');
        this._currentExternalSource = null;
        this.toolbox.close();
        //this.editor.resumeEditing();

        while (this.formcontainer.hasChildNodes()) {
            this.formcontainer.removeChild(this.formcontainer.firstChild);
        };
        if (!this.is_enabled) {
            this.updatebutton.style.display = 'none';
            this.delbutton.style.display = 'none';
            this.cancelbutton.style.display = 'none';
            this.disabled_text.style.display='block';
            this.addbutton.style.display = 'none';
            this.idselect.style.display = 'none';
        } else {
            this.idselect.style.display = 'inline';
            selectSelectItem(this.idselect, '');
            this.addbutton.style.display = 'inline';
            this.cancelbutton.style.display = 'none';
            this.updatebutton.style.display = 'none';
            this.delbutton.style.display = 'none';
            this.toolbox.set_title('external source');
        };
        //this.editor.updateState();
        this._editing = false;
    };
};

SilvaExternalSourceTool.prototype._gatherFormData = function() {
    /* walks through the form and creates a POST body */
    // XXX we may want to turn this into a helper function, since it's
    // quite useful outside of this object I reckon
    var form = this._form;
    if (!form) {
        this.editor.logMessage('Not currently editing');
        return;
    };
    // first place all data into a dict, convert to a string later on
    var data = {};
    /* this function adds a value to a key in the dict.  If a value
       already exists, it converts the value to an array.
       (supports multi-valued items) */
    var setValue = function(dict, key, value) {
        if (dict[key]) {
            if (typeof dict[key] == typeof('')) {
                var v = new Array(dict[key]);
                v.push(value);
                dict[key] = v;
            } else {
                dict[key].push(value);
            };
        } else {
            dict[key] = value;
        };
    };
    for (var i=0; i < form.elements.length; i++) {
        var child = form.elements[i];
        var elname = child.nodeName.toLowerCase();
        if (elname == 'input') {
            var name = child.getAttribute('name');
            var type = child.getAttribute('type');
            if (!type || type == 'text' || type == 'hidden' ||
                    type == 'password') {
                setValue(data, name, child.value);
            } else if (type == 'checkbox' || type == 'radio') {
                if (child.checked) {
                    setValue(data, name, child.value);
                };
            };
        } else if (elname == 'textarea') {
            setValue(data,child.getAttribute('name'),child.value);
        } else if (elname == 'select') {
            var name = child.getAttribute('name');
            var multiple = child.getAttribute('multiple');
            if (!multiple) {
                setValue(data, name, child.options[child.selectedIndex].value);
            } else {
                for (var j=0; j < child.options.length; j++) {
                    if (child.options[j].selected) {
                        setValue(data, name, child.options[j].value);
                    };
                };
            };
        };
    };

    // now we should turn it into a query string
    var ret = new Array();
    for (var key in data) {
        var value = data[key];
        if (!(value instanceof Array)) {
            value = [value];
        };
        for (var i=0; i < value.length; i++) {
            ret.push(
                encodeURIComponent(key) + '=' + encodeURIComponent(value[i]));
        };
    };

    return ret.join("&");
};

SilvaExternalSourceTool.prototype._gatherFormDataFromElement =
        function(esElement) {
    /* esElement, if passed in, is an externalsource div in the document.
       If passed in, this div will be used rather than attempting to get
       the nearest external source node from the current selection.
       Useful for processing external sources in code outside of the ES
       tool (e.g. the ExternalSource preloader) */
    if (esElement) {
        var source = esElement;
    } else {
        var selNode = this.editor.getSelectedNode();
        var source = this.getNearestExternalSource(selNode);
    };
    if (!source) {
        return '';
    };
    var ret = new Array();
    var spans = source.getElementsByTagName("div")[0]
        .getElementsByTagName('span');
    for (var i=0; i < spans.length; i++) {
        var name = spans[i].getAttribute('key');
        if (spans[i].childNodes.length > 0) {
            var value = spans[i].childNodes[0].nodeValue;
        } else {
            var value = '';
        };
        ret.push(encodeURIComponent(name) + '=' + encodeURIComponent(value));
    };
    return ret.join('&');
};

SilvaExternalSourceTool.prototype.getNearestExternalSource = function(selNode, event) {

    var getSource = function(selNode) {
        var node = $(selNode);

        if (node.get(0).nodeName == 'DIV' && node.hasClass('externalsource')) {
            return node.get(0);
        };
        return $(node).parents('div.externalsource').get(0);
    };
    var source = getSource(selNode);

    if (!source && event) {
        /* if the externalsource element's preview is _only_ a floated
            div, in at least FF, clicking anywhere but inside the div
            will cause selNode to be the body (resulting in extsource==undefined)
            */
        event = event || window.event;
        /* updateState is not always called on an event (like a mouse click
           sometimes it is during initialization */
        if (event) {
            var target = event.srcElement || event.target;
            return getSource(target);
        } else {
            return getSource(this.editor.getSelectedNode());
        };
    };

    return source;
};

function SilvaKupuUI(textstyleselectid) {
    this.tsselect = getFromSelector(textstyleselectid);
};

SilvaKupuUI.prototype = new KupuUI;

SilvaKupuUI.prototype.initialize = function(editor) {
    this.editor = editor;
    this._fixTabIndex(this.tsselect);
    this._selectevent = addEventHandler(
        this.tsselect, 'change', this.setTextStyleHandler, this);
};

SilvaKupuUI.prototype.updateState = function(selNode) {
    /* set the text-style pulldown */

    // first get the nearest style
    // use an object here so we can use the 'in' operator later on
    var styles = {};
    for (var i=0; i < this.tsselect.options.length; i++) {
        // XXX we should cache this
        styles[this.tsselect.options[i].value] = i;
    };

    // search the list of nodes like in the original one, break if we
    // encounter a match, this method does some more than the original
    // one since it can handle commands in the form of
    // '<style>|<classname>' next to the plain '<style>' commands
    var currnode = selNode;
    var index = -1;
    while (index==-1 && currnode) {
        var nodename = currnode.nodeName.toLowerCase();
        for (var style in styles) {
            if (style.indexOf('|') < 0) {
                // simple command
                if (nodename == style.toLowerCase() && !currnode.className) {
                    index = styles[style];
                    break;
                };
            } else {
                // command + classname
                var tuple = style.split('|');
                if (nodename == tuple[0].toLowerCase() &&
                        currnode.className == tuple[1]) {
                    index = styles[style];
                    break;
                };
            };
        };
        currnode = currnode.parentNode;
    };
    this.tsselect.selectedIndex = Math.max(index,0);
};

SilvaKupuUI.prototype.setTextStyle = function(style) {
    /* parse the argument into a type and classname part
        generate a block element accordingly
    */

    var classname = "";
    var eltype = style;
    if (style.indexOf('|') > -1) {
        style = style.split('|');
        eltype = style[0];
        classname = style[1];
    };

    var command = eltype;
    // first create the element, then find it and set the classname
    if (this.editor.getBrowserName() == 'IE') {
        command = '<' + eltype + '>';
    };
    this.editor.getDocument().execCommand('formatblock', command);

    // now get a reference to the element just added
    var selNode = this.editor.getSelectedNode();
    var el = this.editor.getNearestParentOfType(selNode, eltype);

    // now set the classname
    if (classname) {
        el.className = classname;
        el.setAttribute('_silva_type', classname);
    };
    this.editor.content_changed = true;
    this.editor.updateState();
    this.editor.getDocument().getWindow().focus();
};

function SilvaPropertyTool(toolboxid, activeclass, plainclass) {
    this.data = $('#' + toolboxid + '-data');
    this.url = $('#' + toolboxid + '-base').attr('href') +
        '/++rest++kupu-properties';
    this.toolbox = new SilvaToolBox(toolboxid, activeclass, plainclass);
};

SilvaPropertyTool.prototype = new KupuTool;

SilvaPropertyTool.prototype.initialize = function(editor) {
    var self = this;
    this.editor = editor;
    $.getJSON(this.url , function(data) {
        self.loadProperties(data);
    });
};

SilvaPropertyTool.prototype._postForm = function(form_data, callback) {
    $.ajax({
        url: this.url,
        type: 'POST',
        dataType: 'json',
        data: form_data,
        success: callback
    });
};

SilvaPropertyTool.prototype._buildButtonCallback = function(form, data) {
    var self = this;
    var action_label = data['label'];
    var action_name = data['name'];
    var action_type = data['action'];
    return function() {
        if (action_type == 'send' || action_type == 'close_on_success') {
            var form_array = form.serializeArray();
            var form_data = {};
            form_data[action_name] = action_label;
            for (var j=0; j < form_array.length; j++) {
                form_data[form_array[j]['name']] = form_array[j]['value'];
            };
            self._postForm(form_data,  function(data) {
                if (action_type != 'close_on_success' || !data['success']) {
                    self.loadProperties(data);
                }
                else {
                    // remove errors
                    form.find('div.error').each(function(index) {
                        $(this).remove();
                    });
                };
                $(document).trigger('smi-refresh-feedback');
            });
        };
        if (action_type == 'close') {
            self.close();
        };
        return false;
    };
};

SilvaPropertyTool.prototype.loadProperties = function(data) {
    var form = $('<form method="post" enctype="multipart/form-data" '+
                 'class="zeam-form zeam-inline-validation" />');
    this.data.empty();
    this.data.append(form);
    if (data['label']) {
        this.toolbox.set_title(data['label']);
    };
    form.attr('action', this.url);
    form.append(data['widgets']);
    for (var i=0; i < data['actions'].length; i++) {
        var button = $('<input class="button" type="submit" />');
        button.attr('value', data['actions'][i]['label']);
        button.attr('name', data['actions'][i]['name']);
        var callback = this._buildButtonCallback(form, data['actions'][i]);
        button.bind('submit', callback);
        if (data['actions'][i]['name'] == data['default_action']) {
            form.bind('submit', callback);
        };
        form.append(button);
    };
    form.trigger('zeam-form-ready');
    this.toolbox.enable();
};

function SilvaCharactersTool(charselectid) {
    /* a tool to add non-standard characters */
    this._charselect = document.getElementById(charselectid);
};

SilvaCharactersTool.prototype = new KupuTool;

SilvaCharactersTool.prototype.initialize = function(editor) {
    this.editor = editor;
    addEventHandler(this._charselect, 'change', this.addCharacter, this);
    var chars = this.editor.config.nonstandard_chars.split(' ');
    for (var i=0; i < chars.length; i++) {
        var option = document.createElement('option');
        option.value = chars[i];
        var text = document.createTextNode(chars[i]);
        option.appendChild(text);
        this._charselect.appendChild(option);
    };
};

SilvaCharactersTool.prototype.addCharacter = function() {
    var select = this._charselect;
    var c = select.options[select.selectedIndex].value;
    if (!c.strip()) {
        return;
    };
    var selection = this.editor.getSelection();
    var textnode = this.editor.getInnerDocument().createTextNode(c);
    var span = this.editor.getInnerDocument().createElement('span');
    span.appendChild(textnode);
    selection.replaceWithNode(span);
    var selection = this.editor.getSelection();
    selection.selectNodeContents(span);
    selection.collapse(true);
    this.editor.logMessage('Character ' + c + ' inserted');
    this.editor.getDocument().getWindow().focus();
    select.selectedIndex = 0;
    this.editor.content_changed = true;
};
