from Products.Five import BrowserView
from urllib import quote

class RenderExternalSource(BrowserView):
    def __call__(self):
        cs = self.request.get("source_id", "")
        docref = self.request.get("docref", "")
        if cs != "" and docref != "":
            del(self.request.form['source_id'])
            del(self.request.form['docref'])
            obj = getattr(self.context, cs)
            self.request["model"] = self.context.resolve_ref(quote(docref))
            if obj.is_previewable():
                return obj.to_html(self.request, **self.request.form)
        return ""
