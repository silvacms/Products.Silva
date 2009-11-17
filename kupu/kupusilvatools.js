/*****************************************************************************
    *
    * Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
    *
    * This software is distributed under the terms of the Kupu
    * License. See LICENSE.txt for license text. For a list of Kupu
    * Contributors see CREDITS.txt.
    *
    *****************************************************************************/

// $Id: kupusilvatools.js 25442 2006-04-06 10:29:19Z guido $

// a mapping from namespace to field names, here you can configure which 
// metadata fields should be editable with the property editor (needs to
// be moved to somewhere in Silva or something?)
EDITABLE_METADATA = {
    'http://infrae.com/namespace/metadata/silva-news-network': 
    [['subjects', 'checkbox', 1, 'subjects'],
     ['target_audiences', 'checkbox', 1, 'target audiences'],
     ['start_datetime', 'datetime', 1, 'start date/time (dmy)'],
     ['end_datetime', 'datetime', 0, 'end date/time (dmy)'],
     ['location', 'text', 0, 'location']]
};

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
    this.params = this.params.replace(/__type__\w*=/g,'=');
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
}

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
                        " [Preview is not available]");
                    h4.appendChild(text)
                    previewDiv.appendChild(h4);
                };
            } else {
                var pc = function(request,pd) {
                    if (request.responseText != "") {
                        pd.innerHTML = request.responseText;
                    } else {
                        var h4 = pd.ownerDocument.createElement("h4");
                        var text = pd.ownerDocument.createTextNode(
                            " [Preview is not available]");
                        hiddenh4 = parentDiv.getElementsByTagName("h4")[0];
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
    if (this.div.className.search("active")==-1) {
        this.div.className += " active"
    };
};

ExternalSourceLoader.prototype.onMouseOutHandler = function(event) {
    /* using a :hover sudo-selector would be nice, but it seems that IE7 can't
       doesn't recognize this selector within designMode */
    if (this.extsourcetool._insideExternalSource != this.div) {
        this.div.className = this.div.className.replace(/ active/,'');
    };
};

function SilvaLinkTool() {
    /* redefine the contextmenu elements */
};

SilvaLinkTool.prototype = new LinkTool;

SilvaLinkTool.prototype.updateLink = function (
        linkel, url, type, name, target, title) {
    if (type && type == 'anchor') {
        linkel.removeAttribute('href');
        linkel.setAttribute('name', name);
    } else {
        linkel.href = url;
        linkel.setAttribute('silva_href', url);
        if (linkel.innerHTML == "") {
            var doc = this.editor.getInnerDocument();
            linkel.appendChild(doc.createTextNode(title || url));
        };
        if (title) {
            linkel.title = title;
        } else {
            linkel.removeAttribute('title');
        };
        if (target && target != '') {
            linkel.setAttribute('target', target);
        } else {
            linkel.removeAttribute('target');
        };
        linkel.style.color = this.linkcolor;
    };
    this.editor.content_changed = true;
};

SilvaLinkTool.prototype.createContextMenuElements = function(selNode, event) {
    /* create the 'Create link' or 'Remove link' menu elements */
    var ret = new Array();
    var link = this.editor.getNearestParentOfType(selNode, 'a');
    if (link) {
        ret.push(new ContextMenuElement('Delete link', this.deleteLink, this));
    } else {
        ret.push(new ContextMenuElement('Create link', getLink, this));
    };
    return ret;
};

function SilvaLinkToolBox(
        inputid, targetselectid, targetinputid, addbuttonid,
        updatebuttonid, delbuttonid, toolboxid, plainclass, activeclass) {
    /* create and edit links */

    this.input = getFromSelector(inputid);
    this.inputTA = document.createElement('textarea');
    this.inputTA.className='store';
    this.inputTA.cols="30";
    this.inputTA.rows="2";
    this.input.parentNode.appendChild(this.inputTA);
    var inputtable = this.input.parentNode.parentNode;
    this.inputeditbutton = inputtable.getElementsByTagName('button')[1];
    this.targetselect = getFromSelector(targetselectid);
    this.targetinput = getFromSelector(targetinputid);
    this.addbutton = getFromSelector(addbuttonid);
    this.updatebutton = getFromSelector(updatebuttonid);
    this.delbutton = getFromSelector(delbuttonid);
    this.toolboxel = getFromSelector(toolboxid);
    this.plainclass = plainclass;
    this.activeclass = activeclass;
};

SilvaLinkToolBox.prototype = new LinkToolBox;

SilvaLinkToolBox.prototype.initialize = function(tool, editor) {
    this.tool = tool;
    this.editor = editor;
    addEventHandler(
        this.targetselect, 'change', this.selectTargetHandler, this);
    addEventHandler(
        this.targetinput, 'change', this.selectTargetHandler, this);
    addEventHandler(this.addbutton, 'click', this.createLinkHandler, this);
    addEventHandler(this.updatebutton, 'click', this.createLinkHandler, this);
    addEventHandler(this.delbutton, 'click', this.tool.deleteLink, this);
    addEventHandler(this.input, 'focus', this.inputFocusHandler, this);
    addEventHandler(this.inputTA, 'blur', this.inputFocusHandler, this);
    this.targetinput.style.display = 'none';
    this.editor.logMessage('Link tool initialized');
};


SilvaLinkToolBox.prototype.inputFocusHandler = function(event) {
    if (this.input.style.display == 'none') {
        this.input.value = this.inputTA.value;
        this.input.style.display = 'inline';
        this.inputTA.style.display = 'none';
    } else {
        this.input.style.display = 'none';
        this.inputTA.value = this.input.value;
        this.inputTA.style.display = 'inline';
        this.inputTA.focus();
    };
};

SilvaLinkToolBox.prototype.selectTargetHandler = function(event) {
    var select = this.targetselect;
    var input = this.targetinput;

    var selvalue = select.options[select.selectedIndex].value;
    if (selvalue != 'input') {
        input.style.display = 'none';
    } else {
        input.style.display = 'inline';
    };
};

SilvaLinkToolBox.prototype.createLinkHandler = function(event) {
    var url = this.input.value;
    var target = this.targetselect.options[
        this.targetselect.selectedIndex].value;
    if (target == 'input') {
        target = this.targetinput.value;
    };
    this.tool.createLink(url, 'link', null, target);
    this.editor.content_changed = true;
    this.editor.updateState();
};

SilvaLinkToolBox.prototype.updateState = function(selNode, event) {
    if (this.editor.getTool('extsourcetool').getNearestExternalSource(selNode)) {
        return;
    }
    var currnode = selNode;
    var link = false;
    var href = '';
    while (currnode) {
        if (currnode.nodeName == 'A') {
            href = currnode.getAttribute('silva_href');
            if (!href) {
                href = currnode.getAttribute('href');
            };
            if (href) {
                if (this.toolboxel) {
                    this.toolboxel.className = this.activeclass;
                    if (this.toolboxel.open_handler) {
                        this.toolboxel.open_handler();
                    };
                };
                this.input.value = href;
                this.inputTA.value = href;
                this.inputeditbutton.style.display="inline";
                this.inputeditbutton.parentNode.style.width="42px";
                var target = currnode.getAttribute('target');
                if (!target) {
                    this.targetselect.selectedIndex = 0;
                    this.targetinput.style.display = 'none';
                } else {
                    var target_found = false;
                    for (var i=0; i < this.targetselect.options.length; i++) {
                        var option = this.targetselect.options[i];
                        if (option.value == target) {
                            this.targetselect.selectedIndex = i;
                            target_found = true;
                            break;
                        };
                    };
                    if (target_found) {
                        this.targetinput.value = '';
                        this.targetinput.style.display = 'none';
                    } else {
                        // XXX this is pretty hard-coded...
                        this.targetselect.selectedIndex = 
                            this.targetselect.options.length - 1;
                        this.targetinput.value = target;
                        this.targetinput.style.display = 'inline';
                    };
                };
                this.addbutton.style.display = 'none';
                this.updatebutton.style.display = 'inline';
                this.delbutton.style.display = 'inline';
                return;
            };
        };
        currnode = currnode.parentNode;
    };
    this.targetselect.selectedIndex = 0;
    this.targetinput.value = '';
    this.targetinput.style.display = 'none';
    this.updatebutton.style.display = 'none';
    this.delbutton.style.display = 'none';
    this.addbutton.style.display = 'inline';
    if (this.toolboxel) {
        this.toolboxel.className = this.plainclass;
    };
    this.input.value = '';
    this.inputTA.value = '';
    this.inputeditbutton.style.display="none";
    this.inputeditbutton.parentNode.style.width="21px";
};

function SilvaImageTool(
    editelid, urlinputid, targetselectid, targetinputid, hireslinkcheckboxid,
    linkinputid, alignselectid, titleinputid, toolboxid, plainclass,
    activeclass, linktocontainerid, resizebuttonid, addbuttonid) {
    /* Silva specific image tool */
    this.editel = getFromSelector(editelid);
    this.urlinput = getFromSelector(urlinputid);
    var urltable = this.urlinput.parentNode.parentNode;
    this.urlinputeditbutton = urltable.getElementsByTagName('button')[1];
    this.targetselect = getFromSelector(targetselectid);
    this.targetinput = getFromSelector(targetinputid);
    this.hireslinkcheckbox = getFromSelector(hireslinkcheckboxid);
    this.linkinput = getFromSelector(linkinputid);
    var linktable = this.linkinput.parentNode.parentNode;
    this.linkinputeditbutton = linktable.getElementsByTagName('button')[1];
    this.alignselect = getFromSelector(alignselectid);
    this.titleinput = getFromSelector(titleinputid);
    this.toolboxel = getFromSelector(toolboxid);
    this.linktocontainer = getFromSelector(linktocontainerid);
    this.resizebutton = getFromSelector(resizebuttonid);
    this.plainclass = plainclass;
    this.activeclass = activeclass;
    this.resizePollingInterval = null;
    this.addbutton = getFromSelector(addbuttonid);
};

SilvaImageTool.prototype = new ImageTool;

SilvaImageTool.prototype.initialize = function(editor) {
    this.editor = editor;
    addEventHandler(this.targetselect, 'change', this.setTarget, this);
    addEventHandler(
        this.targetselect, 'change', this.selectTargetHandler, this);
    addEventHandler(this.targetinput, 'change', this.setTarget, this);
    addEventHandler(this.urlinput, 'change', this.setSrc, this);
    addEventHandler(this.hireslinkcheckbox, 'change', this.setHires, this);
    addEventHandler(this.linkinput, 'change', this.setLink, this);
    addEventHandler(this.alignselect, 'change', this.setAlign, this);
    addEventHandler(this.titleinput, 'change', this.setTitle, this);
    addEventHandler(
        this.resizebutton, 'click', this.finalizeResizeImage, this);
    this.targetinput.style.display = 'none';
    this.resizebutton.style.display = 'none';
    this.editor.logMessage('Image tool initialized');
    /* this edit button cell is actually always displayed, as the
       urlinput will always be filled in if it is visible */
    this.urlinputeditbutton.style.display='inline';
    this.urlinputeditbutton.parentNode.style.width='42px';
};

SilvaImageTool.prototype.createContextMenuElements = function(selNode, event) {
    return new Array(new ContextMenuElement('Create image', getImage, this));
};

SilvaImageTool.prototype.selectTargetHandler = function(event) {
    var select = this.targetselect;
    var input = this.targetinput;

    var selvalue = select.options[select.selectedIndex].value;
    if (selvalue != 'input') {
        input.style.display = 'none';
    } else {
        input.style.display = 'inline';
    };
};

SilvaImageTool.prototype.updateState = function(selNode, event) {
    if (this.editor.getTool('extsourcetool').getNearestExternalSource(selNode)) {
        return;
    }
    var image = this.editor.getNearestParentOfType(selNode, 'img');
    if (image) {
         /* the rest of the image tool was originally designed to 
            getNearestparentOfType(img), but the 'confirm resizing'
            feature needs to know what image was active, after is it
            no longer selected.  So store it as a property of the image
            tool */
        this.image = image;
        this.editel.style.display = 'block';
        this.addbutton.style.display = 'none';
        var src = image.getAttribute('silva_src');
        if (!src) {
            src = image.getAttribute('src');
        };
        this.urlinput.value = src;
        var target = image.getAttribute('target');
        if (!target) {
            this.targetselect.selectedIndex = 0;
            this.targetinput.style.display = 'none';
        } else {
            var target_found = false;
            for (var i=0; i < this.targetselect.options.length; i++) {
                var option = this.targetselect.options[i];
                if (option.value == target) {
                    this.targetselect.selectedIndex = i;
                    target_found = true;
                    break;
                };
            };
            if (target_found) {
                this.targetinput.value = '';
                this.targetinput.style.display = 'none';
            } else {
                this.targetselect.selectedIndex =
                    this.targetselect.options.length - 1;
                this.targetinput.value = target;
                this.targetinput.style.display = 'inline';
            };
        };
        var hires = image.getAttribute('link_to_hires') == '1';
        if (!hires) {
            var link = image.getAttribute('link');
            this.hireslinkcheckbox.checked = false;
            this.linkinput.value = link == null ? '' : link;
            this.linkinputeditbutton.style.display = !link ? 'none' : 'inline';
            this.linkinputeditbutton.parentNode.style.width =
                !link ? '21px' : '42px';
        } else {
            this.hireslinkcheckbox.checked = 'checked';
            this.linktocontainer.style.display = 'none';
            this.linkinput.value = '';
            this.linkinput.disabled = 'disabled';
            this.linkinputeditbutton.style.display = 'none';
            this.linkinputeditbutton.parentNode.style.width = '21px';
        };
        if (this.toolboxel) {
            if (this.toolboxel.open_handler) {
                this.toolboxel.open_handler();
            };
            this.toolboxel.className = this.activeclass;
        };
        var align = image.getAttribute('alignment');
        if (!align) {
            align = 'left';
        };
        var title = image.getAttribute('title');
        if (!title) {
            title = '';
        };
        this.titleinput.value = title;
        selectSelectItem(this.alignselect, align);
        this.startResizePolling(image);
    } else {
        this.addbutton.style.display = 'inline';
        this.editel.style.display = 'none';
        this.urlinput.value = '';
        this.titleinput.value = '';
        if (this.toolboxel) {
            this.toolboxel.className = this.plainclass;
        };
        this.targetselect.selectedIndex = 0;
        this.targetinput.value = '';
        this.targetinput.style.display = 'none';
        if (this.resizebutton.style.display != 'none' && this.image) {
            /* image has been resized, so prompt user to
               confirm resizing */
            if (confirm(
                "Image has been resized in kupu, but not confirmed. " +
                "Really resize?")) {
              this.finalizeResizeImage();
            };
        };
        this.stopResizePolling();
        this.image = null;
        this.resizebutton.style.display='none';
    };
};

SilvaImageTool.prototype.finalizeResizeImage = function() {
    this.stopResizePolling(); /* pause polling during resize */ 
    var image = this.image;
    if (!image) {
        this.editor.logMessage('No image selected!  unable to resize');
        return;
    };
    var width = image.style.width.replace(/px/,'');
    var height = image.style.height.replace(/px/,'');

    var _finalizeResizeImageCallback = function(object, image, width, height) {
        if (request.readyState == 4) {
            if (request.status != '200') {
                if (request.status == '500') {
                    alert('error on server.  body returned:\n' +
                          request.responseText);
                };
            };
            var finish = function(object) {
                /* The width/height styles (style attribute) cannot be removed
                   immediately after repointing the src to the resized image,
                   or the screen will flicker, so do it onload */
                image.onload = "this.removeAttribute('style')";
                image.src = tmpimg.src;
                object.editor.content_changed = true;
                object.resizebutton.style.display='none';
                object.editor.updateState();
                object.editor.focusDocument();
            };
            var tmpimg = new Image();
            addEventHandler(tmpimg, 'load', finish, this, object);
            /* add the dimensions on to the src url, to bypass browser
               caching.  This is OK, because every image (even newly created
               ones) have a silva_src attribute, which is used when saving */
            tmpimg.src = image.src.replace(/\?.*/,'') + '?'+width+'x'+height;
        };
    };
    var url =
        image.src.replace(/\?.*/,'') +
        '/@@resize_image_from_kupu?width=' + width + '&height=' + height;
    var request = new XMLHttpRequest();
    request.open('GET',url, true);
    var callback = new ContextFixer(
        _finalizeResizeImageCallback, request, this, image, width, height);
    request.onreadystatechange = callback.execute;
    request.send(null);
    this.startResizePolling(image);
};

SilvaImageTool.prototype.startResizePolling = function(image) {
    if (this.resizePollingInterval) return;
    var image_style = [image.style.width, image.style.height];
    var self = this;
    function polling() {
        var newstyle = [image.style.width, image.style.height];
        if (!(image_style[0]==newstyle[0] && image_style[1]==newstyle[1])) {
            self.resizebutton.style.display='inline';
            image_style = newstyle;
        };
    };
    this.resizePollingInterval = setInterval(polling, 300);
};

SilvaImageTool.prototype.stopResizePolling = function() {
    clearInterval(this.resizePollingInterval);
    this.resizePollingInterval = null;
};

SilvaImageTool.prototype.createImage = function(url, alttext, imgclass) {
    /* create an image */
    var img = this.editor.getInnerDocument().createElement('img');
    img.src = url;
    img.setAttribute('silva_src', url);
    img.removeAttribute('height');
    img.removeAttribute('width');
    if (alttext) {
        img.alt = alttext;
    };
    if (imgclass) {
        img.className = imgclass;
    };
    img = this.editor.insertNodeAtSelection(img, 1);
    this.editor.logMessage(_('Image inserted'));
    this.editor.content_changed = true;
    this.editor.updateState();
    return img;
};

SilvaImageTool.prototype.setTarget = function() {
    var target = this.targetselect.options[
        this.targetselect.selectedIndex].value;
    if (target == 'input') {
        target = this.targetinput.value;
    };
    var selNode = this.editor.getSelectedNode();
    var image = this.editor.getNearestParentOfType(selNode, 'img');
    if (!image) {
        this.editor.logMessage('No image selected!', 1);
    };
    image.setAttribute('target', target);
    this.editor.content_changed = true;
};

SilvaImageTool.prototype.setSrc = function() {
    var selNode = this.editor.getSelectedNode();
    var img = this.editor.getNearestParentOfType(selNode, 'img');
    if (!img) {
        this.editor.logMessage('Not inside an image!', 1);
    };

    var src = this.urlinput.value;
    img.setAttribute('src', src);
    img.setAttribute('silva_src', src);
    this.editor.content_changed = true;
    this.editor.logMessage('Image updated');
};

SilvaImageTool.prototype.setHires = function() {
    var selNode = this.editor.getSelectedNode();
    var image = this.editor.getNearestParentOfType(selNode, 'img');
    if (!image) {
        this.editor.logMessage('No image selected!', 1);
        return;
    };
    if (this.hireslinkcheckbox.checked) {
        image.setAttribute('link_to_hires', '1');
        image.removeAttribute('link');
        this.linkinput.value = '';
        this.linkinput.disabled = 'disabled';
        this.linkinputeditbutton.style.display = 'none';
        this.linkinputeditbutton.parentNode.style.width = '21px';
        this.linktocontainer.style.display = 'none';
    } else {
        image.setAttribute('link_to_hires', '0');
        image.setAttribute('link', this.linkinput.value);
        this.linkinput.disabled = false;
        this.linktocontainer.style.display = 'block';
    };
    this.editor.content_changed = true;
};

SilvaImageTool.prototype.setLink = function() {
    var link = this.linkinput.value;
    var selNode = this.editor.getSelectedNode();
    var image = this.editor.getNearestParentOfType(selNode, 'img');
    if (!image) {
        this.editor.logMessage('No image selected!', 1);
        return;
    };
    image.setAttribute('link', link);
    image.setAttribute('link_to_hires', '0');
    this.linkinputeditbutton.style.display = !link ? 'none' : 'inline';
    this.linkinputeditbutton.parentNode.style.width = !link ? '21px' : '42px';
    this.editor.content_changed = true;
};

SilvaImageTool.prototype.setTitle = function() {
    var selNode = this.editor.getSelectedNode();
    var image = this.editor.getNearestParentOfType(selNode, 'img');
    if (!image) {
        this.editor.logMessage('No image selected!', 1);
        return;
    };
    var title = this.titleinput.value;
    image.setAttribute('title', title);
    this.editor.content_changed = true;
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
        this._addRowHelper(doc, tbody, 'th', -1, cols);
    };

    for (var i=0; i < rows; i++) {
        this._addRowHelper(doc, tbody, 'td', -1, cols);
    };

    table.appendChild(tbody);

    // call the _getColumnInfo() method, this will generate the colinfo on the
    // table
    this._getColumnInfo(table);

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

SilvaTableTool.prototype.addTableRow = function() {
    /* add a table row or header */
    var currnode = this.editor.getSelectedNode();
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

SilvaTableTool.prototype.delTableRow = function() {
    /* delete a table row or header */
    var currnode = this.editor.getSelectedNode();
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
       var currCell = this.editor.getNearestParentOfType(currNode,'th');
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

    table.removeAttribute('silva_column_info');
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
        var currcell = this.editor.getNearestParentOfType(currnode, 'th');
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
    
    table.removeAttribute('silva_column_info');
    this._getColumnInfo();
    widthinput.value = this.getColumnWidths(table);
    this.editor.content_changed = true;
    this.editor.logMessage('cell removed');
};

SilvaTableTool.prototype.addTableColumn = function(widthinput) {
    /* add a table column */
    var currnode = this.editor.getSelectedNode();
    var doc = this.editor.getInnerDocument();
    var table = this.editor.getNearestParentOfType(currnode, 'table');
    if (!table) {
        this.editor.logMessage('Not inside a table!');
        return;
    };
    var body = table.getElementsByTagName('tbody')[0];
    var currcell = this.editor.getNearestParentOfType(currnode, 'td');
    if (!currcell) {
        var currcell = this.editor.getNearestParentOfType(currnode, 'th');
        if (!currcell) {
            this.editor.logMessage('Not inside a row!', 1);
            return;
        } else {
            var index = -1;
        };
    } else {
        var index = this._getColIndex(currcell) + 1;
    };
    var numcells = this._countColumns(body);
    this._addColHelper(doc, body, index, numcells);
    table.removeAttribute('silva_column_info');
    this._getColumnInfo();

    widthinput.value = this.getColumnWidths(table);
    this.editor.content_changed = true;
    this.editor.logMessage('Column added');
};

SilvaTableTool.prototype.delTableColumn = function(widthinput) {
    /* delete a column */
    var currnode = this.editor.getSelectedNode();
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
        var index = -1;
    } else {
        var index = this._getColIndex(currcell);
    };

    this._delColHelper(body, index);
    table.removeAttribute('silva_column_info');
    this._getColumnInfo();

    widthinput.value = this.getColumnWidths(table);
    this.editor.content_changed = true;
    this.editor.logMessage('Column deleted');
};

SilvaTableTool.prototype.setColumnWidths = function(widths) {
    /* sets relative column widths */
    var selNode = this.editor.getSelectedNode();
    var table = this.editor.getNearestParentOfType(selNode, 'table');

    if (!table) {
        this.editor.logMessage('not a table');
        return;
    };

    var silva_column_info = this._getColumnInfo(table);
    widths = widths.split(',');
    if (widths.length != silva_column_info.length) {
        alert('number of widths doesn\'t match number of columns!');
        return;
    };
    for (var i=0; i < widths.length; i++) {
        silva_column_info[i][1] = widths[i];
    };
    this._setColumnInfo(table, silva_column_info);
    this._updateTableFromInfo(table);
    this.editor.content_changed = true;
    this.editor.logMessage('table column widths adjusted');
};

SilvaTableTool.prototype.getColumnWidths = function(table) {
    var silvacolinfo = table.getAttribute('silva_column_info');
    var widths = new Array();
    silvacolinfo = silvacolinfo.split(' ');
    for (var i=0; i < silvacolinfo.length; i++) {
        var pair = silvacolinfo[i].split(':');
        if (pair[1] == '*') {
            widths.push('*');
        } else {
            widths.push(parseInt(pair[1]));
        };
    };
    widths = this._factorWidths(widths);
    return widths;
};

SilvaTableTool.prototype.setColumnAlign = function(align) {
    var currnode = this.editor.getSelectedNode();
    var currtd = this.editor.getNearestParentOfType(currnode, 'td');
    if (!currtd) {
        var currtd = this.editor.getNearestParentOfType(currnode, 'th');
    }
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
    var infos = this._getColumnInfo();
    infos[index][0] = align;
    var table = this.editor.getNearestParentOfType(currnode, 'table');
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
        doc, body, celltype, index, numcells) {
    /* actually adds a row to the table */
    var row = doc.createElement('tr');

    // fill the row with cells
    if (celltype == 'td') {
        for (var i=0; i < numcells; i++) {
            var cell = doc.createElement(celltype);
            cell.appendChild(doc.createTextNode("\u00a0"));
            row.appendChild(cell);
        };
    } else if (celltype == 'th') {
        var cell = doc.createElement(celltype);
        cell.setAttribute('colSpan', numcells);
        cell.appendChild(doc.createTextNode("\u00a0"));
        row.appendChild(cell);
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

SilvaTableTool.prototype._addColHelper = function(doc, body, index, numcells) {
    /* actually adds a column to a table */
    var rows = this._getAllRows(body);
    var numcols = this._countColumns(body)
    for (var i=0; i < rows.length; i++) {
        var row = rows[i];
        var cols = this._getAllColumns(row);
        var col = cols[0];
	/* a table header row is a row with only one cell, that is a TH
	   in a table that has more than one column */
        if (col.nodeName == 'TH' && numcols > 1 && cols.length == 1) {
            var colspan = col.getAttribute('colspan');
	    colspan = colspan ? parseInt(colspan) : 1;
            col.setAttribute('colspan', colspan + 1);
        } else {
            var cell = doc.createElement(cols[0].nodeName);
            cell.appendChild(doc.createTextNode('\u00a0'));
            if (index == -1 || index >= rows.length) {
                row.appendChild(cell);
            } else {
                row.insertBefore(cell, cols[index]);
            };
        };
    };
    var table = body.parentNode;
    table.removeAttribute('silva_column_info');
    this._getColumnInfo();
};

SilvaTableTool.prototype._delColHelper = function(body, index) {
    /* actually delete all cells in a column */
    /* needs to be smarter when deleting rows containing th's */
    var rows = this._getAllRows(body);
    var numcols = this._countColumns(body);
    for (var i=0; i < rows.length; i++) {
        var row = rows[i];
        var cols = this._getAllColumns(row);
        if (cols[0].nodeName == 'TH' && numcols >=1 && cols.length == 1) {
            // is a table header, so reduce colspan
            var th = cols[0];
            var colspan = th.getAttribute('colSpan');
            if (!colspan || colspan == '1') {
                body.removeChild(row);
            } else {
                colspan = parseInt(colspan);
                th.setAttribute('colSpan', colspan - 1);
            };
        } else {
            // is a table cell row, remove one
            if (index > -1) {
		if (cols[index]) 
                    row.removeChild(cols[index]);
            } else {
		if (cols[cols.length - 1])
                    row.removeChild(cols[cols.length - 1]);
            };
        };
    };
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
    /* get the current column count */
    /* count all cells from all rows, ignoring colspans since they
       may be inaccurate, and take the row with the highest number
       of cells */
    var numcols = 0;
    var rows = this._getAllRows(body);
    for (var i=0; i < rows.length; i++) {
	var rowcols = 0;
	var cols = this._getAllColumns(rows[i]);
	for (var j=0; j < cols.length; j++) {
	    rowcols++;
	}
	if (rowcols > numcols) numcols = rowcols;
    }
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
        if (node.nodeName.search(/TD|TH/) > -1) {
            cols.push(node);
        };
    };
    return cols;
};

SilvaTableTool.prototype._getColumnInfo = function(table) {
    var mapping = {'C': 'center', 'L': 'left', 'R': 'right'};
    var revmapping = {'center': 'C', 'left': 'L', 'right': 'R'};
    if (!table) {
        var selNode = this.editor.getSelectedNode();
        var table = this.editor.getNearestParentOfType(selNode, 'table');
    };
    if (!table) {
        return;
    };
    var silvacolinfo = table.getAttribute('silva_column_info');
    if (silvacolinfo) {
        var infos = silvacolinfo.split(' ');
        var ret = [];
        for (var i=0; i < infos.length; i++) {
            var tup = infos[i].split(':');
            tup[0] = mapping[tup[0]];
            ret.push(tup);
        };
        return ret;
    } else {
        var body = null;
        var iterator = new NodeIterator(table);
        var body = iterator.next();
        while (body.nodeName != 'TBODY') body = iterator.next();
        var rows = this._getAllRows(body);
	var numcols = this._countColumns(body);
        var ret = [];
        var colinfo = []; // to use as the table attribute later on
        for (var i=0; i < rows.length; i++) {
            var cols = this._getAllColumns(rows[i]);
	    /* to make sure this isn't a "row header" */
	    if (cols.length == 1 && numcols == 1 && cols[0].nodeName == 'TH')
		continue;
            for (var j=0; j < cols.length; j++) {
                var tup = ['left'];
                var className = cols[j].className;
                if (className.indexOf('align-') == 0) {
                    tup[0] = className.substr(6);
                };
                var width = cols[j].getAttribute('width');
                tup[1] = !width ? 1 : parseInt(width);
                colinfo[j] = revmapping[tup[0]] + ':' + tup[1];
                ret[j] = tup;
    		var colspan = cols[j].getAttribute('colspan')
            };
	    /* if this row contained every column, break out of loop */
	    if (cols.length == numcols)
	        break;		
        };
        table.setAttribute('silva_column_info', colinfo.join(' '));
        return ret;
    };
};

SilvaTableTool.prototype._setColumnInfo = function(table, info) {
    var mapping = {'center': 'C', 'left': 'L', 'right': 'R'};
    var str = [];
    for (var i=0; i < info.length; i++) {
        str.push(mapping[info[i][0]] + ':' + info[i][1]);
    };
    table.setAttribute('silva_column_info', str.join(' '));
};

SilvaTableTool.prototype._updateTableFromInfo = function(table) {
/* XXX do not skip over any cells, I think */
    var colinfo = this._getColumnInfo(table);

    // convert the relative widths to percentages first
    var totalunits = 0;
    for (var i=0; i < colinfo.length; i++) {
        if (colinfo[i][1] == '*') {
            totalunits += 1;
        } else {
            totalunits += parseInt(colinfo[i][1]);
        };
    };

    var percent_per_unit = 100.0 / totalunits;

    // find the rows containing cells
    var rows = this._getAllRows(table.getElementsByTagName('tbody')[0]);
    for (var i=0; i < rows.length; i++) {
        var cols = this._getAllColumns(rows[i]);
        if (cols[0].nodeName == 'TH') {
            continue;
        };
        for (var j=0; j < cols.length; j++) {
            var align = colinfo[j][0];
            cols[j].className = 'align-' + align;
            var width = colinfo[j][1];
            if (width != '*') {
                cols[j].setAttribute('width', '' + 
                    (width * percent_per_unit) + '%');
            } else {
                cols[j].removeAttribute('width');
            };
        };
    };
};

function SilvaTableToolBox(addtabledivid, edittabledivid, newrowsinputid, 
    newcolsinputid, makeheaderinputid, classselectid, 
    alignselectid, widthinputid, addtablebuttonid, 
    addrowbuttonid, delrowbuttonid, addcolbuttonid, 
    delcolbuttonid, fixbuttonid, delbuttonid, toolboxid, 
    plainclass, activeclass, celltypeid, cellcolspanid,
    addcellafterid, addcellbeforeid, delcellid) {
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
    this.fixbutton = getFromSelector(fixbuttonid);
    this.delbutton = getFromSelector(delbuttonid);
    this.toolboxel = getFromSelector(toolboxid);
    this.celltypesel = getFromSelector(celltypeid);
    this.cellcolspaninput = getFromSelector(cellcolspanid);
    this.addcellafterbutton = getFromSelector(addcellafterid);
    this.addcellbeforebutton = getFromSelector(addcellbeforeid);
    this.delcellbutton = getFromSelector(delcellid);
    this.plainclass = plainclass;
    this.activeclass = activeclass;
};

SilvaTableToolBox.prototype = new TableToolBox;

SilvaTableToolBox.prototype.initialize = function(tool, editor) {
    /* attach the event handlers */
    this.tool = tool;
    this.editor = editor;
    addEventHandler(this.addtablebutton, "click", this.addTable, this);
    addEventHandler(
        this.addrowbutton, "click", this.tool.addTableRow, this.tool);
    addEventHandler(
        this.delrowbutton, "click", this.tool.delTableRow, this.tool);
    addEventHandler(this.addcolbutton, "click", this.addTableColumn, this);
    addEventHandler(this.delcolbutton, "click", this.delTableColumn, this);
    addEventHandler(this.fixbutton, "click", this.fixTable, this);
    addEventHandler(this.delbutton, "click", this.delTable, this);
    addEventHandler(this.alignselect, "change", this.setColumnAlign, this);
    addEventHandler(this.classselect, "change", this.setTableClass, this);
    addEventHandler(this.widthinput, "change", this.setColumnWidths, this);
    addEventHandler(this.celltypesel, "change", this.changeCellType, this);
    addEventHandler(this.cellcolspaninput, "change", this.changeCellColspan, this);
    addEventHandler(this.addcellafterbutton, "click", this.addCell, this);
    addEventHandler(this.addcellbeforebutton, "click", this.addCell, this);
    addEventHandler(this.delcellbutton, "click", this.delCell, this);
    this.edittablediv.style.display = "none";
    this.editor.logMessage('Table tool initialized');
};

SilvaTableToolBox.prototype.delTable = function() {
    this.tool.delTable();
    this.editor.getDocument().getWindow().focus();
    this.editor.updateState();
}


SilvaTableToolBox.prototype.updateState = function(selNode) {
    if (this.editor.getTool('extsourcetool').getNearestExternalSource(selNode)) {
        return;
    }
    /* update the state (add/edit) and update the pulldowns (if required) */
    var table = this.editor.getNearestParentOfType(selNode, 'table');
    if (table) {
        this.addtablediv.style.display = "none";
        this.edittablediv.style.display = "block";
        var td = this.editor.getNearestParentOfType(selNode, 'td');
        if (!td) {
            td = this.editor.getNearestParentOfType(selNode, 'th');
        }

	if (td) {
            var align = td.className.split('-')[1];
            if (align == 'center' || align == 'left' || align == 'right') {
		selectSelectItem(this.alignselect, align);
            };
    	    /* XXX setup the tc type switching */
    	    selectSelectItem(this.celltypesel, td.nodeName.toLowerCase());
	    if (td.nodeName=='TH') {
		var len = td.parentNode.getElementsByTagName('th').length + td.parentNode.getElementsByTagName('td').length
		if (len == 1) { /* a single TH is a silva table row_heading */
		    this.widthinput.value = '';
		} else {
		    this.widthinput.value = this.tool.getColumnWidths(table);
		}
	    } else {
                this.widthinput.value = this.tool.getColumnWidths(table);
	    }
	    this.cellcolspaninput.value = td.getAttribute('colspan');
        };
        selectSelectItem(this.classselect, table.className);
        if (this.toolboxel) {
            if (this.toolboxel.open_handler) {
                this.toolboxel.open_handler();
            };
            this.toolboxel.className = this.activeclass;
        };
    } else {
        this.edittablediv.style.display = "none";
        this.addtablediv.style.display = "block";
        this.alignselect.selectedIndex = 0;
        this.classselect.selectedIndex = 0;
        if (this.toolboxel) {
            this.toolboxel.className = this.plainclass;
        };
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
    this.tool.changeCellType(this.celltypesel.options[this.celltypesel.selectedIndex].value);
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.changeCellColspan = function() {
    this.tool.changeCellColspan(this.cellcolspaninput.value);
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.delTableColumn = function() {
    this.tool.delTableColumn(this.widthinput);
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.addTableColumn = function() {
    this.tool.addTableColumn(this.widthinput);
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.delCell = function(event) {
    this.tool.removeCell(this.widthinput);
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.addCell = function(event) {
    var target = event.srcElement ? event.srcElement : event.target;
    //first param is a boolean, if true then cell is added before active cell
    // otherwise it is added after
    this.tool.addCell(target.value.search(/before/)>-1, this.widthinput);
    this.editor.getDocument().getWindow().focus();
};

SilvaTableToolBox.prototype.setColumnWidths = function() {
    var widths = this.widthinput.value;
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
		numcells = row.getElementsByTagName('td').length + row.getElementsByTagName('th').length;
		if (numcells==1) {
                    newrow.appendChild(node);
                    node.setAttribute('colspan', '1');
                    node.setAttribute('rowspan', '1');
		    continue
                }
            } else if (node.nodeName != 'TD') {
                row.removeChild(node);
                continue;
            };
            node.setAttribute('rowspan', '1');
	    if (!node.hasAttribute('colspan'))
                node.setAttribute('colspan', '1');
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
    
    /* now fix table widths if numcols is incorrect, e.g.
       the add column handlebar was clicked at least once */
    table.removeAttribute('silva_column_info');
    this.tool._getColumnInfo();
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
    this.toolboxel = getFromSelector(toolboxid);
    this.plainclass = plainclass;
    this.activeclass = activeclass;
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

SilvaIndexTool.prototype.updateState = function(selNode, event) {
    if (this.editor.getTool('extsourcetool').getNearestExternalSource(selNode)) {
        return;
    }
    var indexel = this.editor.getNearestParentOfType(selNode, 'A');
    if (indexel && !indexel.getAttribute('href')) {
        if (this.toolboxel) {
            if (this.toolboxel.open_handler) {
                this.toolboxel.open_handler();
            };
            this.toolboxel.className = this.activeclass;
        };
        this.nameinput.value = indexel.getAttribute('name');
        this.titleinput.value = indexel.getAttribute('title');
        this.addbutton.style.display = 'none';
        this.updatebutton.style.display = 'inline';
        this.deletebutton.style.display = 'inline';
    } else {
        if (this.toolboxel) {
            this.toolboxel.className = this.plainclass;
        };
        this.nameinput.value = '';
        this.titleinput.value = '';
        this.updatebutton.style.display = 'none';
        this.deletebutton.style.display = 'none';
        this.addbutton.style.display = 'inline';
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

function SilvaTocTool(
        depthselectid, delbuttonid, toolboxid, plainclass, activeclass) {
    this.depthselect = getFromSelector(depthselectid);
    this.delbutton = getFromSelector(delbuttonid);
    this.toolbox = getFromSelector(toolboxid);
    this.plainclass = plainclass;
    this.activeclass = activeclass;
    this._inside_toc = false;
};

SilvaTocTool.prototype = new KupuTool;

SilvaTocTool.prototype.initialize = function(editor) {
    this.editor = editor;
    addEventHandler(this.depthselect, 'change', this.updateToc, this);
    addEventHandler(this.delbutton, 'click', this.deleteToc, this);
    addEventHandler(
        editor.getInnerDocument(), 'keypress', this.handleKeyPressOnToc, this);
    this.depthselect.style.display = "none";
    this.delbutton.style.display = "none";
    if (this.editor.getBrowserName() == 'IE') {
        addEventHandler(
            editor.getInnerDocument(), 'keydown', this.handleKeyPressOnToc,
            this);
        addEventHandler(
            editor.getInnerDocument(), 'keyup', this.handleKeyPressOnToc,
            this);
    };
};

SilvaTocTool.prototype.handleKeyPressOnToc = function(event) {
    if (!this._inside_toc) {
        return;
    };
    var keyCode = event.keyCode;
    if (keyCode == 8 || keyCode == 46) {
        var selNode = this.editor.getSelectedNode();
        var toc = this.getNearestToc(selNode);
        toc.parentNode.removeChild(toc);
    };
    if (keyCode == 13 || keyCode == 9 || keyCode == 39) {
        var selNode = this.editor.getSelectedNode();
        var toc = this.getNearestToc(selNode);
        var doc = this.editor.getInnerDocument();
        var selection = this.editor.getSelection();
        if (toc.nextSibling) {
            var sibling = toc.nextSibling;
            selection.selectNodeContents(toc.nextSibling);
            selection.collapse();
        } else {
            var parent = toc.parentNode;
            var p = doc.createElement('p');
            parent.appendChild(p);
            var text = doc.createTextNode('\xa0');
            p.appendChild(text);
            selection.selectNodeContents(p);
        };
        this._inside_toc = false;
    };
    if (event.preventDefault) {
        event.preventDefault();
    } else {
        event.returnValue = false;
    };
};

SilvaTocTool.prototype.updateState = function(selNode, event) {
    if (this.editor.getTool('extsourcetool').getNearestExternalSource(selNode)) {
        return;
    }
    var toc = this.getNearestToc(selNode);
    if (toc) {
        var depth = toc.getAttribute('toc_depth');
        selectSelectItem(this.depthselect, depth);
        this.depthselect.style.display = 'inline';
        this.delbutton.style.display = 'inline';
        this._inside_toc = true;
        if (this.toolbox) {
            if (this.toolbox.open_handler) {
                this.toolbox.open_handler();
            };
            this.toolbox.className = this.activeclass;
        };
    } else {
        this.depthselect.style.display = 'none';
        this.depthselect.selectedIndex = 0;
        this.delbutton.style.display = 'none';
        this._inside_toc = false;
        if (this.toolbox) {
            this.toolbox.className = this.plainclass;
        };
    };
};

SilvaTocTool.prototype.addOrUpdateToc = function(event, depth) {
    var selNode = this.editor.getSelectedNode();
    var depth = depth ? depth : this.depthselect.options[
        this.depthselect.selectedIndex].value;
    var toc = this.getNearestToc(selNode);
    var doc = this.editor.getInnerDocument();
    var toctext = this.getTocText(depth);
    if (toc) {
        // there's already a toc, just update the depth
        toc.setAttribute('toc_depth', depth);
        while (toc.hasChildNodes()) {
            toc.removeChild(toc.firstChild);
        };
        toc.appendChild(doc.createTextNode(toctext));
    } else {
        /* no more new tocs, toc should now be created via the TOC
            external source */
        alert(
            _("The TOC element has been deprecated and will be removed in a " +
              "later release of Silva.  Use the TOC external source to add " +
              "a 'Table of Contents' element to this document"));
        /*// create a new toc
            var div = doc.createElement('div');
            div.setAttribute('toc_depth', depth);
            div.setAttribute('is_toc', 1);
            div.className = 'toc';
            var text = doc.createTextNode(toctext);
            div.appendChild(text);
            this.editor.insertNodeAtSelection(div);*/
    };
    this.editor.content_changed = true;
};

SilvaTocTool.prototype.createDefaultToc = function() {
    // XXX nasty workaround, entering null as the event...
    this.addOrUpdateToc(null, '-1');
};

SilvaTocTool.prototype.updateToc = function() {
    var selNode = this.editor.getSelectedNode();
    var toc = this.getNearestToc(selNode);
    if (toc) {
        var depth = this.depthselect.options[
            this.depthselect.selectedIndex].value;
        var toctext = this.getTocText(depth);
        toc.setAttribute('toc_depth', depth);
        while (toc.hasChildNodes()) {
            toc.removeChild(toc.firstChild);
        };
        doc = this.editor.getInnerDocument();
        toc.appendChild(doc.createTextNode(toctext));
    };
    this.editor.content_changed = true;
};

SilvaTocTool.prototype.deleteToc = function() {
    var selNode = this.editor.getSelectedNode();
    var toc = this.getNearestToc(selNode);
    if (!toc) {
        this.editor.logMessage('Not inside a toc!', 1);
        return;
    };
    toc.parentNode.removeChild(toc);
    this.editor.content_changed = true;
    this.depthselect.style.display = "none";
    this.delbutton.style.display = "none";
};

SilvaTocTool.prototype.getNearestToc = function(selNode) {
    var currnode = selNode;
    while (currnode) {
        if (currnode.nodeName.toLowerCase() == 'div' &&
                currnode.getAttribute('is_toc')) {
            return currnode;
        };
        currnode = currnode.parentNode;
    };
    return false;
};

SilvaTocTool.prototype.createContextMenuElements = function(selNode, event) {
    /* create the 'Delete TOC' menu elements */
    var ret = new Array();
    if (this.getNearestToc(selNode)) {
        ret.push(new ContextMenuElement('Delete TOC', this.deleteToc, this));
    } else {
        ret.push(
            new ContextMenuElement('Create TOC', this.createDefaultToc, this));
    };
    return ret;
};

SilvaTocTool.prototype.getTocText = function(depth) {
    var toctext = 'Table of Contents ';
    switch (depth) {
        case '-1':
            toctext += '(unlimited levels)';
            break;
        case '1':
            toctext += '(1 level)';
            break;
        default:
            toctext += '(' + depth + ' levels)';
            break;
    };
    return toctext;
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
    if (this.editor.getTool('extsourcetool').getNearestExternalSource(selNode)) {
        return;
    }
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


function SilvaCitationTool(
        authorinputid, sourceinputid, addbuttonid, updatebuttonid,
        delbuttonid, formid, toolboxid, plainclass, activeclass) {
    /* tool to manage citation elements */
    this.authorinput = getFromSelector(authorinputid);
    this.sourceinput = getFromSelector(sourceinputid);
    this.addbutton = getFromSelector(addbuttonid);
    this.updatebutton = getFromSelector(updatebuttonid);
    this.delbutton = getFromSelector(delbuttonid);
    this.toolbox = getFromSelector(toolboxid);
    this.form = getFromSelector(formid)
    this.plainclass = plainclass;
    this.activeclass = activeclass;
    this._inside_citation = false;
};

SilvaCitationTool.prototype = new KupuTool;

SilvaCitationTool.prototype.initialize = function(editor) {
    this.editor = editor;
    addEventHandler(this.addbutton, 'click', this.addCitation, this);
    addEventHandler(this.updatebutton, 'click', this.updateCitation, this);
    addEventHandler(this.delbutton, 'click', this.deleteCitation, this);
    if (editor.getBrowserName() == 'IE') {
        addEventHandler(
            editor.getInnerDocument(), 'keyup', this.cancelEnterPress, this);
        addEventHandler(
            editor.getInnerDocument(), 'keydown',
            this.handleKeyPressOnCitation, this);
    } else {
        addEventHandler(
            editor.getInnerDocument(), 'keypress',
            this.handleKeyPressOnCitation, this);
    };

    this.updatebutton.style.display = 'none';
    this.delbutton.style.display = 'none';
    this.form.style.display = 'none';
};

SilvaCitationTool.prototype.cancelEnterPress = function(event) {
    if (!this._inside_citation ||
            (event.keyCode != 13 && event.keyCode != 9)) {
        return;
    };
    if (event.preventDefault) {
        event.preventDefault();
    } else {
        event.returnValue = false;
    };
};

SilvaCitationTool.prototype.handleKeyPressOnCitation = function(event) {
    if (!this._inside_citation) {
        return;
    };
    var keyCode = event.keyCode;
    var citation = this.getNearestCitation(this.editor.getSelectedNode());
    var doc = this.editor.getInnerDocument();
    var selection = this.editor.getSelection();
    if (keyCode == 13 && this.editor.getBrowserName() == 'IE') {
        var br = doc.createElement('br');
        var currnode = selection.getSelectedNode();
        selection.replaceWithNode(br);
        selection.selectNodeContents(br);
        selection.collapse(true);
        this.editor.content_changed = true;
        event.returnValue = false;
    } else if (keyCode == 9) {
        var next = citation.nextSibling;
        if (!next) {
            next = doc.createElement('p');
            next.appendChild(doc.createTextNode('\xa0'));
            citation.parentNode.appendChild(next);
            this.editor.content_changed = true;
        };
        selection.selectNodeContents(next);
        selection.collapse();
        if (event.preventDefault) {
            event.preventDefault();
        };
        event.returnValue = false;
        this._inside_citation = false;
        this.form.style.display = 'none';
    };
};

SilvaCitationTool.prototype.updateState = function(selNode, event) {
    if (this.editor.getTool('extsourcetool').getNearestExternalSource(selNode)) {
        return;
    }
    var citation = this.getNearestCitation(selNode);
    if (citation) {
        this.addbutton.style.display = 'none';
        this.updatebutton.style.display = 'inline';
        this.delbutton.style.display = 'inline';
        this.authorinput.value = citation.getAttribute('author');
        this.sourceinput.value = citation.getAttribute('source');
        this._inside_citation = true;
        this.form.style.display = 'block';
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
        this.authorinput.value = '';
        this.sourceinput.value = '';
        this._inside_citation = false;
        this.form.style.display = 'none';
        if (this.toolbox) {
            this.toolbox.className = this.plainclass;
        };
    };
};

SilvaCitationTool.prototype.addCitation = function() {
    var selNode = this.editor.getSelectedNode();
    var citation = this.getNearestCitation(selNode);
    if (citation) {
        this.editor.logMessage('Nested citations are not allowed!');
        return;
    };
    var author = this.authorinput.value;
    var source = this.sourceinput.value;
    var doc = this.editor.getInnerDocument();
    var div = doc.createElement('div');
    div.className = 'citation';
    div.setAttribute('author', author);
    div.setAttribute('source', source);
    div.setAttribute('is_citation', '1');
    var selection = this.editor.getSelection();
    var docfrag = selection.cloneContents();
    var placecursoratend = false;
    if (docfrag.hasChildNodes()) {
        for (var i=0; i < docfrag.childNodes.length; i++) {
            div.appendChild(docfrag.childNodes[i]);
        };
        placecursoratend = true;
    } else {
        var text = doc.createTextNode('\xa0');
        div.appendChild(text);
    };
    this.editor.insertNodeAtSelection(div, 1);
    this.editor.content_changed = true;
    var selection = this.editor.getSelection();
    selection.collapse(placecursoratend);
    this.editor.getDocument().getWindow().focus();
    var selNode = selection.getSelectedNode();
    this.editor.updateState(selNode);
};

SilvaCitationTool.prototype.updateCitation = function() {
    var selNode = this.editor.getSelectedNode();
    var citation = this.getNearestCitation(selNode);
    if (!citation) {
        this.editor.logMessage('Not inside a citation element!');
        return;
    };
    citation.setAttribute('author', this.authorinput.value);
    citation.setAttribute('source', this.sourceinput.value);
    this.editor.content_changed = true;
};

SilvaCitationTool.prototype.deleteCitation = function() {
    var selNode = this.editor.getSelectedNode();
    var citation = this.getNearestCitation(selNode);
    if (!citation) {
        this.editor.logMessage('Not inside citation element!');
        return;
    };
    citation.parentNode.removeChild(citation);
    this.editor.content_changed = true;
};

SilvaCitationTool.prototype.getNearestCitation = function(selNode) {
    var currnode = selNode;
    while (currnode) {
        if (currnode.nodeName.toLowerCase() == 'div' &&
                currnode.getAttribute('is_citation')) {
            return currnode;
        };
        currnode = currnode.parentNode;
    };
    return false;
};

SilvaCitationTool.prototype.createContextMenuElements =
        function(selNode, event) {
    /* create the 'Delete citation' menu elements */
    var ret = new Array();
    if (this.getNearestCitation(selNode)) {
        ret.push(
            new ContextMenuElement('Delete cite', this.deleteCitation, this));
    };
    return ret;
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
    this.toolbox = getFromSelector(toolboxid);
    this.plainclass = plainclass;
    this.activeclass = activeclass;
    this.is_enabled = getFromSelector(isenabledid).value == 'True';
    this.disabled_text = getFromSelector(disabledtextid);
    this.nosources_text = getFromSelector(nosourcestextid);
    this.nosources = false;
    this._editing = false;
    this._url = null;
    this._id = null;
    this._form = null;
    this._insideExternalSource = false;

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
    addEventHandler(this.delbutton, 'click', this.delExternalSource, this);
    addEventHandler(
        editor.getInnerDocument(), 'keypress',
        this.handleKeyPressOnExternalSource, this);
    if (this.editor.getBrowserName() == 'IE') {
        addEventHandler(
            editor.getInnerDocument(), 'keydown',
            this.handleKeyPressOnExternalSource, this);
        addEventHandler(
            editor.getInnerDocument(), 'keyup',
            this.handleKeyPressOnExternalSource, this);
    };

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
    var extsource = this.getNearestExternalSource(selNode);
    if (!extsource) {
        /* if the externalsource element's preview is _only_ a floated
            div, in at least FF, clicking anywhere but inside the div
            will cause selNode to be the body (resulting in extsource==undefined)
            */
        var e = event || window.event;
        /* updateState is not always called on an event (like a mouse click
           sometimes it is during initialization */
        if (e) {
            var target = e.srcElement || e.target;
            extsource = this.getNearestExternalSource(target);
        } else {
            var selNode = this.editor.getSelectedNode();
            extsource = this.getNearestExternalSource(selNode);
        };
    };
    var heading = this.toolbox.getElementsByTagName('h1')[0];
    if (extsource) {
        if (this._insideExternalSource == extsource) {
            return;
        };
        /* if an external source is already active, remove it's active status */
        if (this._insideExternalSource) {
            this._insideExternalSource.className = this._insideExternalSource.className.replace(/ active/,'');
        };
        this._insideExternalSource = extsource;
        if (extsource.className.search("active")==-1) {
            extsource.className += " active";
        };
        selectSelectItem(this.idselect, extsource.getAttribute('source_id'));
        this.addbutton.style.display = 'none';
        this.cancelbutton.style.display = 'none';
        this.updatebutton.style.display = 'inline';
        this.delbutton.style.display = 'inline';
        this.startExternalSourceUpdate(extsource);
        this.disabled_text.style.display = 'none';
        if (this.toolbox) {
            this.toolbox.className = this.activeclass;
        };
        /* now do the new heading */
        title = extsource.getAttribute('source_title') ||
            extsource.getAttribute('source_id');
        span = document.createElement('span');
        span.setAttribute(
            'title', 'source id: ' + extsource.getAttribute('source_id'));
        span.appendChild(document.createTextNode('es \xab' + title + '\xbb'));
        heading.replaceChild(span, heading.firstChild);
        /* if the tool is collapsed, uncollapse it */
        var toolbody = getFromSelector(
            '#' + this.toolbox.id + ' div.kupu-tooltray');
        if (toolbody) {
            if (toolbody.style.display == 'none') {
                toolbody.style.display = 'block';
            };
        };
    } else {
        if (this._insideExternalSource) {
            this._insideExternalSource.className = this._insideExternalSource.className.replace(/ active/,'');
            this._insideExternalSource = false;
            this.resetTool();
            if (this.toolbox) {
                this.toolbox.className = this.plainclass;
            };
        };
    };
};

SilvaExternalSourceTool.prototype.handleKeyPressOnExternalSource =
        function(event) {
    if (!this._insideExternalSource) {
        return;
    };
    var keyCode = event.keyCode;
    var selNode = this.editor.getSelectedNode();
    var div = this.getNearestExternalSource(selNode);
    var doc = this.editor.getInnerDocument();
    var selection = this.editor.getSelection();
    var collapseToEnd = false;
    var sel;
    /* 13=enter -- add a new paragraph after*/
    if (keyCode == 13) {
        sel = doc.createElement('p');
        sel.appendChild(doc.createTextNode('\xa0'));
        if (!div.nextSibling) {
            div.parentNode.appendChild(sel);
        } else {
            div.parentNode.insertBefore(sel,div.nextSibling);
        };
        this.editor.content_changed = true;
        if (this._insideExternalSource) {
            this._insideExternalSource.className = this._insideExternalSource.className.replace(/ active/,'');
        };
        this._insideExternalSource = false;
    } else if (keyCode == 9 || keyCode == 39 || keyCode == 40) {
        /* 9=tab; 39=right; 40=down; */
        if (div.nextSibling) { 
            sel = div.nextSibling;
        } else {
            sel = doc.createElement('p');
            sel.appendChild(doc.createTextNode('\xa0'));
            div.parentNode.appendChild(sel);
            this.editor.content_changed = true;
        };
        if (this._insideExternalSource) {
            this._insideExternalSource.className = this._insideExternalSource.className.replace(/ active/,'');
        };
        this._insideExternalSource = false;
    } else if (keyCode == 37 || keyCode == 38) { 
        /* 37 = leftarrow, 38 = uparrow */
        sel = div.previousSibling;
        if (!sel) {
            sel = doc.createElement('p');
            sel.appendChild(doc.createTextNode('\xa0'));
            div.parentNode.insertBefore(sel,div);
            this.editor.content_changed = true;
        };
        collapseToEnd = true;
        if (this._insideExternalSource) {
            this._insideExternalSource.className = this._insideExternalSource.className.replace(/ active/,'');
        };
        this._insideExternalSource = false;
    } else if (keyCode == 8 || keyCode == 46) { /* 8=backspace, 46=delete */
        if (confirm("Are you sure you want to delete this external source?")) {
            sel = div.nextSibling;
            if (!sel) {
                sel = doc.createElement('p');
                sel.appendChild(doc.createTextNode('\xa0'));
                doc.appendChild(sel);
            };
            div.parentNode.removeChild(div);
            this.editor.content_changed = true;
            if (this._insideExternalSource) {
                this._insideExternalSource.className = this._insideExternalSource.className.replace(/ active/,'');
            };
            this._insideExternalSource = false;
        };
    };
    if (sel) {
        selection.selectNodeContents(sel);
        selection.collapse(collapseToEnd);
    };
    if (sel && sel.nodeName.toLowerCase() == 'div' &&
            sel.className == 'externalsource') {
        this.updateState(sel);
    };
    if (event.preventDefault) {
        event.preventDefault();
    } else {
        event.returnValue = false;
    };
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
            if (request.status.toString() == '200') {
                var returl = request.responseText;
                this._id = id;
                this._url = returl;
                handler.call(this, returl);
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
    // you should not be allowed to add external sources inside 
    // headers or table cells (but the cursor may be inside an ES title,
    // which is an H4.)
    var selNode = this.editor.getSelectedNode();
    if (selNode.tagName == 'H4' && selNode.parentNode.tagName == 'DIV' &&
            (selNode.parentNode.className=='externalsource' || selNode.parentNode.className=='externalsourcepreview')) {
        selNode = selNode.parentNode;
    };
    var not_allowed_parent_tags = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6'];
    for (i=0; i < not_allowed_parent_tags.length; i++){
        if (selNode.tagName == not_allowed_parent_tags[i]){
            alert('Code source is not allowed inside a header.')
            return
        };
    };
    if (selNode.tagName == 'TD'){
        alert('Code source is not allowed inside a table cell.')
        return
    };
    // get the appropriate form and display it
    if (!this._editing) {
        /* the 0 position is 'select source' and
            not a valid option */
        if (this.idselect.selectedIndex == 0) {
            return;
        };
        var id = this.idselect.options[this.idselect.selectedIndex].value;
        this.getUrlAndContinue(id, this._continueStartExternalSourceEdit);
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

SilvaExternalSourceTool.prototype.startExternalSourceUpdate =
        function(extsource) {
    var id = extsource.getAttribute('source_id');
    this.getUrlAndContinue(id, this._continueStartExternalSourceUpdate);
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
    addEventHandler(win, 'load', loadme, this)
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

SilvaExternalSourceTool.prototype.delExternalSource = function() {
    var selNode = this.editor.getSelectedNode();
    var source = this.getNearestExternalSource(selNode);
    if (!source) {
        this.editor.logMessage('Not inside external source!', 1);
        return;
    };
    var nextsibling = source.nextSibling;
    source.parentNode.removeChild(source);
    if (nextsibling) {
        var selection = this.editor.getSelection();
        selection.selectNodeContents(nextsibling);
        selection.collapse();
    };
    this.editor.content_changed = true;
    this.resetTool()
};

SilvaExternalSourceTool.prototype.resetTool = function() {
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
        var heading = this.toolbox.getElementsByTagName('h1')[0];
        heading.replaceChild(
            document.createTextNode('external source'),
            heading.firstChild
        );
    };
    //this.editor.updateState();
    this._editing = false;
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

SilvaExternalSourceTool.prototype._gatherFormDataFromElement = function(esElement) {
    /* esElement, if passed in, is an externalsource div in the document.  If passed in,
        this div will be used rather than attempting to get the nearest external source node
        from the current selection.  Useful for processing external sources in code outside
        of the ES tool (e.g. the ExternalSource preloader)*/
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
    var spans = source.getElementsByTagName("div")[0].getElementsByTagName('span');
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

SilvaExternalSourceTool.prototype.getNearestExternalSource =
        function(selNode) {

    var currnode = selNode;
    while (currnode) {
        if (currnode.nodeName.toLowerCase() == 'div' &&
                currnode.className.search(/(^externalsource$)|(^externalsource\s+)/)>-1) {
            return currnode;
        };
        currnode = currnode.parentNode;
    };
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
        el.setAttribute('silva_type', classname);
    };
    this.editor.content_changed = true;
    this.editor.updateState();
    this.editor.getDocument().getWindow().focus();
};

function SilvaPropertyTool(tablerowid, formid) {
    /* a simple tool to edit metadata fields

       the fields' contents are stored in Silva's metadata sets
    */
    this.tablerow = document.getElementById(tablerowid);
    this.form = document.getElementById(formid);
    this.table = this.tablerow.parentNode;
    while (!this.table.nodeName.toLowerCase() == 'table') {
        this.table = this.table.parentNode;
    };
    // remove current content from the fields
    var tds = this.tablerow.getElementsByTagName('td');
    for (var i=0; i < tds.length; i++) {
        while (tds[i].hasChildNodes()) {
            tds[i].removeChild(tds[i].childNodes[0]);
        };
    };
};

SilvaPropertyTool.prototype = new KupuTool;

SilvaPropertyTool.prototype.initialize = function(editor) {
    this.editor = editor;

    // walk through all metadata fields and expose them to the user
    var metas = this.editor.getInnerDocument().getElementsByTagName('meta');
    for (var i=0; i < metas.length; i++) {
        var meta = metas[i];
        var name = meta.getAttribute('name');
        if (!name) {
            // http-equiv type
            continue;
        };
        var rowcopy = this.tablerow.cloneNode(true);
        this.tablerow.parentNode.appendChild(rowcopy);
        // create the form elements, pass in the rowcopy so the row can be
        // rendered real-time, this because IE doesn't select checkboxes that
        // arent' visible(!!)
        this.parseFormElIntoRow(meta, rowcopy);
        /*
        if (tag) {
            this.tablerow.parentNode.appendChild(tag);
        };
        */
    };
    // throw away the original row: we don't need it anymore...
    this.tablerow.parentNode.removeChild(this.tablerow);
};

SilvaPropertyTool.prototype.parseFormElIntoRow = function(metatag, tablerow) {
    /* render a field in the properties tool according to a metadata tag

        returns some false value if the meta tag should not be editable
    */
    var scheme = metatag.getAttribute('scheme');
    if (!scheme || !(scheme in EDITABLE_METADATA)) {
        return;
    };
    var name = metatag.getAttribute('name');
    var namespace = metatag.getAttribute('scheme');
    var nametypes = EDITABLE_METADATA[scheme];
    var type = 'text';
    var mandatory = false;
    var namefound = false;
    var fieldtitle = '';
    for (var i=0; i < nametypes.length; i++) {
        var nametype = nametypes[i];
        var elname = nametype[0];
        var type = nametype[1];
        var mandatory = nametype[2];
        var fieldtitle = nametype[3];
        if (elname == name) {
            namefound = true;
            break;
        };
    };
    if (!namefound) {
        return;
    };

    tablerow.removeChild(tablerow.getElementsByTagName('td')[1]);   

    var value = metatag.getAttribute('content');
    var parentvalue = metatag.getAttribute('parentcontent');
    var td = tablerow.getElementsByTagName('td')[0]
    if (type == 'text' || type == 'textarea' || type == 'datetime') {
        this._createSimpleItemHTML(
            type, value, name, namespace, mandatory, td, fieldtitle);
    } else if (type == 'checkbox') {
        var titlecell = tablerow.getElementsByTagName('td')[0];
        this._createCheckboxItemHTML(
            titlecell, value, name, namespace, mandatory, td, fieldtitle);
    };
    if (parentvalue && parentvalue != '') {
        td.appendChild(document.createElement('br'));
        td.appendChild(document.createTextNode('acquired value:'));
        td.appendChild(document.createElement('br'));
        td.appendChild(document.createTextNode(parentvalue));
    };

    return tablerow;
};

// just to make the above method a bit more readable
SilvaPropertyTool.prototype._createSimpleItemHTML = function(
        type, value, name, namespace, mandatory, td, fieldtitle) {

    var outerdiv = document.createElement('div');
    outerdiv.className = 'kupu-properties-item-outerdiv';

    // the arrow and 'items' label
    var h2div = document.createElement('h2');
    outerdiv.appendChild(h2div);
    var img = document.createElement('img');
    // XXX would be nice if this would be absolute...
    img.src = 'service_kupu_silva/closed_arrow.gif'; 
    outerdiv.image = img; // XXX memory leak!!
    h2div.appendChild(img);
    h2div.appendChild(document.createTextNode(fieldtitle));
    h2div.className = 'kupu-properties-metadata-field'
    // handler for showing/hiding the checkbox divs
    var handler = function(evt) {
        if (this.lastChild.style.display == 'none') {
            this.image.src = 'service_kupu_silva/opened_arrow.gif';
            this.image.setAttribute('title', _('click to fold'));
            this.lastChild.style.display = 'block';
        } else {
            this.image.src = 'service_kupu_silva/closed_arrow.gif';
            this.image.setAttribute('title', _('click to unfold'));
            this.lastChild.style.display = 'none';
        };
    };
    addEventHandler(h2div, 'click', handler, outerdiv);

    var innerdiv = document.createElement('div');
    innerdiv.className = 'kupu-properties-item-innerdiv';
    outerdiv.appendChild(innerdiv);

    var input = null;

    if (type == 'text' || type == 'datetime') {
        input = document.createElement('input');
        input.setAttribute('type', 'text');
        input.value = value;
        if (type == 'datetime') {
            input.setAttribute('widget:type', 'datetime');
        };
    } else if (type == 'textarea') {
        input = document.createElement('textarea');
        var content = document.createTextNode(value);
        input.appendChild(content);
    };
    input.setAttribute('name', name);
    input.setAttribute('namespace', namespace);
    input.className = 'metadata-input';
    if (mandatory) {
        input.setAttribute('mandatory', 'true');
    };
    innerdiv.appendChild(input);
    td.appendChild(outerdiv);
};

SilvaPropertyTool.prototype._createCheckboxItemHTML = function(
        titlecell, value, name, namespace, mandatory, td, fieldtitle) {
    // elements are seperated by ||
    var infos = value.split('||');

    // messy stuff coming up, that make the checkboxes appear in some
    // 'foldable' div
    var outerdiv = document.createElement('div');
    outerdiv.className = 'kupu-properties-item-outerdiv';

    // the arrow and 'items' label
    var h2div = document.createElement('h2');
    outerdiv.appendChild(h2div);
    var img = document.createElement('img');
    // XXX would be nice if this would be absolute...
    img.src = 'service_kupu_silva/closed_arrow.gif'; 
    outerdiv.image = img; // XXX memory leak!!
    h2div.appendChild(img);
    h2div.appendChild(document.createTextNode(fieldtitle));
    h2div.className = 'kupu-properties-metadata-field'

    // handler for showing/hiding the checkbox divs
    var handler = function(evt) {
        if (this.lastChild.style.display == 'none') {
            this.image.src = 'service_kupu_silva/opened_arrow.gif';
            this.image.setAttribute('title', _('click to fold'));
            this.lastChild.style.display = 'block';
        } else {
            this.image.src = 'service_kupu_silva/closed_arrow.gif';
            this.image.setAttribute('title', _('click to unfold'));
            this.lastChild.style.display = 'none';
        };
    };
    addEventHandler(h2div, 'click', handler, outerdiv);

    // innerdiv is where the actual checkboxes are displayed in, and what
    // is collapsed/uncollapsed
    var innerdiv = document.createElement('div');
    innerdiv.className = 'kupu-properties-item-innerdiv';
    outerdiv.appendChild(innerdiv);
    td.appendChild(outerdiv);

    for (var i=0; i < infos.length; i++) {
        // in certain cases the value you want to display is different
        // from that you want to store, in that case seperate id from
        // value with a |, there should always be a value|checked, but
        // in some cases you may want a value|title|checked set...
        var info = infos[i].split('|');
        var itemvalue = info[0];
        var title = info[0];
        var checked = (info[1] == 'true' || info[1] == 'yes');
        if (info.length == 3) {
            title = info[1];
            checked = (info[2] == 'true' || info[2] == 'yes');
        };
        var div = document.createElement('div');
        div.className = 'kupu-properties-checkbox-line';
        innerdiv.appendChild(div);

        var cbdiv = document.createElement('div');
        cbdiv.className = 'kupu-properties-checkbox-input';
        div.appendChild(cbdiv);

        checkbox_id = 'kupu-properties-' + fieldtitle + '-' + title;
        var checkbox = document.createElement('input');
        checkbox.setAttribute('name', name);
        checkbox.setAttribute('namespace', namespace);
        checkbox.setAttribute('id',checkbox_id);
        checkbox.type = 'checkbox';
        checkbox.value = itemvalue;
        cbdiv.appendChild(checkbox);
        if (checked) {
            checkbox.checked = 'checked';
        };
        checkbox.className = 'metadata-checkbox';
        // XXX a bit awkward to set this on all checkboxes
        if (mandatory) {
            checkbox.setAttribute('mandatory', 'true');
        };
        var textdiv = document.createElement('div');
        textdiv.className = 'kupu-properties-checkbox-item-title';
        var cblabel = document.createElement('label');
        cblabel.setAttribute('for',checkbox_id);
        cblabel.htmlFor = checkbox_id; /* for IE 6 setAttribute doesn't work */
        cblabel.appendChild(document.createTextNode(title));
        textdiv.appendChild(cblabel);
        div.appendChild(textdiv);
    };
    // we can not hide the checkboxes earlier because IE requires them
    // to be *visible* in order to check them from code :(
    innerdiv.style.display = 'none';
};

SilvaPropertyTool.prototype.beforeSave = function() {
    /* save the metadata to the document */
    if (window.widgeteer) {
        widgeteer.widget_registry.prepareForm(this.form);
    };
    var doc = this.editor.getInnerDocument();
    var inputs = this.table.getElementsByTagName('input');
    var textareas = this.table.getElementsByTagName('textarea');
    var checkboxdata = {}; // name: value for all checkboxes checked
    var errors = [];
    var okay = [];
    for (var i=0; i < inputs.length; i++) {
        var input = inputs[i];
        if (!input.getAttribute('namespace')) {
            continue;
        };
        var name = input.getAttribute('name');
        var scheme = input.getAttribute('namespace');
        if (input.getAttribute('type') == 'text') {
            var value = input.value;
            if (input.getAttribute('mandatory') && value.strip() == '') {
                errors.push(name);
                continue;
            };
            okay.push([name, scheme, value]);
        } else if (input.getAttribute('type') == 'checkbox') {
            if (checkboxdata[name] === undefined) {
                checkboxdata[name] = [];
                // XXX yuck!!
                checkboxdata[name].namespace = scheme;
                checkboxdata[name].mandatory = 
                    input.getAttribute('mandatory') ? true : false;
            };
            if (input.checked) {
                checkboxdata[name].push(
                    input.value.replace('|', '&pipe;', 'g'));
            };
        };
    };
    for (var i=0; i < textareas.length; i++) {
        var textarea = textareas[i];
        var name = textarea.getAttribute('name');
        var scheme = textarea.getAttribute('namespace');
        var value = textarea.value;
        if (textarea.getAttribute('mandatory') && value.strip() == '') {
            errors.push(name);
            continue;
        };
        okay.push([name, scheme, value]);
    };
    for (var name in checkboxdata) {
        if (checkboxdata[name].mandatory && checkboxdata[name].length == 0) {
            errors.push(name);
        } else {
            var data = checkboxdata[name];
            okay.push([name, data.namespace, data.join('|')]);
        };
    };
    if (errors.length) {
        throw('Error in properties: fields ' + errors.join(', ') + 
            ' are required but not filled in');
    };
    for (var i=0; i < okay.length; i++) {
        this._addMetaTag(doc, okay[i][0], okay[i][1], okay[i][2]);
    };
};

SilvaPropertyTool.prototype._addMetaTag = function(
        doc, name, scheme, value, parentvalue) {
    var head = doc.getElementsByTagName('head')[0];
    if (!head) {
        throw('The editable document *must* have a <head> element!');
    };
    // first find and delete the old one
    // XXX if only we'd have XPath...
    var metas = doc.getElementsByTagName('meta');
    for (var i=0; i < metas.length; i++) {
        var meta = metas[i];
        if (meta.getAttribute('name') == name && 
                meta.getAttribute('scheme') == scheme) {
            meta.parentNode.removeChild(meta);
        };
    };
    var tag = doc.createElement('meta');
    tag.setAttribute('name', name);
    tag.setAttribute('scheme', scheme);
    tag.setAttribute('content', value);

    head.appendChild(tag);
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
    selection.moveEnd(1);
    selection.collapse(true);
    this.editor.logMessage('Character ' + c + ' inserted');
    this.editor.getDocument().getWindow().focus();
    select.selectedIndex = 0;
    this.editor.content_changed = true;
};
