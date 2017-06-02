
# In[23]:

def combomaker(x):
    combos = itertools.combinations(x, 2)
    usable_pairs = []
    for i in combos:
        usable_pairs.append(i)
    return usable_pairs
    # Takes a list of ticker symbols as an input and returns a list of
    # all possible combination without repetition



# In[24]:

def ssd(X,Y):
#This function returns the sum of squared differences between two lists, in addition the
#standard deviation of the spread between the two lists are calculated and reported.
    spread = [] #Initialize variables
    std = 0
    cumdiff = 0
    for i in range(len(X)): #Calculate and store the sum of squares
        cumdiff += (X[i]-Y[i])**2
        spread.append(X[i]-Y[i])
    std = np.std(spread)  #Calculate the standard deviation
    return cumdiff,std


# In[28]:

def pairsmatch(x, daxnorm):
    allpairs = combomaker(x)
    squared = []
    std = []
    for i in allpairs:
        squared.append(ssd(daxnorm[i[0]],daxnorm[i[1]])[0])
        std.append(ssd(daxnorm[i[0]],daxnorm[i[1]])[1])
    distancetable = pd.DataFrame({'Pair' : allpairs, 'SSD' : squared, 'Standard Deviation' : std})
    distancetable.sort(columns=['SSD'], axis=0, ascending=True, inplace=True)
    return distancetable

def norming(x):
    #if isinstance(x, basestring):
    #    return x
    return x / x[0]
