import numpy as np


def activation_thr(x,thr=0.2):
    """"Treshold Activation Function"""
    return (x > thr).astype(int)

def activation(x):
    """Sigmoid activation function"""
    return (1 / (1 + np.exp(-x)))

class NNet:
    """Class of Neural Networks with variable number of layers"""

    def __init__(self, x, lay=[],rand_weights=True):
        """The constructor of the class"""

        # Copy the input into a member variable
        self.input = x

        # Number of nodes per layer is copied
        self.layers = lay

        # Number of layers is computed
        self.n_layers = len(self.layers)

        # Construct array for the values of each node
        self.layer_values = []
        for i in self.layers:
            self.layer_values.append(np.zeros(i))


        # initialize random weights
        self.weights = []
        if rand_weights:
            for i in range(self.n_layers-1):
            
                self.weights.append(np.random.randn(self.layers[i], self.layers[i+1]))
        else:
            for i in range(self.n_layers-1):
            
                self.weights.append(np.zeros(self.layers[i], self.layers[i+1]))

        # initialize placeholder for output
        self.y = np.zeros(lay[-1])

    def forward(self):
        self.layer_values[0] = self.input
        for i in range(self.n_layers-1):
            self.layer_values[i+1] = activation(np.dot(self.layer_values[i], self.weights[i]))
        return self.layer_values


class generation:
    """genration of neural nets"""

    def __init__(self, n, x, lay,rand_weights=True):

        self.size = n
        self.x=x
        self.lay = lay
        # We generate n neural nets of shape lay
        self.individuals = []
        [self.individuals.append(NNet(x, lay,rand_weights)) for i in range(n)]

        # We initialize score array
        self.scores = np.zeros(n)

    
    def speeddate(self,pair_scores):
        "function that selects n parent_pairs for breeding"

        parents1=np.array([])
        parents2=np.array([])

        while len(parents1)<self.size:

            #Simulate reproduction using the respective pair_scores as probability
            selection = (np.random.random_sample(np.shape(pair_scores)) < pair_scores)

            #Eliminate the pairs that successfully reproduced
            #pair_scores[selection]=0

            #Save the corresponding pair indices
            pair_indices=np.where(selection)
            parents1=np.concatenate((parents1,pair_indices[0]))
            parents2=np.concatenate((parents2,pair_indices[1]))
        return parents1.astype(int),parents2.astype(int)

    def reproduce(self, index1, index2):
        """function that simulates the reproduction n parent pairs and returns the new generation"""

        mutation_prob = 0.2
        mutation_factor = 0.01

        #Instantiate new generation
        new_gen=self

        #We iterate over parent pairs
        for pair in range(self.size):
            
            #List of the weights of the current parent pair
            curr_weights1 = self.individuals[index1[pair]].weights
            curr_weights2 = self.individuals[index2[pair]].weights
            
            new_weights=[]
            #Introduce random mutations for each layer
            for layer in range(len(curr_weights1)):

                #Average the parent weights for this layer
                new_weights_layer=(curr_weights1[layer]+curr_weights2[layer])/2

                #Roll the amount of the mutation and whether it occurs
                mutation_amount=np.random.random_sample(np.shape(curr_weights1[layer]))

                mutation_rolls=np.where(np.random.random_sample(np.shape(curr_weights1[layer]))<mutation_prob)

                #We add a term of mut_amount*mut_prob to the weights that rolled True with mut_prob
                new_weights_layer[mutation_rolls]*=mutation_factor*mutation_amount[mutation_rolls]

                new_weights.append(new_weights_layer)
            
            new_gen.individuals[pair].weights=new_weights
        
        return new_gen

            

    def evolve(self):
        """function that evolves the population to a new generation based on their scores"""

        # We calculate the sores of parent pairs
        pair_scores = np.triu(np.outer(self.scores, self.scores),1)
        pair_scores_flat = np.ravel(pair_scores)

        # we normalize the scores
        scores_norm = np.linalg.norm(pair_scores_flat)

        if scores_norm != 0:

            pair_scores = pair_scores / scores_norm
        
        else:
            return generation(self.size,self.x,self.lay)
        parents1,parents2=self.speeddate(pair_scores)
        new_gen=self.reproduce(parents1,parents2)

        return new_gen
        
