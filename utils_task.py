import itertools
from lxml import etree as et
import utils_docs
import utils_naf
import utils_task
import os
import json
import pandas as pd
from datetime import datetime

def get_frame_overlap(predicate_info1, predicate_info2):
    pair_dict = dict()
    
    frames1 = set([p_dict['frame'] for p_dict in predicate_info1])
    frames2 = set([p_dict['frame'] for p_dict in predicate_info2])
    pred_both = frames1.intersection(frames2)
    # print(len(pred_both))
    # print(len(frames1), len(frames2))

    fn_elements1 = set()
    fn_elements2 = set()

    for pred in predicate_info1:
        roles = pred['roles']
        elements = [role_dict['role'] for role_dict in roles]
        fn_elements1.update(elements)

    for pred in predicate_info2:
        roles = pred['roles']
        elements = [role_dict['role'] for role_dict in roles]
        fn_elements2.update(elements)  

    fn_elements_both = fn_elements1.intersection(fn_elements2)
    # print(len(fn_elements_both))
    
    pair_dict['shared_frames'] = pred_both
    pair_dict['shared_elements'] = fn_elements_both
    return pair_dict


def get_doc_pred_dict(path_texts, docs, inc_id):
    
    doc_pred_dict = dict()
    for doc in docs:
        path_naf = f'{path_texts}/{doc}.naf'
        #print(path_naf)
        if os.path.isfile(path_naf):
            tree = et.parse(path_naf)
            root = tree.getroot()
            pred_info = utils_naf.get_predicate_role_info(root, inc_id, anchor_filter=True)
            doc_pred_dict[doc] = pred_info
    return doc_pred_dict


def get_text_pairs(path_texts, docs1 = [], docs2 = None, inc1_id = None, inc2_id = None, inc1_time = None, inc2_time = None):
    # collect pairs
    data = []
    
    # create text pairs
    if docs2 is None:
        doc_pairs = itertools.combinations(docs1, 2)
        label = 1
        inc_ids = [inc1_id, inc1_id]
        # doc pred dict
        doc_pred_dict = get_doc_pred_dict(path_texts, docs1, inc1_id)
        # inc_doc_pred_dict = dict()
        # inc_doc_pred_dict = 
        inc_times = [inc1_time, inc1_time]
        
            
    else:
        doc_pairs = itertools.product(docs1, docs2)
        doc_pred_dict = get_doc_pred_dict(path_texts, docs1, inc1_id)
        doc_pred_dict2 = get_doc_pred_dict(path_texts, docs2, inc2_id)
        doc_pred_dict.update(doc_pred_dict2)
        #print(doc_pred_dict.keys())
        label = 0
        inc_ids = [inc1_id, inc2_id]
        inc_times = [inc1_time, inc2_time]
    
    for pair in doc_pairs:
        pair_dict = dict()
        pair_dict['label'] = label
        #print(pair)
        pred_info_dicts = []
        for n, doc in enumerate(pair):
            #print(doc)
            path_naf = f'{path_texts}/{doc}.naf'
            #print(path_naf)
            inc_time = inc_times[n]
            # check format:
            if len(inc_time) != 10:
                inc_time = '0001-01-01'
            
            inc_time_dt = datetime.strptime(inc_time, '%Y-%m-%d')
            
            # if not root is None:
            if os.path.isfile(path_naf):
                #print(inc_ids[n])
                predicate_info = doc_pred_dict[doc]
                tree = et.parse(path_naf)
                root = tree.getroot() 
                doc_time = utils_naf.get_timestamp(root)
                doc_time_str = doc_time.split('T')[0]
                if len(doc_time_str) != 10:
                    doc_time_str = '0001-01-01'
                doc_time_dt = datetime.strptime(doc_time_str, '%Y-%m-%d')
                dst = doc_time_dt - inc_time_dt
                
                if len(predicate_info) > 0:
                    pred_info_dicts.append(predicate_info)
                    pair_dict[f'title{n}'] = doc
                    pair_dict[f'text{n}'] = utils_docs.load_text(path_naf)
                    pair_dict[f'inc_id{n}'] = inc_ids[0]
                    pair_dict[f'temp_dist{n}'] = dst

        if len(pred_info_dicts) == 2:
            frame_dict = get_frame_overlap(pred_info_dicts[0], pred_info_dicts[1])
            total_overlap = len(frame_dict['shared_frames']) + len(frame_dict['shared_elements'])
            pair_dict['shared_frames'] = len(frame_dict['shared_frames'])
            pair_dict['shared_elements'] = len(frame_dict['shared_elements'])
            pair_dict['total_overlap'] = total_overlap
            data.append(pair_dict)
    return data, doc_pred_dict



def create_event_type_data(type_selected, overview_df, path_data, lang, inc2label, inc2lang2doc, inc2str, min_doc = 10):
    path_texts = f'{path_data}/{lang}'
    
    os.makedirs('task_data', exist_ok=True)
    type_selected_str = type_selected.replace(' ', '-')
    out_path = f'task_data/{type_selected_str}_{lang}.csv'
    path_frames = f'task_data/{type_selected_str}_{lang}_frames.json'
    incidents_id_dict = dict()
    overview_df.fillna(0)
    
    doc_pred_dict_all = dict()
    inc_inc_time_dict = dict()

    for i, row in overview_df.iterrows():
        et = row['type']
        n_annotated = row['annotated-manual']
        inc_time = row['inc_time']
        #print(n_annotated)
        if et == type_selected and n_annotated >= min_doc :
            incidents_id_dict[row['inc']] = row['incID']
            inc_inc_time_dict[row['incID']] = inc_time


    inc_combinations =  list(itertools.combinations(incidents_id_dict.keys(), 2))

    all_data = []

    for name, inc_id in incidents_id_dict.items():
        inc1_time = inc_inc_time_dict[inc_id]
        inc1_id, docs1 = utils_docs.get_text_names(name, lang, inc2str, inc2label, inc2lang2doc)
        data_same, doc_pred_dict = utils_task.get_text_pairs(path_texts, docs1 = docs1, inc1_id = inc1_id, inc1_time = inc1_time)
        #print(name, inc_id, len(data_same))
        all_data.extend(data_same)
        doc_pred_dict_all.update(doc_pred_dict)

    # different     
    for name1, name2 in inc_combinations:    
        inc1_id, docs1 = utils_docs.get_text_names(name1, lang, inc2str, inc2label, inc2lang2doc)
        inc2_id, docs2 = utils_docs.get_text_names(name2, lang, inc2str, inc2label, inc2lang2doc)
        inc1_time = inc1_time = inc_inc_time_dict[inc1_id]
        inc2_time = inc1_time = inc_inc_time_dict[inc2_id]
        data_different, pred_docs_different = utils_task.get_text_pairs(path_texts, docs1 = docs1, docs2 = docs2, 
                                                                        inc1_id = inc1_id, inc2_id = inc2_id, inc1_time = inc1_time, inc2_time = inc2_time)
        all_data.extend(data_different)
        doc_pred_dict_all.update(pred_docs_different)


    df = pd.DataFrame(all_data)
    df.to_csv(out_path)
    
    with open(path_frames, 'w') as outfile:
        json.dump(doc_pred_dict_all, outfile)
    
    print(f'Created dataset for event type: {type_selected}')
    print(f'Written dataset to: {out_path}')
    print(f'Frame info written to: {path_frames}')