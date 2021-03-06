import sys, random
import numpy as np
import theano
import theano.tensor as T
from theano import config
from theano.sandbox.rng_mrg import MRG_RandomStreams as RandomStreams
import _pickle as pickle
from collections import OrderedDict
from sklearn.metrics import roc_auc_score

def unzip(zipped):
    new_params = OrderedDict()
    for key, value in zipped.items():
        new_params[key] = value.get_value()
    return new_params

def numpy_floatX(data):
    return np.asarray(data, dtype=config.floatX)

def get_random_weight(dim1, dim2, left=-0.1, right=0.1):
    return np.random.uniform(left, right, (dim1, dim2)).astype(config.floatX)

def init_params(options):
    params = OrderedDict()

    inputDimSize = options['inputDimSize']
    hiddenDimSize = options['hiddenDimSize'] #hidden layer does not need an extra space

    params['W_emb'] = np.eye(inputDimSize, dtype=config.floatX)

    params['W_gru'] = get_random_weight(inputDimSize, 3*hiddenDimSize)
    params['U_gru'] = get_random_weight(hiddenDimSize, 3*hiddenDimSize)
    params['b_gru'] = np.zeros(3*hiddenDimSize).astype(config.floatX)

    params['W_logistic'] = get_random_weight(hiddenDimSize,1)
    params['b_logistic'] = np.zeros((1,), dtype=config.floatX)

    #params = [params['W_emb'],params['W_gru'],params['U_gru'],params['b_gru'],params['W_logistic'],params['b_logistic']]

    return params

def init_tparams(params):
    tparams = OrderedDict()
    for key, value in params.items():
        if key == 'W_emb': continue#####################
        tparams[key] = theano.shared(value, name=key)
    return tparams

def dropout_layer(state_before, use_noise, trng):
    proj = T.switch(use_noise, (state_before * trng.binomial(state_before.shape, p=0.5, n=1, dtype=state_before.dtype)), state_before * 0.5)
    return proj

def _slice(_x, n, dim):
    if _x.ndim == 3:
        return _x[:, :, n*dim:(n+1)*dim]
    return _x[:, n*dim:(n+1)*dim]

def gru_layer(tparams, emb, options, mask=None):
    hiddenDimSize = options['hiddenDimSize']
    timesteps = emb.shape[0]
    if emb.ndim == 3: n_samples = emb.shape[1]
    else: n_samples = 1

    def _step(m_, x_, h_, c_):
        preact = T.dot(h_, tparams['U_gru'])
        preact += x_

        i = T.nnet.sigmoid(_slice(preact, 0, hiddenDimSize))
        f = T.nnet.sigmoid(_slice(preact, 1, hiddenDimSize))
        o = T.nnet.sigmoid(_slice(preact, 2, hiddenDimSize))
        c = T.tanh(_slice(preact, 3, hiddenDimSize))

        c = f * c_ + i * c
        c = m_[:, None] * c + (1. - m_)[:, None] * c_

        h = o * T.tanh(c)
        h = m_[:, None] * h + (1. - m_)[:, None] * h_

        return h, c

    state_below = (T.dot(emb, tparams['W_gru']) +
                   tparams['b_gru'])

    # dim_proj = options['dim_proj']
    rval, updates = theano.scan(_step,
                                sequences=[mask, state_below],
                                outputs_info=[T.alloc(numpy_floatX(0.),
                                                           n_samples,
                                                           hiddenDimSize),
                                              T.alloc(numpy_floatX(0.),
                                                           n_samples,
                                                           hiddenDimSize)],
                                name='gru_layer',
                                n_steps=timesteps)
    return rval[0]



def build_model(tparams, options, Wemb):
    trng = RandomStreams(123)
    use_noise = theano.shared(numpy_floatX(0.))

    x = T.matrix('x', dtype='int64')
    mask = T.matrix('mask', dtype=config.floatX)
    y = T.vector('y', dtype='int64')

    n_timesteps = x.shape[0]
    n_samples = x.shape[1]

    emb = Wemb[x.flatten()].reshape([n_timesteps,n_samples,options['inputDimSize']])

    proj = gru_layer(tparams, emb, options, mask=mask)
    proj = (proj * mask[:, :, None]).sum(axis=0)
    proj = proj / mask.sum(axis=0)[:, None]

    p_y_given_x = T.nnet.sigmoid(T.dot(proj, tparams['W_logistic']) + tparams['b_logistic'])
    L = -(y * T.flatten(T.log(p_y_given_x)) + (1 - y) * T.flatten(T.log(1 - p_y_given_x)))

    #print (L)
    cost = T.mean(L)

    if options['L2_reg'] > 0.: cost += options['L2_reg'] * (tparams['W_logistic'] ** 2).sum()

    #print ("***************", cost)

    return use_noise, x, mask, y, p_y_given_x, cost





