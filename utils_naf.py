from collections import defaultdict


def get_text(root):
    text = root.find('raw').text
    return text
        
        
def get_timestamp(root):
    doc_time = root.find('nafHeader/fileDesc').get('creationtime')
    return doc_time

def get_srl(root):
    srl = root.find('srl')
    return srl
    
def get_term_dict(root):
    
    term_dict = dict()
    #tok_dict = dict()
    terms = root.find('terms')
    toks = root.find('text')
    for t in toks.getchildren():
        w = t.text
        wid = t.get('id').replace('w', 't')
        term_dict[wid] = w
    return term_dict

def get_term_mw_dict(root):
    terms = root.findall('terms/term')
    multiwords = root.findall('multiwords/mw')
    term_mw_dict = defaultdict(set)
    for term in terms:
        #print(term.attrib)
        if 'component_of' in term.attrib:
            # get mw info:
            #print(term.get('id'), term.get('component_of'))
            term_mw_dict[term.get('id')].add(term.get('component_of'))
    for mw in multiwords:
        components = mw.findall('component')
        for component in components:
            mw_id = component.get('id').split('.')[0]
            targets = component.findall('span/target')
            for target in targets:
                term_id = target.get('id')
                term_mw_dict[term_id].add(mw_id)
    return term_mw_dict


def get_coref(root):
    coref = root.find('coreferences')
    return coref

def get_tok_coref_dict(root):
    tok_coref_dict = dict()
    coref = get_coref(root)
    for co in coref.getchildren():
    #print(co.tag, co.attrib)
        co_id = co.get('id')

        span = co.find('span')
        ref = co.find('externalReferences/externalRef')
        ref_id = ref.get('reference')

        for el in span.getchildren():
            t_id = el.get('id')
            tok_coref_dict[t_id] = ref_id
    return tok_coref_dict

def get_predicate_info(predicate, tok_coref_dict, term_dict, term_mw_dict, event_q):
    
    predicate_dict = dict()
    
    ref = predicate.find('externalReferences/externalRef')
    span = predicate.find('span')
    source = ref.get('source')
    
    fn = ref.get('reference')
    ref_type = ref.get('reftype')
    
    predicate_dict['frame'] = fn
    predicate_dict['source'] = source
    predicate_dict['toks'] = []
    predicate_dict['tok_ids'] = []
    predicate_dict['coref_chain'] = set()
    predicate_dict['coref_ids'] = set()
    coref_ids = set()
    
    all_mw_ids = set()
    for term, mws in term_mw_dict.items():
        all_mw_ids.update(mws)
    #print(all_mw_ids)
    
    targets = span.findall('target')
    for t in targets:
        target_span = t.get('id')
        tok_ids = []
        # if target_span.startswith('mw'):
        #     print('multiword target span', target_span)
        #     print(term_mw_dict)
        if target_span in all_mw_ids:
            #print('found multiword!', target_span)
            tok_ids = [tok_id for tok_id, mw_ids in term_mw_dict.items() if target_span in mw_ids]
        else:
            tok_ids = [target_span]
        for tok_id in tok_ids:
            tok_id = tok_id.split('.')[0]
            w = term_dict[tok_id]
            predicate_dict['toks'].append(w.strip())
            predicate_dict['tok_ids'].append(tok_id)

            if tok_id in tok_coref_dict:
                coref = tok_coref_dict[tok_id]
                coref_ids.add(coref)
                for tok_id, cf in tok_coref_dict.items():
                    if '.' in tok_id:
                        tok_id = tok_id.split('.')[0]
                    if tok_id in all_mw_ids:
                        for term, mws in term_mw_dict.items():
                            if tok_id in mws:
                                tok_id = term
                                break
                    if cf == coref:
                        #print(cf, coref)
                        if tok_id in term_dict:
                            predicate_dict['coref_chain'].add(term_dict[tok_id].strip())
                            predicate_dict['coref_ids'].add(tok_id) 
                        # else:
                        #     print('could not find tok_id', tok_id)
                # predicate_dict['coref_chain'].update([term_dict[tok_id].strip() for tok_id, cf in tok_coref_dict.items() if cf == coref])
                # predicate_dict['coref_ids'].update([tok_id for tok_id, cf in tok_coref_dict.items() if cf == coref])
    if event_q in coref_ids:
        predicate_dict['anchor'] = True
    else:
        predicate_dict['anchor'] = False
    return predicate_dict
    
    
