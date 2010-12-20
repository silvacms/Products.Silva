if (![].indexOf) {
    Array.prototype.indexOf = function indexOf(el) {
        for (var i=0; i < this.length; i++) {
            if (this[i] == el) {
                return i;
            };
        };
        return -1;
    };
};

function debug(msg) {
    if (window.console && console.log) {
        console.log(msg);
    };
};

function raise(exc, msg, remove_stack_depth) {
    if (remove_stack_depth === undefined) {
        remove_stack_depth = 1;
    };
    try {
        thishopefullydoesnotexist();
    } catch(e) {
        if (!e.stack) {
            // non-Moz
            throw(exc + ': ' + msg);
        };
        var stack = e.stack;
        var lines = stack.split('\n');
        lines = lines.slice(remove_stack_depth);
        e.name = exc;
        e.message = msg;
        e.stack = lines.join('\n');
        throw(e);
    };
};

function str_escape(s) {
    /* escapes quotes and special chars (\n, \a, \r, \t, etc.)

        adds double slashes
    */
    // XXX any more that need escaping?
    s = s.replace(/\\/g, '\\\\');
    s = s.replace(/\n/g, '\\\n');
    s = s.replace(/\r/g, '\\\r');
    s = s.replace(/\t/g, '\\\t');
    s = s.replace(/'/g, "\\'");
    s = s.replace(/"/g, '\\"');
    return s;
};

function repr(o, visited) {
    var newid = 0;
    if (visited === undefined) {
        visited = {};
    };
    // XXX oomph... :|
    for (var attr in visited) {
        if (visited[attr] === o) {
            return '#' + attr + '#';
        };
        newid++;
    };
    var ret = 'unknown?';
    if (o === null) {
        ret = 'null';
    } else {
        var type = typeof o;
        switch (type) {
            case 'undefined':
                ret = 'undefined'
                break;
            case 'string':
                ret = '"' + str_escape(o) + '"';
                break;
            case 'object':
                if (o instanceof Array) {
                    if (visited) {
                        visited[newid] = o;
                    };
                    var r = [];
                    for (var i=0; i < o.length; i++) {
                        var newo = o[i];
                        r.push(repr(newo, visited));
                    };
                    ret = ''
                    if (visited) {
                        ret += '#' + newid + '=';
                    };
                    ret += '[' + r.join(', ') + ']';
                } else if (o instanceof Date) {
                    ret = '(new Date(' + o.valueOf() + '))';
                } else {
                    if (visited) {
                        visited[newid] = o;
                    };
                    var r = [];
                    for (var attr in o) {
                        try {
                            var newo = o[attr];
                            r.push(attr + ': ' +
                                repr(newo, visited));
                        } catch(e) {
                            if (e.message &&
                                    e.message == 'too much recursion') {
                                // XXX how does this work in other
                                // browsers?
                                throw(e);
                            };
                            r.push(attr + ': <unknown>');
                        };
                    };
                    ret = '';
                    if (visited) {
                        ret += '#' + newid + '=';
                    };
                    ret += '{' + r.join(', ') + '}';
                };
                break;
            default:
                ret = o.toString();
                break;
        };
    };
    return ret;
};

function cmp(o1, o2) {
    var attrs = [];
    if (typeof o1 != typeof o2) {
        return false;
    };
    for (var attr in o1) {
        if (o1[attr] !== o2[attr]) {
            return false;
        };
        attrs.push(attr);
    };
    for (var attr in o2) {
        if (attrs.indexOf(attr) == -1) {
            return false;
        };
    };
    return true;
};

function assert(statement) {
    if (!statement) {
        raise('AssertionError', 'false assertion');
    };
};

function assertEquals(var1, var2, userepr) {
    if (!cmp(var1, var2)) {
        if (!userepr || repr(var1) != repr(var2)) {
            raise('AssertionError', var1 + ' != ' + var2);
        };
    };
};

var global = this;
function run_tests(tests) {
    var outcomediv = document.getElementById('tests_outcome');
    for (var i=0; i < tests.length; i++) {
        var testname = tests[i];
        var test = global[testname];
        var error = null;
        try {
            test();
        } catch(e) {
            error = e;
        };
        var resdiv = document.createElement('div');
        var msg = testname + ': ';
        if (error) {
            msg += 'ERROR: ' + error;
            var msgdiv = document.createElement('div');
            msgdiv.appendChild(document.createTextNode(msg));
            msgdiv.style.color = 'red';
            resdiv.appendChild(msgdiv);
            var pre = document.createElement('pre');
            pre.appendChild(document.createTextNode(error.stack));
            pre.style.marginLeft = '2em';
            resdiv.appendChild(pre);
        } else {
            msg += 'success';
            var msgdiv = document.createElement('div');
            msgdiv.appendChild(document.createTextNode(msg));
            msgdiv.style.color = 'green';
            resdiv.appendChild(msgdiv);
        };
        outcomediv.appendChild(resdiv);
    };
};