def load_data(inputFile, timeFile=''):

    #print ('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&',seqFile)
    # open pickle file
    #with open(seqFile, 'rb') as f:
    #   f.seek(0)
#       temp = pickle.load(f)

    with open(inputFile) as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip().split(",") for x in content]
    flattenedset = list(set([val for sublist in content for val in sublist]))
    mapping = {}
    maps = enumerate(flattenedset)
    for i,a in maps:
        mapping[a] = i

    train = list()
    labels = np.zeros(len(content))
    count=0
    for listing in content:
        seq = list()
        for i in range(0,len(listing)):
            if i ==0:
                continue
            else:
                seq.append( mapping[listing[i]])
    #     print(seq)
        train.append(seq)
        labels[count] = listing[0]
        count = count +1
    sequences = np.array(train)

    dataSize = len(labels)
    ind = np.random.permutation(dataSize)
    nTest = int(0.10 * dataSize)
    nValid = int(0.20 * dataSize)

    test_indices = ind[:nTest]
    valid_indices = ind[nTest:nTest+nValid]
    train_indices = ind[nTest+nValid:]

    train_set_x = sequences[train_indices]
    train_set_y = labels[train_indices]
    test_set_x = sequences[test_indices]
    test_set_y = labels[test_indices]
    valid_set_x = sequences[valid_indices]
    valid_set_y = labels[valid_indices]
    train_set_t = None
    test_set_t = None
    valid_set_t = None

    if len(timeFile) > 0:
        train_set_t = times[train_indices]
        test_set_t = times[test_indices]
        valid_set_t = times[valid_indices]

    def len_argsort(seq):
        return sorted(range(len(seq)), key=lambda x: len(seq[x]))

    train_sorted_index = len_argsort(train_set_x)
    train_set_x = [train_set_x[i] for i in train_sorted_index]
    train_set_y = [train_set_y[i] for i in train_sorted_index]

    valid_sorted_index = len_argsort(valid_set_x)
    valid_set_x = [valid_set_x[i] for i in valid_sorted_index]
    valid_set_y = [valid_set_y[i] for i in valid_sorted_index]

    test_sorted_index = len_argsort(test_set_x)
    test_set_x = [test_set_x[i] for i in test_sorted_index]
    test_set_y = [test_set_y[i] for i in test_sorted_index]

    if len(timeFile) > 0:
        train_set_t = [train_set_t[i] for i in train_sorted_index]
        valid_set_t = [valid_set_t[i] for i in valid_sorted_index]
        test_set_t = [test_set_t[i] for i in test_sorted_index]

    train_set = (train_set_x, train_set_y, train_set_t)
    valid_set = (valid_set_x, valid_set_y, valid_set_t)
    test_set = (test_set_x, test_set_y, test_set_t)

    return train_set, valid_set, test_set,len(flattenedset)

def adadelta(tparams, grads, x, mask, y, cost):
    zipped_grads = [theano.shared(p.get_value() * numpy_floatX(0.), name='%s_grad' % k) for k, p in tparams.items()]
    running_up2 = [theano.shared(p.get_value() * numpy_floatX(0.), name='%s_rup2' % k) for k, p in tparams.items()]
    running_grads2 = [theano.shared(p.get_value() * numpy_floatX(0.), name='%s_rgrad2' % k) for k, p in tparams.items()]

    zgup = [(zg, g) for zg, g in zip(zipped_grads, grads)]
    rg2up = [(rg2, 0.95 * rg2 + 0.05 * (g ** 2)) for rg2, g in zip(running_grads2, grads)]

    f_grad_shared = theano.function([x, mask, y], cost, updates=zgup + rg2up, name='adadelta_f_grad_shared')

    updir = [-T.sqrt(ru2 + 1e-6) / T.sqrt(rg2 + 1e-6) * zg for zg, ru2, rg2 in zip(zipped_grads, running_up2, running_grads2)]
    ru2up = [(ru2, 0.95 * ru2 + 0.05 * (ud ** 2)) for ru2, ud in zip(running_up2, updir)]
    param_up = [(p, p + ud) for p, ud in zip(tparams.values(), updir)]

    f_update = theano.function([], [], updates=ru2up + param_up, on_unused_input='ignore', name='adadelta_f_update')

    return f_grad_shared, f_update

