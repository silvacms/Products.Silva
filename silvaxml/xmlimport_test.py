import silva_xmlimport

def main():
    root = silva_xmlimport.test('data/test1.xml')
    testfolder = root.getItems()[0]
    assert testfolder._metadata['silva_extra']['creator'] == 'test_user_1_'
    assert testfolder.id == 'testfolder'
    assert testfolder.getTitle() == 'foldertitle'
    link = testfolder.getItems()[0]
    assert link.id == 'link'
    version = link.getVersion('0')
    assert version.getUrl() == 'http://www.infrae.com'
    workflow_version = link.getWorkflow()['0']
    assert workflow_version[0] == 'unapproved'
    assert version.getTitle() == 'linktitle'
    assert version._metadata['silva_metadata']['shorttitle'] == 'lnkttl'
if __name__ == '__main__':
    main()