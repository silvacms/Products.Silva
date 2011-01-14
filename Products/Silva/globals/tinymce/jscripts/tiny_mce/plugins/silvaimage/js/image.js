var ImageDialog = {
    preInit : function() {
        tinyMCEPopup.requireLangPack();
    },
        
    init : function(ed) {
        var f = document.forms[0], 
            nl = f.elements, 
            ed = tinyMCEPopup.editor, 
            dom = ed.dom, 
            n = ed.selection.getNode(),
            showPreview;
        tinyMCEPopup.resizeToInnerSize();
        this.fillClassList('silvaclass_list');
        this.fillClassList('extclass_list');
        TinyMCE_EditableSelects.init();
        if (n.nodeName == 'IMG') {
            var src = dom.getAttrib(n, 'src'),
                 silvaOrExt = src.match(/(.*)\?(thumbnail|webformat|hires)$/);

            if (silvaOrExt != null) {
                showPreview = "silva";
                /* silva image */
                nl.silvasrc.value = silvaOrExt[1]
                selectByValue(f, 'silvasize', silvaOrExt[2]);
                /* both the title and alt of the image are the same */
                nl.silvatitle.value = n.title;
                selectByValue(f, 'silvaalign', this.getAttrib(n, 'align'));
                selectByValue(f, 'silvaclass_list', n.className, true, true);
            } else { /* external image */
                showPreview = "ext";
                nl.extsrc.value = n.src;
                nl.extalt.value = n.alt;
                nl.exttitle.value = n.title;
                nl.extwidth.value = n.width;
                nl.extheight.value = n.height;
                selectByValue(f, 'extalign', this.getAttrib(n, 'align'));
                selectByValue(f, 'extclass_list', n.className, true, true);
                // set active panel to "ext_tab"
                mcTabs.displayTab('ext_tab','ext_panel');
            }
            /* common properties */
            nl.style.value = n.style;
            nl.id.value = n.id;
            nl.longdesc.value = n.longDesc;
            this.changeAppearance('silva');
            this.changeAppearance('ext');
            
            if (/^\s*this.src\s*=\s*\'([^\']+)\';?\s*$/.test(dom.getAttrib(n, 'onmouseover')))
            nl.onmouseoversrc.value = dom.getAttrib(n, 'onmouseover').replace(/^\s*this.src\s*=\s*\'([^\']+)\';?\s*$/, '$1');
            
            if (ed.settings.inline_styles) {
            // Move attribs to styles
                if (n.align)
                    this.updateStyle('align');
        
                if (n.hspace)
                    this.updateStyle('hspace');
                
                if (n.border)
                    this.updateStyle('border');
            
                if (n.vspace)
                    this.updateStyle('vspace');
            }
        }
    
        if (ed.getParam("silvaimage_constrain_proportions", true))
            f.extconstrain.checked = true;
            
        // Check swap image if valid data
        if (nl.onmouseoversrc.value)
            this.setSwapImage(true);
        else
            this.setSwapImage(false);
        
        this.changeAppearance();
        if (showPreview) {
            // showPreview = the prefix for the type of image (either silva or ext)
            this.showPreviewImage(showPreview, nl[showPreview + "src"].value, 1);
        }
    },
            
    insert : function(file, title) {
        var ed = tinyMCEPopup.editor, 
            t = this, 
            f = document.forms[0];
        if (f.silvasrc.value === "" && f.extsrc.value === "") {
            if (ed.selection.getNode().nodeName == 'IMG') {
                ed.dom.remove(ed.selection.getNode());
                ed.execCommand('mceRepaint');
            }
            
            tinyMCEPopup.close();
            return;
        }
        if (tinyMCEPopup.getParam("accessibility_warnings", 1)) {
            if ((f.silvasrc.value && !f.silvatitle.value) || 
                (f.extsrc.value && !f.extalt.value)) {
                tinyMCEPopup.confirm(tinyMCEPopup.getLang('silvaimage_dlg.missing_alt'), 
                    function(s) {
                        if (s) t.insertAndClose();
                });
                return;
            }
        }
        t.insertAndClose();
    },
    
    insertAndClose : function() {
        var ed = tinyMCEPopup.editor,
            f = document.forms[0],
            nl = f.elements,
            which = nl.silvasrc.value ? 'silva' : 'ext',
            v,
            args = {},
            el;
        
        tinyMCEPopup.restoreSelection();
    
        // Fixes crash in Safari
        if (tinymce.isWebKit)
            ed.getWin().focus();

        if (!ed.settings.inline_styles) {
            args = {
                vspace : nl.vspace.value,
                hspace : nl.hspace.value,
                border : nl.border.value,
                align : getSelectValue(f, which + 'align')
            };
        } else {
            // Remove deprecated values
            args = {
                vspace : '',
                hspace : '',
                border : '',
                align : ''
            };
        }
        if (nl.silvasrc.value) {
            var src = nl.silvasrc.value + '?' + nl.silvasize.value;
            tinymce.extend(args, {
                src : src,
                alt : nl.silvatitle.value,
                title : nl.silvatitle.value,
                style : nl.style.value
            });
            /* get width / height from preview image */
            var prevImg = document.getElementById('silvaPreviewImg');
            if (prevImg && (prevImg.height || prevImg.width)) {
                tinymce.extend(args, {
                    width: prevImg.width,
                    height: prevImg.height
                });
            }
        } else { /* external image */
            tinymce.extend(args, {
                src : nl.extsrc.value,
                width : nl.extwidth.value,
                height : nl.extheight.value,
                alt : nl.extalt.value,
                title : nl.exttitle.value,
                style : nl.style.value
            });
        
        }
        tinymce.extend(args, {
            id : nl.id.value,
            'class' : getSelectValue(f, which + 'class_list'),
            longdesc : nl.longdesc.value
        });
            
        args.onmouseover = args.onmouseout = '';
            
        if (f.onmousemovecheck.checked) {
            if (nl.onmouseoversrc.value) {
                args.onmouseover = "this.src='" + nl.onmouseoversrc.value + "';";
        
                args.onmouseout = "this.src='" + args.src + "';";
            }
        }
                
        el = ed.selection.getNode();
        
        if (el && el.nodeName == 'IMG') {
            ed.dom.setAttribs(el, args);
        } else {
            ed.execCommand('mceInsertContent', false, '<img id="__mce_tmp" />', {skip_undo : 1});
            ed.dom.setAttribs('__mce_tmp', args);
            ed.dom.setAttrib('__mce_tmp', 'id', '');
            ed.undoManager.add();
        }
            
        tinyMCEPopup.close();
    },
            
    getAttrib : function(e, at) {
        var ed = tinyMCEPopup.editor, dom = ed.dom, v, v2;
        
        if (ed.settings.inline_styles) {
            switch (at) {
                case 'align':
                    if (v = dom.getStyle(e, 'float'))
                        return v;
                    if (v = dom.getStyle(e, 'vertical-align'))
                        return v;
                    break;
                case 'hspace':
                    v = dom.getStyle(e, 'margin-left')
                    v2 = dom.getStyle(e, 'margin-right');
                    if (v && v == v2)
                        return parseInt(v.replace(/[^0-9]/g, ''));
                    break;
                case 'vspace':
                    v = dom.getStyle(e, 'margin-top')
                    v2 = dom.getStyle(e, 'margin-bottom');
                    if (v && v == v2)
                        return parseInt(v.replace(/[^0-9]/g, ''));
                    break;
                case 'border':
                    v = 0;
                    tinymce.each(['top', 'right', 'bottom', 'left'], 
                                function(sv) {
                                    sv = dom.getStyle(e, 'border-' + sv + '-width');
                                    // False or not the same as prev
                                    if (!sv || (sv != v && v !== 0)) {
                                        v = 0;
                                        return false;
                                    }
                                    if (sv)
                                    v = sv;
                    });
                    if (v)
                        return parseInt(v.replace(/[^0-9]/g, ''));
                    break;
            }
        }
            
        if (v = dom.getAttrib(e, at))
            return v;
        return '';
    },
    
    setSwapImage : function(st) {
        var f = document.forms[0];
        
        f.onmousemovecheck.checked = st;
        setBrowserDisabled('overbrowser', !st);
        setBrowserDisabled('outbrowser', !st);
            
        if (f.over_list)
            f.over_list.disabled = !st;
        
        if (f.out_list)
        f.out_list.disabled = !st;
        
        f.onmouseoversrc.disabled = !st;
        f.onmouseoversrclookup.disabled = !st;
    },
            
    fillClassList : function(id) {
        var dom = tinyMCEPopup.dom,
            lst = dom.get(id),
            v,
            cl;
        if (v = tinyMCEPopup.getParam('silvaimage_styles')) {
            cl = [];
        
            tinymce.each(v.split(';'), function(v) {
                var p = v.split('=');
                cl.push({'title' : p[0], 'class' : p[1]});
            });
        } else {
            cl = tinyMCEPopup.editor.dom.getClasses();
        }
        if (cl.length > 0) {
            lst.options.length = 0;
            lst.options[lst.options.length] = new Option(tinyMCEPopup.getLang('not_set'), '');
        
            tinymce.each(cl, function(o) {
                lst.options[lst.options.length] = new Option(o.title || o['class'], o['class']);
            });
        } else {
            dom.remove(dom.getParent(id, 'tr'));
        }
    },
    
    resetImageData : function(which) {
        var f = document.forms[0];
        if (which=='ext') {
            f.elements.extwidth.value = f.elements.extheight.value = '';
        }
    },
    
    updateImageData : function(img, st) {
    /* called when the preview image loads (i.e. onload) */
        var f = document.forms[0];
        if (img.id.match(/^ext/)) {
            img.setAttribute('_mce_width',img.width);
            img.setAttribute('_mce_height',img.height);
            if (!st) {
                f.elements.extwidth.value = img.width;
                f.elements.extheight.value = img.height;
            } else {
                img.width = f.elements.extwidth.value
                img.height = f.elements.extheight.value
            }
        }
        this[img.id] = img;
    },
    
    
    changeAppearance : function(previewPrefix) {
        var ed = tinyMCEPopup.editor, 
            f = document.forms[0], 
            img = document.getElementById(previewPrefix + 'AlignSampleImg');
        if (img) {
            if (previewPrefix=="silva") {
                img.align = f.silvaalign.value;
            } else if (ed.getParam('inline_styles')) {
                ed.dom.setAttrib(img, 'style', f.style.value);
            } else {
                img.align = f.extalign.value;
                img.border = f.extborder.value;
                img.hspace = f.exthspace.value;
                img.vspace = f.extvspace.value;
            }
        }
    },
            
    changeHeight : function(useConstrain) {
        /* if useConstrain is true, then the new height (placed in extheight)
           is updated based on the proportion of the 
           (current width (extwidth) / orig width) * orig height.
           
           If false, then the height of the preview image is updated to the
            extheight.
        */
        var f = document.forms[0], 
            tp;
        if (useConstrain) {
            if (!f.extconstrain || !f.extconstrain.checked || !this.extPreviewImg) {
                return;
            }
                
            if (f.extwidth.value == "" || f.extheight.value == "") {
                return;
            }
                
            tp = (parseInt(f.extwidth.value) / parseInt(this.extPreviewImg.getAttribute('_mce_width'))) * this.extPreviewImg.getAttribute('_mce_height');
            f.extheight.value = this.extPreviewImg.height = tp.toFixed(0);
        } else {
            this.extPreviewImg.height = f.extheight.value;
        }
    },
            
    changeWidth : function(useConstrain) {
        /* if useConstrain is true, then the new width (placed in extwidth)
           is updated based on the proportion of the 
           (current height (extheight) / orig height) * orig width
           
           If false, then the width of the preview image is updated to the
            extwidth.
         */
        var f = document.forms[0],
            tp;
        if (useConstrain) {
        if (!f.extconstrain || !f.extconstrain.checked || !this.extPreviewImg) {
            return;
        }
            
        if (f.extwidth.value == "" || f.extheight.value == "") {
            return;
        }
            
        tp = (parseInt(f.extheight.value) / parseInt(this.extPreviewImg.getAttribute('_mce_height'))) * this.extPreviewImg.getAttribute('_mce_width');
        f.extwidth.value = this.extPreviewImg.width = tp.toFixed(0);
        } else {
            this.extPreviewImg.width = f.extwidth.value;
        }
    },
            
    updateStyle : function(ty) {
        var dom = tinyMCEPopup.dom, 
            st,
            v, 
            f = document.forms[0],
            which = f.silvasrc.value && 'silva' || 'ext',
            img = dom.create('img', {style : dom.get('style').value});
        
        if (tinyMCEPopup.editor.settings.inline_styles) {
            // Handle align
            if (ty == 'align') {
                dom.setStyle(img, 'float', '');
                dom.setStyle(img, 'vertical-align', '');
        
                v = getSelectValue(f, which+'align');
                if (v) {
                    if (v == 'left' || v == 'right')
                        dom.setStyle(img, 'float', v);
                    else
                        img.style.verticalAlign = v;
                }
            }
                
            // Handle border
            if (ty == 'border' && which=='ext') {
                dom.setStyle(img, 'border', '');
    
                v = f.border.value;
                if (v || v == '0') {
                    if (v == '0')
                        img.style.border = '0';
                    else
                        img.style.border = v + 'px solid black';
                }
            }
                
            // Handle hspace
            if (ty == 'hspace' && which=='ext') {
                dom.setStyle(img, 'marginLeft', '');
                dom.setStyle(img, 'marginRight', '');
    
                v = f.hspace.value;
                if (v) {
                    img.style.marginLeft = v + 'px';
                    img.style.marginRight = v + 'px';
                }
            }
        
            // Handle vspace
            if (ty == 'vspace' && which=='ext') {
                dom.setStyle(img, 'marginTop', '');
                dom.setStyle(img, 'marginBottom', '');
    
                v = f.vspace.value;
                if (v) {
                    img.style.marginTop = v + 'px';
                    img.style.marginBottom = v + 'px';
                }
            }
        
            // Merge
            dom.get('style').value = dom.serializeStyle(dom.parseStyle(img.style.cssText), 'img');
        }
    },
    
    showPreviewImage : function(which, u, st) {
        if (!u) {
            tinyMCEPopup.dom.setHTML(which+'prev', '');
            return;
        }
        
        if (!st && tinyMCEPopup.getParam("silvaimage_update_dimensions_onchange", true))
            this.resetImageData(which);
                
        if (which=='silva') {
            /* add the image format if not already present */
            var silvaURL = u.match(/(.*)\?(thumbnail|webformat|hires)$/);
            if (!silvaURL) {
                u += '?' + document.forms[0].elements['silvasize'].value;
            }
        }
        u = tinyMCEPopup.editor.documentBaseURI.toAbsolute(u);
        if (!st) {
            var html = '<img id="'+which+'PreviewImg" src="' + u + '" border="0" onload="ImageDialog.updateImageData(this);" onerror="ImageDialog.resetImageData("'+which+'");" />'
            tinyMCEPopup.dom.setHTML(which+'prev', html);
        } else {
            var html = '<img id="'+which+'PreviewImg" src="' + u + '" border="0" onload="ImageDialog.updateImageData(this, 1);" />';
            tinyMCEPopup.dom.setHTML(which+'prev', html);
        }
    },
        
    lookupSilvaImage: function(inputID) {
        var href = window.opener.containerurl || window.opener.location.href,
	t = this;
        href = href.replace(/\/edit(\/tab_edit\/?)?$/,'');
        
        var handler = function(path, id, title) {
	    var nl = document.forms[0].elements;
	    if (inputID == 'silvasrc') {
		nl['silvasrc'].value = path;
		nl['silvatitle'].value = title;
		/* clear the "external image" inputs */
		t.resetImageSettings('ext');
		t.showPreviewImage('silva', path);
	    } else { /* likely an onmouseover/out */
		nl[inputID].value = path;
	    }
	};
	startpath = href;
	filter = 'Silva Image';
	show_add = true;
	/* not much point in sending this, since the selected_path needs to be
	   the full physical path of the source, and this is rooted at the docbase.  
	   If set (correctly), this will cause the radio button for the object
	   with the same phys. path. to be selected. */
	selected_path = document.forms[0].elements['silvasrc'].value;

	sourcepath = href.replace(/^https?:\/\/.*?\//,'/'); //Trim server from front
	sourcepath = sourcepath.replace(/\/$/,''); //Trim trailing slash, if present
	reference.getReference(handler,startpath,filter,show_add,selected_path,sourcepath);
    },
    
    resetImageSettings: function(which) {
        /* clear out the image settings for either the "ext" or "silva"
           tabs.  This should be called whenever the image src is set
           in either tab 
           @which - the tab to clear settings.  Either 'silva' or 'ext' 
        */
        if (which != 'silva') {
            which = 'ext';
        }
        document.forms[0].elements[which+'src'].value = '';
        if (document.forms[0].elements[which+'alt']) {
            document.forms[0].elements[which+'alt'].value = '';
        }
        document.forms[0].elements[which+'title'].value = '';
        // calling this with no url (second param) will cause
        // the preview image for that image type to be cleared.
        this.showPreviewImage(which);
    }
};
            
ImageDialog.preInit();
tinyMCEPopup.onInit.add(ImageDialog.init, ImageDialog);