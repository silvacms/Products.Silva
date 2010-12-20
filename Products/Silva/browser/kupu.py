from Products.Five import BrowserView
from urllib import quote

class RenderExternalSource(BrowserView):
    def __call__(self):
        source_id = self.request.get("source_id", "")
        docref = self.request.get("docref", "")
        if source_id != "" and docref != "":
            del(self.request.form['source_id'])
            del(self.request.form['docref'])
            source = getattr(self.context, source_id, None)
            if source is None:
                return ""
            self.request["model"] = self.context.resolve_ref(quote(docref))
            if source.is_previewable():
                return source.to_html(self.request, **self.request.form)
        return ""
