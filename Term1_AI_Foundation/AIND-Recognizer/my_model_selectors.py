import math
import statistics
import warnings

import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.model_selection import KFold
from asl_utils import combine_sequences

class ModelSelector(object):
    '''
    base class for model selection (strategy design pattern)
    '''

    def __init__(self, all_word_sequences: dict, all_word_Xlengths: dict, this_word: str,
                 n_constant=3,
                 min_n_components=2, max_n_components=10,
                 random_state=14, verbose=False):
        self.words = all_word_sequences
        self.hwords = all_word_Xlengths
        self.sequences = all_word_sequences[this_word]
        self.X, self.lengths = all_word_Xlengths[this_word]
        self.this_word = this_word
        self.n_constant = n_constant
        self.min_n_components = min_n_components
        self.max_n_components = max_n_components
        self.random_state = random_state
        self.verbose = verbose

    def select(self):
        raise NotImplementedError

    def base_model(self, num_states):
        # with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # warnings.filterwarnings("ignore", category=RuntimeWarning)
        try:
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            if self.verbose:
                print("model created for {} with {} states".format(self.this_word, num_states))
            return hmm_model
        except:
            if self.verbose:
                print("failure on {} with {} states".format(self.this_word, num_states))
            return None


class SelectorConstant(ModelSelector):
    """ select the model with value self.n_constant

    """

    def select(self):
        """ select based on n_constant value

        :return: GaussianHMM object
        """
        best_num_components = self.n_constant
        return self.base_model(best_num_components)


class SelectorBIC(ModelSelector):
    """ select the model with the lowest Bayesian Information Criterion(BIC) score

    http://www2.imm.dtu.dk/courses/02433/doc/ch6_slides.pdf
    Bayesian information criteria: BIC = -2 * logL + p * logN
    logL: log loss
    logN: N is the number of data points
    """

    def select(self):
        """ select the best model for self.this_word based on
        BIC score for n between self.min_n_components and self.max_n_components

        :return: GaussianHMM object
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # The Process:
        # 1. Loop through a number of possible states for HMM, n between self.min_n_components and self.max_n_components
        # 2. For each state, build a model with num_states from step 1 and calculate the BIC
        # 3. Choose the num_states which has the lowest(best) BIC.
        bic_dict = {}
        # 1. Loop through a number of possible states for HMM, n between self.min_n_components and self.max_n_components
        for num_states in range(self.min_n_components, self.max_n_components + 1):
            # 2. For each state, build a model with num_states from step 1 and calculate the BIC
            hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                    random_state=self.random_state, verbose=False).fit(self.X, self.lengths)
            k = len(self.X[0])
            p = (num_states ^ 2) + (2 * k * num_states - 1)
            try:
                log_loss = hmm_model.score(self.X, self.lengths)
            except:
                continue
            bic_score = -2 * log_loss + p * math.log(len(self.sequences))
            bic_dict[num_states] = bic_score
        # 3. Choose the num_states which has the lowest(best) BIC.
        ideal_num_states = min(bic_dict, key=bic_dict.get)
        return GaussianHMM(n_components=ideal_num_states, covariance_type="diag", n_iter=1000,
                           random_state=self.random_state, verbose=False)


class SelectorDIC(ModelSelector):
    ''' select best model based on Discriminative Information Criterion

    Biem, Alain. "A model selection criterion for classification: Application to hmm topology optimization."
    Document Analysis and Recognition, 2003. Proceedings. Seventh International Conference on. IEEE, 2003.
    http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.58.6208&rep=rep1&type=pdf
    DIC = log(P(X(i)) - 1/(M-1)SUM(log(P(X(all but i))
    '''

    def select(self):
        """
        Function to get the best model based on DIC

        :return: a model with the optimal number of states according to DIC.
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # The Process
        # 1. Loop through a number of possible states for HMM, n between self.min_n_components and self.max_n_components
        # 2. For each state, build a model with num_states from step 1 and calculate the DIC
        # 3. Choose the num_states which has the highest(best) DIC.
        dic_dict = {}
        # 1. Loop through a number of possible states for HMM, n between self.min_n_components and self.max_n_components
        for num_states in range(self.min_n_components, self.max_n_components + 1):
            # 2. For each state, build a model with num_states from step 1 and calculate the DIC
            dic_score = self.get_dic_score(num_states)
            dic_dict[num_states] = dic_score
        # 3. Choose the num_states which has the highest(best) DIC.
        num_states = max(dic_dict, key=dic_dict.get)
        return self.base_model(num_states)

    def get_dic_score(self, num_states):
        """
        Helper function to get the DIC score for a hmm model

        :param num_states: number of states in the hmm model
        :return: the DIC score for the particular model and the model itself
        """
        model = self.base_model(num_states)
        scores = []
        for word, (X, length) in self.hwords.items():
            if word != self.this_word:
                try:
                    scores.append(model.score(X, length))
                except:
                    continue
        try:
            return model.score(self.X, self.lengths) - np.mean(scores)
        except:
            return float('-Inf')


class SelectorCV(ModelSelector):
    ''' select best model based on average log Likelihood of cross-validation folds

    '''

    def select(self):
        """
        Function to select the best hmm model using cross validation.
        The objective is to find a model with the best number of states, for a given word.

        :return: the best model based on logL.
        """
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # If a word has less than 3 sequences we return a base model
        # with 3 states, the reason for this is because we know every word atleast
        # has a hand raise, some action and hand lower which intuitively gives
        # us 3 states.
        if len(self.sequences) < 3:
            return self.base_model(num_states = 3)

        # split method for k-folds
        n_splits = 3
        split_method = KFold(n_splits=n_splits, shuffle=False, random_state=None) # Default params

        # The process
        # 1. Loop through a number of possible states for HMM
        # 2. For each state, build a model with num_states from step 1 and calculate the average log loss using CV
        # 3. Choose the number of state based on the one that gives us the highest
        #    average log loss
        state_loss_dict = {}
        # 1. Loop through a number of possible states for HMM
        for num_states in range(self.min_n_components, self.max_n_components + 1):
            # 2. For each state, build a model with num_states from step 1 and calculate the average log loss using CV
            avg_log_loss = 0
            sum_log_loss = 0
            for cv_train_idx, cv_test_idx in split_method.split(self.sequences):
                # get the training data suitable for HMM learning
                cv_train_X, cv_train_lengths = combine_sequences(cv_train_idx, self.sequences)
                # Build a hmm model
                hmm_model = GaussianHMM(n_components=num_states, covariance_type="diag", n_iter=1000,
                                        random_state=self.random_state, verbose=False).fit(cv_train_X, cv_train_lengths)
                # get the test data suitable for scoring
                cv_test_X, cv_test_lengths = combine_sequences(cv_test_idx, self.sequences)
                # get the log loss for the test set
                try:
                    log_loss = hmm_model.score(cv_test_X, cv_test_lengths)
                except:
                    continue
                sum_log_loss += log_loss
            avg_log_loss = sum_log_loss / n_splits
            state_loss_dict[num_states] = avg_log_loss
        # 3. Choose the number of state based on the one that gives us the highest
        #    average log loss
        ideal_num_states = max(state_loss_dict, key=state_loss_dict.get)
        return GaussianHMM(n_components=ideal_num_states, covariance_type="diag", n_iter=1000,
                           random_state=self.random_state, verbose=False)
