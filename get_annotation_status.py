from lxml import etree as et
import os
import json

def load_doc(path_text, lang, doc_name):
    path_doc = f'{path_text}{lang}/{doc_name}.naf'
    if os.path.isfile(path_doc):
        tree = et.parse(path_doc)
    else:
        tree = None
    return tree

def get_srl(tree):
    
    root = tree.getroot()
    srl = root.find('srl')
    return srl


def check_if_annotated(path_text, lang, doc_name):
    
    tree = load_doc(path_text, lang, doc_name)
    status = 'file not found'
    if tree is not None:
        status = 'file exists'
        srl = get_srl(tree)
        if srl is not None:
            status = 'annotated'
            predicates = srl.findall('predicate')
            sources = set([p.get('status') for p in predicates])
            if 'manual' in sources:
                source = 'manual'
            elif 'deprecated' in sources:
                source = 'deprecated'
            else:
                source = 'system'
            status = f'{status}-{source}'
    return status



inc2doc = '../DFNDataReleases/structured/inc2lang2doc_index.json'
path_text = '../DFN_Annotations/unstructured/'

with open(inc2doc) as infile:
    inc2doc_dict = json.load(infile)


annotation_status_dict = dict()
for inc, lang_doc_dict in inc2doc_dict.items():
    for lang, docs in lang_doc_dict.items():
        for doc in docs:
            status = check_if_annotated(path_text, lang, doc)
            annotation_status_dict[doc] = status
            
path = '../DFNDataReleases/structured/'
with open(f'{path}annotation_status.json', 'w') as outfile:
    json.dump(annotation_status_dict, outfile)