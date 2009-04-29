When changing the kupu templates, please run 'make all' in this directory
before checking in. This will rebuild the new templates. We want to
run make before checking in as it is important that Silva checkouts
work out of the box, which makes us do the slightly ugly thing of
checking in generated code.

When kupu is updated, we also need to rerun 'make all'.
