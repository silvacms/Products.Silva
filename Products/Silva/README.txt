=====
Silva
=====

`Silva`_ is a Zope-based web application designed for the creation and
management of structured, textual content. Silva allows users to enter
new documents as well as edit existing documents using a web
interface.

Silva stores the content in a structured format, and keeps a strict
separation between the way the content is used and the way it is
presented. This leads to several important advantages:

* The same content can be used in different media, such as the web,
  paper, or word processor content. Web publication of content is
  native to Silva as it is based on Zope, but Silva also has export
  filters to various formats.

* The content is future proofed and not out of date as soon as you
  want to use a new system or present it in a different way.

* The structuring of the content facilitates more sophisticated
  searching and indexing.

Silva supports (but does not require) a separation between authors who
can create new content and editors who can approve whether content
actually gets published. It also allows delegation of editing or
authoring responsibilities of a section of the publication to
others. Thus, users can be empowered (avoiding a single-person
bottleneck), without the loss of editorial control.

To assist in the publication process, Silva implements workflow where
multiple versions of the same document are kept around at the same
time. One version of a particular document may be published while
another version can be edited at the same time.

Silva is extensible with new document types and other types of content
objects, others skins ...

For more information please consult the site: http://silvacms.org

Code repository
===============

You can find the code of this extension in Git:
https://github.com/silvacms/Products.Silva

.. _Silva: http://silvacms.org