def get_role_info(role, tok_coref_dict, term_dict, term_mw_dict, event_q):
    
    role_dict = dict()

    ref = role.find('externalReferences/externalRef')
    span = role.find('span')
    source = ref.get('source')
    
    role_name = ref.get('reference')
    ref_type = ref.get('reftype')
    
    role_dict['role'] = role_name
    role_dict['source'] = source
    role_dict['toks'] = []
    role_dict['tok_ids'] = []
    role_dict['coref_chain'] = set()
    role_dict['coref_ids'] = set()
    coref_ids = set()
    
    all_mw_ids = set()
    for term, mws in term_mw_dict.items():
        all_mw_ids.update(mws)
    
    targets = span.findall('target')
    #print('found role targets', len(targets))
    for t in targets:
        target_span = t.get('id')
        #print(target_span)
        if '.' in target_span:
            target_span = target_span.split('.')[0]
        # if not target_span.startswith('t'):
        #     print(target_span)
        #w = term_dict[target_span]
        
        # tok_ids = []
        # if target_span.startswith('mw'):
        #     print(target_span)
        if target_span in all_mw_ids:
            #print('found mw!', target_span)
            tok_ids = [tok_id for tok_id, mw_ids in term_mw_dict.items() if target_span in mw_ids]
        else:
            tok_ids = [target_span]
        for tok_id in tok_ids:
            tok_id = tok_id.split('.')[0]
            w = term_dict[tok_id]
            role_dict['toks'].append(w.strip())
            role_dict['tok_ids'].append(tok_id)

            if tok_id in tok_coref_dict:
                coref = tok_coref_dict[tok_id]
                coref_ids.add(coref)
                for tok_id, cf in tok_coref_dict.items():
                    if '.' in tok_id:
                        tok_id = tok_id.split('.')[0]
                    if tok_id in all_mw_ids:
                        for term, mws in term_mw_dict.items():
                            if tok_id in mws:
                                tok_id = term
                                break
                    if cf == coref:
                        if tok_id in term_dict:
                            role_dict['coref_chain'].add(term_dict[tok_id].strip())
                            role_dict['coref_ids'].add(tok_id) 
                        # else:
                        #     print('could not find tok_id', tok_id)
    if event_q in coref_ids:
        role_dict['anchor'] = True
    else:
        role_dict['anchor'] = False
    return role_dict
    

def get_predicate_role_info(root, event_q, anchor_filter=True):
    
    predicate_role_info = []
    
    srl = get_srl(root)
    coref_layer = root.findall('coreferences/coref')
    if not srl is None and len(coref_layer) > 0:
        predicates = srl.findall('predicate')
        tok_coref_dict = get_tok_coref_dict(root)
        term_dict = get_term_dict(root)
        term_mw_dict = get_term_mw_dict(root)
        #print(term_mw_dict)
        for predicate in predicates:
            pred_dict = get_predicate_info(predicate, tok_coref_dict, term_dict, term_mw_dict, event_q)
            roles = predicate.findall('role')
            pred_dict['roles'] = []
            for role in roles:
                role_dict = get_role_info(role, tok_coref_dict, term_dict, term_mw_dict, event_q)
                pred_dict['roles'].append(role_dict)
            if pred_dict['anchor'] == True:
                predicate_role_info.append(pred_dict)
            else:
                if any([role_dict['anchor'] == True for role_dict in pred_dict['roles']]):
                    predicate_role_info.append(pred_dict)
    else:
        print('No srl layer')
    return predicate_role_info