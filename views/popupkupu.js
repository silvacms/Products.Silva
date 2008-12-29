function openPopupKupu(contentbaseid,buttons,textstyles,toolboxes) {
    var winwidth = 750;
    var winheight = 500;
    var leftpos = (screen.width - winwidth) / 2;
    var toppos = (screen.height - winheight) / 2;
    var winname = 'kupu_popup_window' + contentbaseid;
    var winurl = '../@@kupu_popup_window?content_id='+contentbaseid + 'content';
    var win = window.open('about:blank', 
                           winname,
                           'toolbar=yes,status=yes,scrollbars=yes,' +
                           'resizable=yes,width=' + winwidth +
                           ',height=' + winheight +
                           ',left=' + leftpos + ',top=' + toppos);
    /* store the popup kupu settings and the save callback in the new
       window */
    win.kupu_popup_ui_init_settings = [buttons,textstyles,toolboxes];
    win.save_callback = function(content) {
        document.getElementById(contentbaseid+'content').innerHTML = content;
        ta = document.getElementById(contentbaseid);
        ta.value = content;
        window.kupueditor.content_changed = true;
        
    }
    win.location.href = winurl;
    win.focus();
}
