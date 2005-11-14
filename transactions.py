"""Abstraction to allow more uniform handling of transactions
    across various versions of Zope.

    Eventually we will also need to switch to using use  savepoints
    rather than (deprecated) sub-transactions, though, which may be slightly
    trickier.
"""

try:  			# Zope 2.8 style transactions
    import transaction
except ImportError:  	# Old-style transactions
    class TransactionMan:
        def begin(self):                get_transaction().begin()
        def commit(self, sub=False):    get_transaction().commit(sub)
        def abort(self, sub=False):     get_transaction().abort(sub)
        def get(self):                  return get_transaction()
    transaction = TransactionMan()
