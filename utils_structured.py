import pandas as pd
import json

def load_structured_data(path_structured):
    
    type2inc_path = f'{path_structured}/type2inc_index.json'
    inc2str_path = f'{path_structured}/inc2str_index.json'

    type2label_path = f'{path_structured}/type2label.json'
    inc2label_path = f'{path_structured}/inc2label.json'

    inc2lang2doc_path = f'{path_structured}/inc2lang2doc_index.json'
    annotation_status_path = f'{path_structured}/annotation_status.json'

    with open(type2inc_path) as infile:
        type2inc = json.load(infile)

    with open(type2label_path) as infile:
        type2label = json.load(infile)

    with open(inc2label_path) as infile:
        inc2label = json.load(infile)

    with open(inc2lang2doc_path) as infile:
        inc2lang2doc = json.load(infile)

    with open(annotation_status_path) as infile:
        annotation_status_dict = json.load(infile)

    with open(f'{path_structured}/inc2str_index.json') as infile:
        inc2str = json.load(infile)
        
    return type2inc, type2label, inc2label, inc2lang2doc, annotation_status_dict, inc2str

def generate_overview(lang, type2inc, type2label, inc2label, inc2lang2doc, annotation_status_dict):
    table_data = []
    for ty_id, inc_ids in type2inc.items():
        ty_label = type2label[ty_id]
        # print(ty_id, ty_label)
        for inc_id in inc_ids:
            inc_label = inc2label[inc_id]
            status_cnt = dict()
            status_cnt['type'] = ty_label
            status_cnt['typeID'] = ty_id
            status_cnt['inc'] = inc_label
            status_cnt['incID'] = inc_id
            docs = inc2lang2doc[inc_id]
            if lang in docs:
                docs_lang = docs[lang]
            else:
                docs_lang = []
            # print(len(docs_lang))
            status_cnt['total'] = len(docs_lang)
            for doc in docs_lang:
                annotation_status = annotation_status_dict[doc]
                if annotation_status not in status_cnt:
                    status_cnt[annotation_status] = 1
                else:
                    status_cnt[annotation_status] += 1
            table_data.append(status_cnt)
    df = pd.DataFrame(table_data)
    path = f'overview_{lang}.csv'
    df.to_csv(path)
    print(f'table written to: {path}')
    return df