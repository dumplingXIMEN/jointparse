

def get_parser_evaluation(predicted_list, gold_list):
    predict_gold_map, correct_count = map_predicted_with_gold_words(predicted_list, gold_list)
    pos_correct_count = get_pos_match(predicted_list, gold_list, predict_gold_map)
    uas_score, las_score = get_uas_las_match(predicted_list, gold_list, predict_gold_map)

    evaluation = dict()
    evaluation['predicted_list_len'] = len(predicted_list)
    evaluation['gold_list_len'] = len(gold_list)
    evaluation['correct_count'] = correct_count
    evaluation['precision'] = (correct_count / len(predicted_list)) * 100
    evaluation['recall'] = (correct_count / len(gold_list)) * 100
    evaluation['f1_score'] = get_f1_score(evaluation['precision'], evaluation['recall'])
    evaluation['pos_match'] = pos_correct_count
    evaluation['pos_acc'] = (pos_correct_count / correct_count) * 100 if correct_count > 0 else 0
    evaluation['uas_match'] = uas_score
    evaluation['uas_score'] = (uas_score / correct_count) * 100 if correct_count > 0 else 0
    evaluation['uas_precision'] = (uas_score / len(predicted_list)) * 100
    evaluation['uas_recall'] = (uas_score / len(gold_list)) * 100
    evaluation['uas_f1_score'] = get_f1_score(evaluation['uas_precision'], evaluation['uas_recall'])
    evaluation['las_match'] = las_score
    evaluation['las_score'] = (las_score / correct_count) * 100 if correct_count > 0 else 0
    evaluation['las_precision'] = (las_score / len(predicted_list)) * 100
    evaluation['las_recall'] = (las_score / len(gold_list)) * 100
    evaluation['las_f1_score'] = get_f1_score(evaluation['las_precision'], evaluation['las_recall'])

    return evaluation


def get_epoch_evaluation(evaluation_list):
    epoch_eval = dict()
    n_eval = len(evaluation_list)

    epoch_eval['word_precision'] = (sum(x['precision'] for x in evaluation_list) / n_eval)
    epoch_eval['word_recall'] = (sum(x['recall'] for x in evaluation_list) / n_eval)
    epoch_eval['word_f1_score'] = (sum(x['f1_score'] for x in evaluation_list) / n_eval)
    epoch_eval['pos_accuracy'] = (sum(x['pos_acc'] for x in evaluation_list) / n_eval)
    epoch_eval['uas_accuracy'] = (sum(x['uas_score'] for x in evaluation_list) / n_eval)
    epoch_eval['las_accuracy'] = (sum(x['las_score'] for x in evaluation_list) / n_eval)
    epoch_eval['uas_f1_score'] = (sum(x['uas_f1_score'] for x in evaluation_list) / n_eval)
    epoch_eval['las_f1_score'] = (sum(x['las_f1_score'] for x in evaluation_list) / n_eval)

    epoch_eval['correct_words'] = sum([x['correct_count'] for x in evaluation_list])
    epoch_eval['all_gold_words'] = sum([x['gold_list_len'] for x in evaluation_list])
    epoch_eval['all_predicted_words'] = sum([x['predicted_list_len'] for x in evaluation_list])
    epoch_eval['correct_pos'] = sum([x['pos_match'] for x in evaluation_list])
    epoch_eval['correct_uas'] = sum([x['uas_match'] for x in evaluation_list])
    epoch_eval['correct_las'] = sum([x['las_match'] for x in evaluation_list])

    return epoch_eval


def map_predicted_with_gold_words(predicted_list, gold_list):
    """
    :param predicted_list: a list of word_info for predicted words
    :param gold_list: a list of word_info for gold standard words
    :return: - a list mapped from word no. in predicted set to word no. in gold set, None if no word match
             - number of correctly segmented words
    """
    predicted_index_map = generate_start_end_map([word_info['word'] for word_info in predicted_list])
    gold_index_map = generate_start_end_map([word_info.word for word_info in gold_list])

    correct_count = 0
    two_set_map = [None] * (len(predicted_list) + 1)
    two_set_map[0] = 0  # Match ROOT - ROOT

    for start_idx in range(len(predicted_index_map)):
        end_idx = predicted_index_map[start_idx]['end']
        predicted_word_idx = predicted_index_map[start_idx]['word_idx']

        if end_idx is not None and gold_index_map[start_idx]['end'] == end_idx:
            gold_word_idx = gold_index_map[start_idx]['word_idx']
            two_set_map[predicted_word_idx + 1] = gold_word_idx + 1  # word is 1-based (0 is for ROOT)
            correct_count += 1

    return two_set_map, correct_count


def generate_start_end_map(data_list):
    """
    :param data_list: a list of words
    :return: data_map: a list of dict {end_idx, word_idx} for each start_idx
    """
    n_len = sum([len(word) for word in data_list])
    data_map = [{'end': None, 'word_idx': None} for _ in range(n_len)]

    last_idx = 0
    for word_idx, word in enumerate(data_list):
        start_idx = last_idx
        end_idx = start_idx + len(word)

        data_map[start_idx]['end'] = end_idx
        data_map[start_idx]['word_idx'] = word_idx

        last_idx = end_idx

    return data_map


def get_pos_match(predicted_list, gold_list, predict_gold_map):
    correct_count = 0

    for word_idx, word_info in enumerate(predicted_list):
        word_gold_index = predict_gold_map[word_idx + 1]

        if word_gold_index is not None:
            predicted_pos = word_info['pos']
            gold_pos = gold_list[word_gold_index - 1].pos
            if predicted_pos == gold_pos:
                correct_count += 1

    return correct_count


def get_uas_las_match(predicted_list, gold_list, predict_gold_map):
    uas_count = 0
    las_count = 0
    for word_idx, word_info in enumerate(predicted_list):
        word_gold_index = predict_gold_map[word_idx + 1]

        if word_gold_index is not None:
            predicted_head_node = word_info['head_idx']
            predicted_dep_label = word_info['dep_label']

            gold_head_node = gold_list[word_gold_index - 1].head_idx
            gold_dep_label = gold_list[word_gold_index - 1].dep_label

            if predict_gold_map[predicted_head_node] == gold_head_node:
                uas_count += 1

                if predicted_dep_label == gold_dep_label:
                    las_count += 1

    return uas_count, las_count


def get_f1_score(precision, recall):
    if precision + recall > 0:
        return (2 * (precision * recall)) / (precision + recall)
    else:
        return 0
