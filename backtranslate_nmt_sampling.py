from args import get_nmt_args
from backtranslate_util import *
import util
# from transformers import DistilBertTokenizerFast


def nmt_sampling(beam=1):
    args = get_nmt_args(beam)
    
    # sampling
    sample_idx, sample_context_individual_length, gold_answers, answer_locs = sample_dataset(args, args.train_datasets, args.train_dir,
                                                                                             args.sample_queries_dir, args.sample_context_dir, 
                                                                                             args.sample_prob, args.seed)

    # forward translation
    keep_index_1 = get_keep_index(args.trans_queries_dir, args.trans_context_dir, sample_context_individual_length,
                              args.dropped_queries_dir, args.dropped_context_dir)
    sample_idx, dropped_context_individual_length, gold_answers, answer_locs = clean_lists(keep_index_1, [sample_idx, sample_context_individual_length, gold_answers, answer_locs])
    print('Num of examples after translation:', len(keep_index_1))

    # back translation
    keep_index_2 = get_keep_index(args.back_trans_queries_dir, args.back_trans_context_dir, dropped_context_individual_length,
                              args.back_dropped_queries_dir, args.back_dropped_context_dir)
    sample_idx, dropped_context_individual_length, gold_answers, answer_locs = clean_lists(keep_index_2, [sample_idx, dropped_context_individual_length, gold_answers, answer_locs])
    print('Num of examples after back translation:', len(keep_index_2))

    # estimate new answers
    keep_index_3, new_answers = get_trans_context_answers(args.back_dropped_context_dir, dropped_context_individual_length, 
                                                          gold_answers, answer_locs, args.jaccard_threshold)
    drop_files(keep_index_3, args.back_dropped_queries_dir, args.back_dropped_context_dir,
               args.jaccard_queries_dir, args.jaccard_context_dir, dropped_context_individual_length)
    sample_idx, dropped_context_individual_length, gold_answers, answer_locs = clean_lists(keep_index_3, [sample_idx, dropped_context_individual_length, gold_answers, answer_locs])
    print('Num of examples after filtering by Jaccard similarity:', len(keep_index_3))

    # compute queries and context BLEU
    
    keep_index_23 = [elem for idx, elem in enumerate(keep_index_2) if idx in keep_index_3]
    keep_index = [elem for idx, elem in enumerate(keep_index_1) if idx in keep_index_23]
    # keep_index = [elem for idx, elem in enumerate(keep_index_1) if idx in [elem1 for idx1, elem1 in enumerate(keep_index_2) if idx1 in keep_index_3]]
    
    # for sanity check
    print("Start dropping files: ")
    
    drop_files(keep_index, args.sample_queries_dir, args.sample_context_dir, 
               args.sample_queries_dropped_dir, args.sample_context_dropped_dir, sample_context_individual_length)
    compute_backtrans_bleu(args.sample_queries_dropped_dir, args.sample_context_dropped_dir,
                           args.jaccard_queries_dir, args.jaccard_context_dir)

    # create augmented dataset
    new_data_dict = gen_augmented_dataset('beam{0}'.format(beam), args.jaccard_queries_dir, args.jaccard_context_dir, 
                                          dropped_context_individual_length, sample_idx, new_answers)
    save_as_pickle(new_data_dict, args.aug_dataset_pickle)
#     save_as_json(new_data_dict, args.aug_dataset_dict)

#     data_encodings = read_and_process(args, tokenizer, new_dataset_dict, data_dir, dataset_name, split_name)

    
if __name__ == '__main__':
#    nmt_sampling(beam=1) 
    nmt_sampling(beam=5) 

#   tokenizer = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')
#   output = get_sampling_dataset(args, args.train_datasets, args.train_dir, tokenizer, 'train')
