/*****************************************************************************
 *
 * Copyright (c) 2003-2005 Kupu Contributors. All rights reserved.
 *
 * This software is distributed under the terms of the Kupu
 * License. See LICENSE.txt for license text. For a list of Kupu
 * Contributors see CREDITS.txt.
 *
 *****************************************************************************/

// $Id: kupusaveonpart.js 25438 2006-04-06 10:27:12Z guido $

function saveOnPart(event) {
    /* ask the user if (s)he wants to save the document before leaving */
    if (kupu.content_changed && !confirm(
            _('You have unsaved changes. Are you sure you want to ' +
                'leave the editor?')
            )) {
        kupu.config.reload_src = 0;
        if (event.stopPropagation) {
            event.stopPropagation();
        } else {
            event.returnValue = false;
        };

        if(event.preventDefault){
            event.preventDefault();
        }
        //return false;
    };
    return true;
};
