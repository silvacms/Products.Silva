/* a set of helper functions that should be available on all edit pages */

// can be attached to formfields so that pressing enter makes the form use
// a specific action, useful in forms with more than 1 submit button
function handle_default_action(element, event, action)
{
    code = event.which ? event.which : event.keyCode;
    if (code == 10 || code == 13)
    {
        element.form.action = action;
        element.form.submit();
    }
}

