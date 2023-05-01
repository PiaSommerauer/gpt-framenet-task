
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