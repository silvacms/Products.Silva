request = context.REQUEST
model = request.model

# have to do this to introduce backwards compatibility with membership
# services which do not have the use_direct_lookup method.

use_direct_lookup = getattr(model.service_members.aq_inner,
                            'use_direct_lookup', None)

if use_direct_lookup is None:
    return False

return use_direct_lookup()


