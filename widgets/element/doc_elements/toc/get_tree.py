##parameters=model=None, toc_depth=-1, public=0

if model:
    if public:
        return model.get_container().get_public_tree(toc_depth)
    else:
        return model.get_container().get_tree(toc_depth)

# shouldn't happen though...
return None
