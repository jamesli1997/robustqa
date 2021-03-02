import util
import numpy as np
from nltk import tokenize
# conda install spacy
# python -m spacy download en_core_web_sm
import spacy

# load the module
nlp = spacy.load('en_core_web_sm')

def sample_dataset(args, datasets, data_dir, sample_prob = 0.1, seed = 94305,
                   sample_queries_dir = 'queries/sample_queries.txt',
                   sample_context_dir = 'queries/sample_context.txt'):
    np.random.seed(seed)
    datasets = datasets.split(',')
    dataset_dict = None
    dataset_name=''
    for dataset in datasets:
        dataset_name += f'_{dataset}'
        dataset_dict_curr = util.read_squad(f'{data_dir}/{dataset}')
        dataset_dict = util.merge(dataset_dict, dataset_dict_curr)
    train_length = len(dataset_dict['id'])
    sample_idx = list(np.random.choice(train_length, size = int(sample_prob * train_length), replace = False))
    sample_queries = [dataset_dict['question'][i] for i in sample_idx]
    sample_context = [dataset_dict['context'][i] for i in sample_idx]
    
    
    write_queries(sample_queries, sample_queries_dir)
    sample_context_individual_length = write_context(sample_context, sample_context_dir)
        
    return dataset_dict, sample_idx, sample_context_individual_length
    

def write_queries(queries, output_dir = 'queries/sample_queries.txt'):
    with open(output_dir, 'w') as f:
        for q in queries:
            f.write(q)
            f.write('\n')

def write_context(context, output_dir = 'queries/sample_context.txt'):
    out_lengths = []
    with open(output_dir, 'w') as f:
        for c in context:
#             c = c.replace('\n','')
            out = [str(sent).strip() for sent in nlp(c).sents if str(sent) != '\n']
            for o in out:
                f.write(o)
                f.write('\n')
            out_lengths.append(len(out))
    return out_lengths

def concat_queries(queries_dir):
    output_queries = []
    f = open(queries_dir, 'r')
    whole_queries = f.readlines()
    for q in whole_queries:
        output_queries.append(q)
    return output_queries
    
def concat_context(context_dir, sample_context_individual_length):
    output_context = []
    count = 0
    f = open(context_dir, 'r')
    whole_context = f.readlines()
    for l in sample_context_individual_length:
        individual_context = whole_context[count:(count+l)]
        individual_context = [ic.rstrip() for ic in individual_context]
        individual_context = ' '.join(individual_context)
        output_context.append(individual_context)
        count += l
    return output_context
