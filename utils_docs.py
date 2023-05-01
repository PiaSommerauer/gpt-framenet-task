from lxml import etree as et
import utils_naf


def get_text_names(incident_name, lang, inc2str, inc2label, inc2lang2doc):

    label2incid = dict()
    for inc_id, label in inc2label.items():
        label2incid[label] = inc_id

    inc_id = label2incid[incident_name]
    print(inc_id)
    docs = inc2lang2doc[inc_id][lang]

    print('Incident info')
    print(inc2str[inc_id])
    print()

    # for doc in docs:
    #     status = annotation_status_dict[doc]
    #     print(status, '\t', doc)
    return inc_id, docs


def show_docs_by_time(path_texts, docs, annotation_status_dict):
    doc_time_dict = dict()
    for doc in docs:
        status = annotation_status_dict[doc]
        if status == 'annotated-manual':
            path_naf = f'{path_texts}/{doc}.naf'
            tree = et.parse(path_naf)
            root = tree.getroot()
            doc_time = utils_naf.get_timestamp(root)
            doc_time_dict[doc_time] = doc
    sorted_doc_times = sorted(list(doc_time_dict.keys()))

    for t in sorted_doc_times:
        doc = doc_time_dict[t]
        status = annotation_status_dict[doc]
        print(t, doc, status)
    return doc_time_dict


def load_text(path_naf):
    tree = et.parse(path_naf)
    root = tree.getroot()
    text = utils_naf.get_text(root)
    return text