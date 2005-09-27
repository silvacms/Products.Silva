function HandlerRegistry() {
    /* a small registry to register functions that should be called on
        certain events (e.g. onload on the body)
    */
    this.initialize();
};

HandlerRegistry.prototype.initialize = function() {
    this.handlers = [];
};

HandlerRegistry.prototype.register = function(handler, asfirst) {
    if (asfirst) {
        this.handlers.unshift(handler);
    } else {
        this.handlers.push(handler);
    };
};

HandlerRegistry.prototype.callHandlers = function() {
    for (var i=0; i < this.handlers.length; i++) {
        this.handlers[i]();
    };
};

window.onload_registry = new HandlerRegistry();
window.unonload_registry = new HandlerRegistry();
