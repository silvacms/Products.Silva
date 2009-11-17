function DummyEditor() {
    this.inserted = [];
    this.logmessages = [];
    this.selectedNode = null;
};

DummyEditor.prototype = new KupuEditor;

DummyEditor.prototype.insertNodeAtSelection =
        function insertNodeAtSelection(node) {
    this.inserted.push(node);
};

DummyEditor.prototype.updateState = function updateState() {
};

DummyEditor.prototype.logMessage = function logMessage(msg) {
    this.logmessages.push(msg);
};

DummyEditor.prototype.getInnerDocument = function getInnerDocument() {
    return document;
};

DummyEditor.prototype.getSelection = function getSelection() {
    var self = this;
    return {
        cloneContents: function() {
            return self.selectedNode;
        },
        selectNodeContents: function(node) {self.selectedNode = node},
        collapse: function() {}
    };
};

DummyEditor.prototype.getSelectedNode = function getSelectedNode() {
    return this.selectedNode;
};

function test_create_table() {
    var e = new DummyEditor();
    var t = new SilvaTableTool();
    t.initialize(e);
    e.selectedNode = document.createElement('div');
    t.createTable(2, 2, false, 'grid');
    var table = e.inserted[0];
    assertEquals(table.nodeName, 'TABLE');
    assertEquals(table.className, 'grid');
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>\ufeff</td><td>\ufeff</td></tr>' +
        '<tr><td>\ufeff</td><td>\ufeff</td></tr></tbody>');

    t.createTable(1, 2, true, 'grid');
    var table = e.inserted[1];
    assertEquals(
        table.innerHTML,
        '<tbody><tr><th colspan="2">\ufeff</th></tr><tr>' +
        '<td>\ufeff</td><td>\ufeff</td></tr></tbody>');
};

// not in Silva, but I don't fully trust this function...
function test__getColIndex() {
    var e = new DummyEditor();
    var t = new SilvaTableTool();
    t.initialize(e);

    var table = document.createElement('table');
    table.innerHTML =
        '<tbody><tr> <td>foo</td> <td>bar</td> <td>baz</td> </tbody></tr>';
    var tds = table.getElementsByTagName('td');
    assertEquals(t._getColIndex(tds[0]), 0);
    assertEquals(t._getColIndex(tds[2]), 2);
    tds[1].colSpan = 2;
    assertEquals(t._getColIndex(tds[2]), 3);
};

function test__factorWidths() {
    var e = new DummyEditor();
    var t = new SilvaTableTool();
    t.initialize(e);

    assertEquals(t._factorWidths([1, 2, 3]), [1, 2, 3]);
    assertEquals(t._factorWidths([2, 2, 4]), [1, 1, 2]);
    assertEquals(t._factorWidths([33, 66, 11]), [3, 6, 1]);
    assertEquals(t._factorWidths([33, 33, 33]), [1, 1, 1]);
};

