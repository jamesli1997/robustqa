from args import get_transformer_args, get_transformer_ood_args
from backtranslate_util import *
import util
# from transformers import DistilBertTokenizerFast

def transformer_sampling(lang='de', indomain=True):
  if indomain:
    args = get_transformer_args(lang)
  else:
    args = get_transformer_ood_args(lang)
  
  # sampling
  sample_idx, sample_context_individual_length, gold_answers, answer_locs = sample_dataset(args, args.train_datasets, args.train_dir,
                                                                                          args.sample_queries_dir, args.sample_context_dir, 
                                                                                          args.sample_prob, args.seed, max_num=10000)
  # estimate new answers
  keep_index, new_answers = get_trans_context_answers(args.back_trans_context_dir, sample_context_individual_length, 
                                                      gold_answers, answer_locs, args.jaccard_threshold)
  drop_files(keep_index, args.back_trans_queries_dir, args.back_trans_context_dir,
             args.jaccard_queries_dir, args.jaccard_context_dir, sample_context_individual_length)
  drop_files(keep_index, args.sample_queries_dir, args.sample_context_dir, 
             args.sample_queries_dropped_dir, args.sample_context_dropped_dir, sample_context_individual_length)
  sample_idx, sample_context_individual_length, gold_answers, answer_locs = clean_lists(keep_index, [sample_idx, sample_context_individual_length, gold_answers, answer_locs])
  print('Num of examples after filtering by Jaccard similarity:', len(keep_index))

  # compute queries and context BLEU    
  compute_backtrans_bleu(args.sample_queries_dropped_dir, args.sample_context_dropped_dir,
                         args.jaccard_queries_dir, args.jaccard_context_dir)

  # create augmented dataset
  new_data_dict = gen_augmented_dataset('transformer{0}indomain{1}'.format(lang, indomain), args.jaccard_queries_dir, args.jaccard_context_dir, 
                                        sample_context_individual_length, sample_idx, new_answers)
  save_as_pickle(new_data_dict, args.aug_dataset_pickle)
    
  
if __name__ == '__main__':
#   transformer_sampling(lang='de', indomain=True) 
#   transformer_sampling(lang='ru', indomain=True)
  transformer_sampling(lang='de', indomain=False) 
  transformer_sampling(lang='ru', indomain=False) 
