lookupWindow = null;

// helper function and class ripped from Kupu, the no. 1 WYSIWYG editor ;)

function addEventHandler(element, event, method, context) {
    /* method to add an event handler for both IE and Mozilla */
    var wrappedmethod = new ContextFixer(method, context);
    if (!document.all) {
        element.addEventListener(event, wrappedmethod.execute, false);
    } else {
        element.attachEvent("on" + event, wrappedmethod.execute);
    };
};

function ContextFixer(func, context) {
    /* Make sure 'this' inside a method points to its class */
    this.func = func;
    this.context = context;
    this.args = arguments;
    var self = this;
    
    this.execute = function() {
        /* execute the method */
        var args = new Array();
        // the first arguments will be the extra ones of the class
        for (var i=0; i < self.args.length - 2; i++) {
            args.push(self.args[i + 2]);
        };
        // the last are the ones passed on to the execute method
        for (var i=0; i < arguments.length; i++) {
            args.push(arguments[i]);
        };
        self.func.apply(self.context, args);
    };
};

// some additional helper functions
getPageX = function(event) {
    if (!event.pageX) {
        var orgnode = event.srcElement;
        var currnode = orgnode;
        var left = event.offsetX;
        while (currnode) {
            left += currnode.offsetLeft + currnode.clientLeft;
            currnode = currnode.offsetParent;
        };
        return left;
      } else {
        return event.pageX;
    };
};

getPageY = function(event) {
    if (!event.pageY) {
        var orgnode = event.srcElement;
        var currnode = orgnode;
        var top = event.offsetY;
        while (currnode) {
            top += currnode.offsetTop + currnode.clientTop;
            currnode = currnode.offsetParent;
        };
        return top;
    } else {
        return event.pageY;
    };
};

function Draggable(draggable, dragbar) {
    this.draggable = document.getElementById(draggable);
    this.dragbar = document.getElementById(dragbar);

    this._dragging = false;
    this._startOffsetLeft = 0;
    this._startOffsetTop = 0;

    this.initialize = function() {
        addEventHandler(this.dragbar, 'mousedown', this.startDrag, this);
        addEventHandler(document, 'mousemove', this.dragElement, this);
        addEventHandler(document, 'mouseup', this.endDrag, this);
    };

    this.startDrag = function(event) {
        this._dragging = true;
        this._startOffsetLeft = event.layerX ? event.layerX : event.offsetX;
        this._startOffsetTop = event.layerY ? event.layerY : event.offsetY;
    };

    this.dragElement = function(event) {
        if (!this._dragging) {
            return;
        };
        this.draggable.style.left = '' + (getPageX(event) - this._startOffsetLeft) + 'px';
        this.draggable.style.top = '' + (getPageY(event) - this._startOffsetTop) + 'px';
        if (event.preventDefault) {
            event.preventDefault();
        } else {
            event.returnValue = false;
        };
    };

    this.endDrag = function(event) {
        this._dragging = false;
    };
};

function Resizable(resizable, handle, minwidth, minheight) {
    this.resizable = document.getElementById(resizable);
    this.handle = document.getElementById(handle);
    this.minwidth = minwidth;
    this.minheight = minheight;

    this.resizing = false;
    this.startOffsetRight = 0;
    this.startOffsetBottom = 0;

    this.initialize = function() {
        addEventHandler(this.handle, "mousedown", this.startResize, this);
        addEventHandler(document, "mousemove", this.resizeElement, this);
        addEventHandler(document, "mouseup", this.stopResize, this);
    };

    this.startResize = function(event) {
        this.resizing = true;
        this.startOffsetRight = event.layerX ? (parseInt(this.resizable.style.width) - event.layerX) : (parseInt(this.handle.style.width) - event.offsetX);
        this.startOffsetBottom = event.layerY ? (parseInt(this.resizable.style.height) - event.layerY) : (parseInt(this.handle.style.height) - event.offsetY);
    };

    this.resizeElement = function(event) {
        if (!this.resizing) {
            return;
        };
        var width = (getPageX(event) - parseInt(this.resizable.style.left)) + this.startOffsetRight;
        var height = (getPageY(event) - parseInt(this.resizable.style.top)) + this.startOffsetBottom;
        if (width > this.minwidth) {
            this.resizable.style.width = '' + width + 'px';
        };
        if (height > this.minheight) {
            this.resizable.style.height = '' + height + 'px';
        };
        if (event.preventDefault) {
            event.preventDefault();
        } else {
            event.returnValue = false;
        };
    };

    this.stopResize = function(event) {
        this.resizing = false;
    };

};


function Cropper(layer, dragbar, resizehandle, minwidth, minheight) {
    this.resizable = new Resizable(layer, resizehandle, minwidth, minheight);
    this.draggable = new Draggable(layer, dragbar);
    
    this.layer = document.getElementById(layer);
    this.dragbar = document.getElementById(dragbar);
    this.resizehandle = document.getElementById(resizehandle);

    
    this.initialize = function() {
        var additional = document.getElementById('additional_draggable');
        addEventHandler(additional, 'mousedown', this.draggable.startDrag, this.draggable);
        addEventHandler(document, 'dblclick', this.insertCropCoords, this);
        this.draggable.initialize();
        this.resizable.initialize();
    };

    this.width = function() {
        return parseInt(this.layer.style.width);
    };

    this.height = function() {
        return parseInt(this.layer.style.height);
    };

    this.left = function() {
    return parseInt(this.layer.style.left) - 200;
    };

    this.top = function() {
        return parseInt(this.layer.style.top);
    };
    
    this.insertCropCoords = function(event) {
        // Append to previously focused text area
        field_web_crop = opener.document.getElementById('field_web_crop');
        var x1 = this.left();
        var y1 = this.top();
        
        // test if the cropper don't add negative values
        if (x1 < 0) {
          x1 = 0;
        };
        if (y1 < 0) {
          y1 = 0;
        };
        
        x2 = x1 + this.width();
        y2 = y1 + this.height();
        
        crop = x1 + 'x' + y1 + '-' + x2 + 'x' + y2;
        field_web_crop.value = crop;
        
        // Close LookupWindow
        self.close();
    };

    this.initialize();
};

function openlookupWindow(url_to_open, url_to_image) {
  width = 512;
  height = 512;
  leftPos = (screen.width - width) / 2;
  topPos = (screen.height - height) / 2;
  aspects = 'toolbar=no, status=yes, scrollbars=yes, resizable=yes, width='+width+',height='+height+',left='+leftPos+',top='+topPos;
  lookupWindow = window.open(
    url_to_open, 'ImageMapWindow', aspects);
  lookupWindow.focus();
}