function test_mergeTableCell() {
    var e = new DummyEditor();
    var t = new SilvaTableTool();
    t.initialize(e);

    e.selectedNode = document.createElement('div');
    t.createTable(2, 2, false, 'grid');
    var table = e.inserted[0];
    table.innerHTML = '<tbody><tr><td>foo</td><td>bar</td></tr></tbody>';

    t.mergeTableCell(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td colspan="2">foo<br>bar</td></tr></tbody>');

    t.mergeTableCell(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td colspan="2">foo<br>bar</td></tr></tbody>');

    var table = document.createElement('table');
    table.innerHTML =
        '<tbody><tr><th>foo</th><th>bar</th></tr>' +
        '<tr><td>1</td><td>2</td></tr></tbody>';
    t.mergeTableCell(table.getElementsByTagName('th')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><th colspan="2">foo<br>bar</th></tr>' +
        '<tr><td>1</td><td>2</td></tr></tbody>');

    table.innerHTML =
        '<tbody><tr><th colspan="2">foo</th><th>bar</th></tr>' +
        '<tr><td>1</td><td>2</td><td>3</td></tr></tbody>';
    t.mergeTableCell(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><th colspan="2">foo</th><th>bar</th></tr>' +
        '<tr><td colspan="2">1<br>2</td><td>3</td></tr></tbody>');
};

function test_splitTableCell() {
    var e = new DummyEditor();
    var t = new SilvaTableTool();
    t.initialize(e);

    var table = document.createElement('table');
    table.innerHTML =
        '<tbody><tr><td colspan="2">foo</td><td>bar</td></tr></tbody>';
    t.splitTableCell(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>foo</td><td>\ufeff</td><td>bar</td></tr></tbody>');

    table.innerHTML = '<tbody><tr><td>foo</td></tr></tbody>';
    t.splitTableCell(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>foo</td></tr></tbody>');

    table.innerHTML =
        '<tbody><tr><td colspan="2">foo</td><td>bar</td></tr></tbody>';
    t.splitTableCell(table.getElementsByTagName('td')[1]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td colspan="2">foo</td><td>bar</td></tr></tbody>');

    table.innerHTML =
        '<tbody><tr><td colspan="2">foo</td><td>bar</td></tr>' +
        '<tr><td>1</td><td>2</td><td>3</td></tr></tbody>';
    t.splitTableCell(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>foo</td><td>\ufeff</td><td>bar</td></tr>' +
        '<tr><td>1</td><td>2</td><td>3</td></tr></tbody>');

    table.innerHTML =
        '<tbody><tr><td>1</td><td colspan="2">2</td></tr></tbody>';
    t.splitTableCell(table.getElementsByTagName('td')[1]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>1</td><td>2</td><td>\ufeff</td></tr></tbody>');
};

function test_delTableColumn() {
    var e = new DummyEditor();
    var t = new SilvaTableTool();
    t.initialize(e);

    var table = document.createElement('table');

    table.setAttribute('silva_column_info', 'L:1 L:1');
    table.innerHTML = '<tbody><tr><td>foo</td><td>bar</td></tr></tbody>';
    e.selectedNode = table.getElementsByTagName('td')[0];
    t.delTableColumn(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>bar</td></tr></tbody>');

    table.setAttribute('silva_column_info', 'L:1 L:1 L:1');
    table.innerHTML =
        '<tbody><tr><td colspan="2">foo</td><td>bar</td></tr></tbody>';
    t.delTableColumn(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>foo</td><td>bar</td></tr></tbody>');

    table.innerHTML =
        '<tbody><tr><th colspan="3">foo</th></tr>' +
        '<tr><td>1</td><td>2</td><td>3</td></tr></tbody>';
    t.delTableColumn(table.getElementsByTagName('td')[2]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><th colspan="2">foo</th></tr>' +
        '<tr><td>1</td><td>2</td></tr></tbody>');

    table.innerHTML =
        '<tbody><tr><th colspan="2">foo</th><th>bar</th></tr>' +
        '<tr><td>1</td><td>2</td><td>3</td></tr></tbody>';
    t.delTableColumn(table.getElementsByTagName('td')[2]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><th colspan="2">foo</th></tr>' +
        '<tr><td>1</td><td>2</td></tr></tbody>');

    table.innerHTML = '<tbody><tr><td>foo</td></tr></tbody>';
    t.delTableColumn(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>foo</td></tr></tbody>');
};

function test_addTableColumn() {
    var e = new DummyEditor();
    var t = new SilvaTableTool();
    t.initialize(e);

    var table = document.createElement('table');

    table.setAttribute('silva_column_info', 'L:1 L:1');
    table.innerHTML = '<tbody><tr><td>foo</td><td>bar</td></tr></tbody>';
    e.selectedNode = table.getElementsByTagName('td')[0];
    t.addTableColumn(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>foo</td><td>\ufeff</td><td>bar</td></tr></tbody>');

    table.setAttribute('silva_column_info', 'L:1 L:1 L:1');
    table.innerHTML =
        '<tbody><tr><th colspan="2">foo</th><th>bar</th></tr>' +
        '<tr><td>1</td><td>2</td><td>3</td></tr></tbody>';
    e.selectedNode = table.getElementsByTagName('td')[0];
    t.addTableColumn(table.getElementsByTagName('td')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><th colspan="2">foo</th><th>\ufeff</th><th>bar</th></tr>' +
        '<tr><td>1</td><td>\ufeff</td><td>2</td><td>3</td></tr></tbody>');

    table.setAttribute('silva_column_info', 'L:1 L:1 L:1');
    table.innerHTML =
        '<tbody><tr><th colspan="2">foo</th><th>bar</th></tr>' +
        '<tr><td>1</td><td>2</td><td>3</td></tr></tbody>';
    e.selectedNode = table.getElementsByTagName('td')[1];
    t.addTableColumn(table.getElementsByTagName('td')[1]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><th colspan="2">foo</th><th>\ufeff</th><th>bar</th></tr>' +
        '<tr><td>1</td><td>2</td><td>\ufeff</td><td>3</td></tr></tbody>');

    table.setAttribute('silva_column_info', 'L:1');
    table.innerHTML = '<tbody><tr><th>foo</th></tr></tbody>';
    e.selectedNode = table.getElementsByTagName('th')[0];
    t.addTableColumn(table.getElementsByTagName('th')[0]);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><th>foo</th><th>\ufeff</th></tr></tbody>');
};

function test_changeCellType() {
    var e = new DummyEditor();
    var t = new SilvaTableTool();
    t.initialize(e);

    e.selectedNode = document.createElement('div');
    t.createTable(1, 2, false, 'grid');
    var table = e.inserted[0];

    e.selectedNode = table.getElementsByTagName('td')[1].childNodes[0];
    t.changeCellType('th');
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>\ufeff</td><th>\ufeff</th></tr></tbody>');

    e.selectedNode.innerHTML = '<strong>foo</strong><em>bar</em>';
    t.changeCellType('td');
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>\ufeff</td><td>' +
        '<strong>foo</strong><em>bar</em></td></tr></tbody>');

    e.selectedNode.innerHTML = '\ufeff';
    t.changeCellType('td');
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td>\ufeff</td><td>\ufeff</td></tr></tbody>');
};

function test_setColumnWidths() {
    var e = new DummyEditor();
    var t = new SilvaTableTool();
    t.initialize(e);

    var table = document.createElement('table');
    table.setAttribute('silva_column_info', 'L:1');
    table.innerHTML = '<tbody><tr><td>foo</td></tr></tbody>';

    var td = table.getElementsByTagName('td')[0];
    e.selectedNode = td;
    t.addTableColumn(td);
    assertEquals(table.getAttribute('silva_column_info'), 'L:1 L:1');

    var table = document.createElement('table');
    table.setAttribute('silva_column_info', 'L:1');
    table.innerHTML = '<tbody><tr><td>foo</td></tr></tbody>';

    var td = table.getElementsByTagName('td')[0];
    td.width = '100%';
    t.addTableColumn(td);
    assertEquals(table.getAttribute('silva_column_info'), 'L:1 L:1');

    td.width = '50%';
    table.getElementsByTagName('td')[1].width = '50%';
    t.addTableColumn(td);
    assertEquals(table.getAttribute('silva_column_info'), 'L:1 L:1 L:1');

    td.width = '25%';
    table.getElementsByTagName('td')[1].width = '50%';
    table.getElementsByTagName('td')[2].width = '25%';
    table.removeAttribute('silva_column_info');
    var colinfo = t._getColumnInfo(table);
    t._setColumnInfo(table, colinfo);
    assertEquals(colinfo, [['left', 1], ['left', 2], ['left', 1]], true);

    t.delTableColumn(td);
    assertEquals(table.getAttribute('silva_column_info'), 'L:2 L:1');

    table.innerHTML =
        '<tbody><tr><td>foo</td><td colspan="2">bar</td></tr>' +
        '<tr><td colspan="2">spam</td><td>eggs</td></tr></tbody>';
    table.removeAttribute('silva_column_info');
    var colinfo = t._getColumnInfo(table);
    t._setColumnInfo(table, colinfo);
    assertEquals(table.getAttribute('silva_column_info'), 'L:1 L:1 L:1');

    table.setAttribute('silva_column_info', 'L:1 L:2 L:1');
    var colinfo = t._getColumnInfo(table);
    t._setColumnInfo(table, colinfo);
    t._updateTableFromInfo(table);
    assertEquals(
        table.innerHTML,
        '<tbody><tr><td width="25%">foo</td>' +
        '<td colspan="2" width="75%">bar</td></tr>' +
        '<tr><td colspan="2" width="75%">spam</td>' +
        '<td width="25%">eggs</td></tr></tbody>');

    table.removeAttribute('silva_column_info');
    table.innerHTML =
        '<tbody><tr><th colspan="3">head</th></tr>' +
        '<tr><td>foo</td><td>bar</td><td>baz</td></tr>' +
        '<tr><td>spam</td><td>eggs</td><td>spam</td></tr></tbody>';
    var colinfo = t._getColumnInfo(table);
    t._setColumnInfo(table, colinfo);
    assertEquals(table.getAttribute('silva_column_info'), 'L:1 L:1 L:1');
};

var kupu_tests = [
    'test_create_table',
    'test_mergeTableCell',
    'test_splitTableCell',
    'test_delTableColumn',
    'test_addTableColumn',
    'test__getColIndex',
    'test__factorWidths',
    'test_changeCellType',
    'test_setColumnWidths'
];