def calculate_auc(test_model, datasets):
    batchSize = 20
    n_batches = int(np.ceil(float(len(datasets[0])) / float(batchSize)))
    scoreVec = []
    for index in range(n_batches):
        #print (index)
        x, mask = padMatrix(datasets[0][index*batchSize: (index+1)*batchSize])
        scoreVec.extend(list(test_model(x, mask)))
    labels = datasets[1]
    #print ("&&&&&&&&&&&&&&&&&&&&&&")
    #print (list(labels))
    #print ("^^^^^^^^^^^^^^^^")
    #print (list(scoreVec))
    auc = roc_auc_score(list(labels), list(scoreVec))

    return auc

def padMatrix(seqs):
    lengths = [len(s) for s in seqs]
    n_samples = len(seqs)
    maxlen = np.max(lengths)

    x = np.zeros((maxlen, n_samples)).astype('int32')
    x_mask = np.zeros((maxlen, n_samples)).astype(config.floatX)
    for idx, s in enumerate(seqs):
        x[:lengths[idx], idx] = s
        x_mask[:lengths[idx], idx] = 1.

    return x, x_mask

def train_GRU_RNN(
    dataFile='data.txt',
    # labelFile='label.txt',
    outFile='out.txt',
    inputDimSize= 100,
    hiddenDimSize=100,
    max_epochs=100,
    L2_reg = 0.,
    batchSize=100,
    use_dropout=True
):


    print ('Loading data ... ')
    trainSet, validSet, testSet,inputDimSize = load_data(dataFile)
    options = locals().copy()

    n_batches = int(np.ceil(float(len(trainSet[0])) / float(batchSize)))
    print ('done!!')

    print ('Building the model ... ')
    params = init_params(options)
    tparams = init_tparams(params)
    Wemb = theano.shared(params['W_emb'], name='W_emb')
    #print (tparams)
    #print (options)
    #print (Wemb)
    use_noise, x, mask, y, p_y_given_x, cost =  build_model(tparams, options, Wemb)
    print ('done!!')

    print ('Constructing the optimizer ... ')
    #print ("#############################")
    #print (tparams.values())

    grads  = []
    for param in tparams.values():
            gparam = T.grad(cost, param)
            grads.append(gparam)

    #print (grads)

    #grads = T.grad(cost, wrt=tparams.items())
    #grads = T.grad(cost, wrt=Wemb)
    #print (grads)
    #print ("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    f_grad_shared, f_update = adadelta(tparams, grads, x, mask, y, cost)
    print ('done!!')

    test_model = theano.function(inputs=[x, mask], outputs=p_y_given_x, name='test_model')

    bestValidAuc = 0.
    bestTestAuc = 0.
    iteration = 0
    bestParams = OrderedDict()
    print ('Optimization start !!')
    # print('n batches =',n_batches)
    # print('trainSet = ',len(trainSet[0]),len(trainSet[1]))
    for epoch in range(max_epochs):
        for index in random.sample(range(n_batches), n_batches):
            use_noise.set_value(1.)
            x, mask = padMatrix(trainSet[0][index*batchSize:(index+1)*batchSize])
            y = trainSet[1][index*batchSize:(index+1)*batchSize]
            # print(len(x),len(mask),len(y))
            cost = f_grad_shared(x, mask, y)
            f_update()
            iteration += 1

        use_noise.set_value(0.)
        validAuc = calculate_auc(test_model, validSet)
        print ('epoch:%d, valid_auc:%f' % (epoch, validAuc))
        if (validAuc > bestValidAuc):
            bestValidAuc = validAuc
            testAuc = calculate_auc(test_model, testSet)
            bestTestAuc = testAuc
            bestParams = unzip(tparams)
            print ('Currenlty the best test_auc:%f' % testAuc)

    np.savez_compressed(outFile, **bestParams)

if __name__ == '__main__':
    dataFile = sys.argv[1]
    # labelFile = sys.argv[2]
    outFile = sys.argv[2]


    inputDimSize = 100 #The number of unique medical codes
    hiddenDimSize = 100#The size of the hidden layer of the GRU
    max_epochs = 100 #Maximum epochs to train
    L2_reg = 0.001 #L2 regularization for the logistic weight
    batchSize = 100 #The size of the mini-batch
    use_dropout = True #Whether to use a dropout between the GRU and the logistic layer

train_GRU_RNN(dataFile=dataFile, outFile=outFile, inputDimSize=inputDimSize, hiddenDimSize=hiddenDimSize, max_epochs=max_epochs, L2_reg=L2_reg, batchSize=batchSize, use_dropout=use_dropout)
