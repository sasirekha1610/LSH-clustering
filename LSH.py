from bs4 import BeautifulSoup
import sys
import os.path
import string
import os
import re
import random
import time
import binascii

documents = []
printedbodies = {}
print ('Reading files')
print ('Please wait...')
t0 = time.time()

#data = bytes(" ",'UTF-8')
#data = ""
for file in os.listdir("data/"):
    if file.endswith(".sgm"):
        filename = os.path.join("data", file)

        f = open(filename, 'rb')
        data = f.read()

print ('Reading data took %.2f sec.' % (time.time() - t0))

print ('Transforming data...')
t0 = time.time()
soup = BeautifulSoup(data, "html.parser")
bodies = soup.findAll('body')
i = 0
for body in bodies:
    printedbodies[i] = body
    text =  str(body).replace("<body>", "").replace("</body>", "")
    documents.append(
        re.sub(' +', ' ',text.translate(None,string.punctuation)
               .replace("", "").replace("\n", " ").lower()))
    i = i + 1

print ('Transforming data took %.2f sec.' % (time.time() - t0))

print ('The number of documents read was: ' + str(len(documents)))

i = 0
d = {}

t = {}
t0 = time.time()
for value in documents:
    # create a dictionary where key=docid and value=document text
    d[i] = value
    # split text into words
    d[i] = re.sub("[^\w]", " ", d[i]).split()
    if d[i]:
        i = i + 1
    else:
        del d[i]
        del body[i]
docsAsShingleSets = {}
docNames = []
totalShingles = 0
shingleNo = 0
while True:
    try:
        shingle_size = int(input("Please enter k value for k-shingles: "))
    except ValueError:
        print("Your input is not valid. Give a positive natural number > 0...")
        continue
    if shingle_size <= 0:
        continue
    else:
        break

print ("Shingling articles...")
t0 = time.time()
for i in range(0, len(d)):
    words = d[i]
    docID = i
    docNames.append(docID)
    shinglesInDocWords = set()
    shinglesInDocInts = set()
    shingle = []
    for index in range(len(words) - shingle_size + 1):
        shingle = words[index:index + shingle_size]
        shingle = ' '.join(shingle)
       # Hash the shingle to a 32-bit integer.
        crc = binascii.crc32(shingle) & 0xffffffff
        if shingle not in shinglesInDocWords:
            shinglesInDocWords.add(shingle)
        if crc not in shinglesInDocInts:
            shinglesInDocInts.add(crc)
            shingleNo = shingleNo + 1
        else:
            del shingle
            index = index - 1
    docsAsShingleSets[docID] = shinglesInDocInts

totalShingles = shingleNo

print ('Total Number of Shingles', shingleNo)
print ('\nShingling ' + str(len(docsAsShingleSets)) + ' docs took %.2f sec.' % (time.time() - t0))
print ('\nAverage shingles per doc: %.2f' % (shingleNo / len(docsAsShingleSets)))
numElems = int(len(docsAsShingleSets) * (len(docsAsShingleSets) - 1) / 2)
JSim = [0 for x in range(numElems)]
estJSim = [0 for x in range(numElems)]

def getTriangleIndex(i, j):
    if i == j:
        sys.stderr.write("Can't access triangle matrix with i == j")
        sys.exit(1)
    if j < i:
        temp = i
        i = j
        j = temp
    k = int(i * (len(docsAsShingleSets) - (i + 1) / 2.0) + j - i) - 1

    return k

while True:
    try:
        numHashes = int(input("\nPlease enter how many hash functions you want to be used: "))
    except ValueError:
        print("Your input is not valid. Give a positive natural number > 0...")
        continue
    if numHashes <= 0:
        continue
    else:
        break
print ('\nGenerating random hash functions...')

#generating minhash signature

from time import clock
t0 = time.time()
def MillerRabinPrimalityTest(number):
    if number == 2:
        return True
    elif number == 1 or number % 2 == 0:
        return False
    oddPartOfNumber = number - 1
    timesTwoDividNumber = 0
    while oddPartOfNumber % 2 == 0:
        oddPartOfNumber = oddPartOfNumber / 2
        timesTwoDividNumber = timesTwoDividNumber + 1
    for time in range(3):
        while True:
            randomNumber = random.randint(2, number) - 1
            if randomNumber != 0 and randomNumber != 1:
                break
        randomNumberWithPower = pow(randomNumber, oddPartOfNumber,number)
        if (randomNumberWithPower != 1) and (randomNumberWithPower != number - 1):
            iterationNumber = 1
            while (iterationNumber <= timesTwoDividNumber - 1) and (randomNumberWithPower != number - 1):
                randomNumberWithPower = pow(randomNumberWithPower, 2, number)
                iterationNumber = iterationNumber + 1
            if (randomNumberWithPower != (number - 1)):
                return False
    return True

i = 1
while not MillerRabinPrimalityTest(shingleNo + i):
    i = i + 1
print ('Next prime = ', shingleNo + i)

maxShingleID = shingleNo
nextPrime = shingleNo + i



def pickRandomCoeffs(k):
    randList = []
    while k > 0:
        randIndex = random.randint(0, maxShingleID)
        while randIndex in randList:
            randIndex = random.randint(0, maxShingleID)
        randList.append(randIndex)
        k = k - 1
    return randList

coeffA = pickRandomCoeffs(numHashes)
coeffB = pickRandomCoeffs(numHashes)

print ('\nGenerating MinHash signatures for all documents...')
signatures = []


for docID in docNames:
    shingleIDSet = docsAsShingleSets[docID]
    signature = []
    for i in range(0, numHashes):
        minHashCode = nextPrime + 1
        for shingleID in shingleIDSet:
            hashCode = (coeffA[i] * shingleID + coeffB[i]) % nextPrime
            if hashCode < minHashCode:
                minHashCode = hashCode
    signature.append(minHashCode)
    signatures.append(signature)
elapsed = (time.time() - t0)

print ("\nGenerating MinHash signatures took %.2fsec" % elapsed)

numDocs = len(signatures)

while True:
    try:
        docid = int(input(
            "Please enter the document id you are interested in. The valid document ids are 1 - " + str(
                numDocs) + ": "))
    except ValueError:
        print("Your input is not valid.")
        continue
    if docid <= 0 or docid > numDocs:
        print ("Your input is out of the defined range...")
        continue
    else:
        break
while True:
    try:
        neighbors = int(input("Please enter the number of closest neighbors you want to find... "))
    except ValueError:
        print("Your input is not valid.")
        continue
    if neighbors <= 0:
        continue
    else:
        break

# Calculating Jaccard similarity directly

from decimal import *
print ("\nCalculating Jaccard Similarities of Shingles...")
t0 = time.time()
s0 = len(docsAsShingleSets[0])
i = docid
if (i % 100) == 0:
    print ("  (" + str(i) + " / " + str(len(docsAsShingleSets)) + ")")
s1 = docsAsShingleSets[docNames[i]]
neighbors_of_given_documentSHINGLES = {}
fp = []
tp = []
for j in range(0, len(docsAsShingleSets)):
    if j != i:
        s2 = docsAsShingleSets[docNames[j]]
        JSim[getTriangleIndex(i, j)] = (len(s1.intersection(s2)) / float(len(s1.union(s2))))
        percsimilarity = JSim[getTriangleIndex(i, j)] * 100
        if (percsimilarity > 0):
            print ("  %5s --> %5s   %.2f%s   " % (docNames[i], docNames[j], percsimilarity, '%'))
            neighbors_of_given_documentSHINGLES[j] = percsimilarity

sorted_neigborsSHINGLES = sorted(neighbors_of_given_documentSHINGLES.items(), key=lambda x: x[1], reverse=True)

print ('Comparing Shingles ...')
print ("The " + str(neighbors) + " closest neighbors of document " + str(docNames[i]) + " are:")
for i in range(0, neighbors):
    if i >= len(sorted_neigborsSHINGLES):
        break
    tp.append(sorted_neigborsSHINGLES[i][0])
    print ("Shingles of Document " + str(sorted_neigborsSHINGLES[i][0]) + " with Jaccard Similarity " + str(
        round(sorted_neigborsSHINGLES[i][1], 2)) + "%")
elapsed = (time.time() - t0)

print ('These are the True Positives, since no time saving assumptions were made while calculating the Jaccard similarity of shingles')
print ("\nCalculating all Jaccard Similarities of Shingles Took %.2fsec" % elapsed)
print ('\nNote: In this section, we directly calculated the Jaccard similarities by comparing the shingle sets. This is included here to show how much slower it is than the MinHash and LSH approach.')
print ('\nMoreover, the similarities calculated above are the actual similarities of the documents, since there were no assumption made')

print ('Number of signatures', len(signatures))
tpsig = 0
fpsig = 0

t0 = time.time()

threshold = 0
print ('\nNow we will calculate Jaccard Similarity between signatures')
print ("Values shown are the estimated Jaccard similarity")
i = docid
signature1 = signatures[i]

neighbors_of_given_documentSIGNATURES = {}

for j in range(0, numDocs):
    if (i != j):
        signature2 = signatures[j]
        count = 0
        for k in range(0, numHashes):

            if (signature1[k] == signature2[k]):
                count = count + 1
        estJSim[getTriangleIndex(i, j)] = (count / float(numHashes))
        if float(estJSim[getTriangleIndex(i, j)]) > 0:
            s1 = set(signature1)
            s2 = set(signature2)

            J = len(s1.intersection(s2)) / float(len(s1.union(s2)))
            neighbors1 = []
            if (float(J) > threshold):
                percsimilarity = estJSim[getTriangleIndex(i, j)] * 100
                percJ = J * 100
                neighbors_of_given_documentSIGNATURES[j] = percJ

sorted_neigborsSIGNATURES = sorted(neighbors_of_given_documentSIGNATURES.items(), key=lambda x: x[1], reverse=True)


sigpos = []
print ('Comparing Signatures...')
print ("The " + str(neighbors) + " closest neighbors of document " + str(docNames[i]) + " are:")
for i in range(0, neighbors):
    if i >= len(sorted_neigborsSIGNATURES):
        break
    print ("Signatures of Document " + str(sorted_neigborsSIGNATURES[i][0]) + " with Jaccard Similarity " + str(
        round(sorted_neigborsSIGNATURES[i][1], 2)) + "%")
    sigpos.append(sorted_neigborsSIGNATURES[i][0])

fpsig = neighbors - len(list(set(tp).intersection(sigpos)))
tpsig = neighbors - fpsig
elapsed = (time.time() - t0)
print ('\n', tpsig, '/', neighbors, 'True Positives and', fpsig, '/', neighbors, 'False Positives Produced While Comparing Signatures',)

print ("\nCalculating Jaccard Similarity of Signatures took %.2fsec" % elapsed)
while True:
    try:
        band_size = int(
            input("\nPlease enter the size of the band. Valid band rows are 1 - " + str(numHashes) + ": "))
    except ValueError:
        print("Your input is not valid.")
        continue
    if band_size <= 0 or band_size > numHashes:
        print ("Your input is out of the defined range...")
        continue
    else:
        break

t0 = time.time()

tlist = []
for key, value in t.iteritems():
    temp = value
    tlist.append(temp)

from random import randint, seed, choice, random
import string
import sys
import itertools


def get_band_hashes(minhash_row, band_size):
    band_hashes = []
    for i in range(len(minhash_row)):
        if i % band_size == 0:
            if i > 0:
                band_hashes.append(band_hash)
            band_hash = 0
        band_hash += hash(minhash_row[i])
    return band_hashes


neighbors_of_given_documentLSH = {}


def get_similar_docs(docs, shingles, threshold, n_hashes, band_size, collectIndexes=True):
    t0 = time.time()
    lshsignatures = {}
    hash_bands = {}
    random_strings = [str(random()) for _ in range(n_hashes)]
    docNum = 0
    w = 0
    for doc in docs:
        lshsignatures[w] = doc
        minhash_row = doc
        band_hashes = get_band_hashes(minhash_row, band_size)
        w = w + 1
        docMember = docNum if collectIndexes else doc
        for i in range(len(band_hashes)):
            if i not in hash_bands:
                hash_bands[i] = {}
            if band_hashes[i] not in hash_bands[i]:
                hash_bands[i][band_hashes[i]] = [docMember]
            else:
                hash_bands[i][band_hashes[i]].append(docMember)
        docNum += 1

    similar_docs = set()
    similarity1 = []
    noPairs = 0
    print ('Comparing Signatures Found in the Same Buckets During LSH ...')
    samebucketLSH = []
    samebucketcnt = 0
    for i in hash_bands:
        for hash_num in hash_bands[i]:
            if len(hash_bands[i][hash_num]) > 1:
                for pair in itertools.combinations(hash_bands[i][hash_num], r=2):
                    if pair not in similar_docs:
                        similar_docs.add(pair)
                        if pair[0] == docid and pair[1] != docid:

                            s1 = set(lshsignatures[pair[0]])
                            s2 = set(lshsignatures[pair[1]])

                            sim = len(s1.intersection(s2)) / float(len(s1.union(s2)))
                            if (float(sim) > threshold):
                                percsim = sim * 100
                                noPairs = noPairs + 1
                            else:
                                percsim = 0
                            neighbors_of_given_documentLSH[pair[1]] = percsim
                            samebucketLSH.append(pair[1])
                            samebucketcnt = samebucketcnt + 1
                            elapsed = (time.time() - t0)

    print ('Number of false positives while comparing signatures which were found in the same bucket',)
    sorted_neigborsLSH = sorted(neighbors_of_given_documentLSH.items(), key=lambda x: x[1], reverse=True)
    
    lshpos = []
    print ('Comparing Signatures Found in the Same Bucket During LSH...')
    print ("The " + str(neighbors) + " closest neighbors of document " + str(docid) + " are:")
    for i in range(0, neighbors):
        if i >= len(sorted_neigborsLSH):
            break
        if sorted_neigborsLSH[i][1] > 0:
            print ("\nChosen Signatures (After LSH) of Document " + str(sorted_neigborsLSH[i][0]) + " with Jaccard Similarity " + str(round(sorted_neigborsLSH[i][1], 2)) + "%")
            print ("\nBody of document " + str(sorted_neigborsLSH[i][0]) + "\n" + str(printedbodies[sorted_neigborsLSH[i][0]]))
            lshpos.append(sorted_neigborsLSH[i][0])

    neighborsfplsh = neighbors - len(list(set(tp).intersection(lshpos)))
    neighborstplsh = neighbors - neighborsfplsh
    totaltplsh = len(list(set(tp).intersection(samebucketLSH)))
    totalfplsh = samebucketcnt - totaltplsh

    print ('\nEvaluating the', neighbors, 'neighbors produced by LSH...')
    print (neighborstplsh, 'out of', neighbors, 'TP and', neighborsfplsh, 'out of', neighbors, 'FP')
    print ('\nEvaluating the', samebucketcnt, 'pairs which fell in the same bucket...')

    if samebucketcnt > 0:
        prctpLSH = round((totaltplsh / float(samebucketcnt)) * 100, 2)
        prcfpLSH = 100 - prctpLSH
        print (totaltplsh, 'out of', samebucketcnt, 'documents which fell in the same bucket are TP', prctpLSH, '%')
        print (totalfplsh, 'out of', samebucketcnt, 'documents which fell in the same bucket are FP', prcfpLSH, '%')
    else:
        print (totaltplsh, 'out of', samebucketcnt, 'documents which fell in the same bucket are TP')
        print (totalfplsh, 'out of', samebucketcnt, 'documents which fell in the same bucket are FP')

    return similar_docs

n_hashes = numHashes
n_similar_docs = 2
seed(42)
finalshingles = docsAsShingleSets
similar_docs = get_similar_docs(signatures, finalshingles, threshold, n_hashes, band_size, collectIndexes=True)
print ('\nLocality Sensitive Hashing ' + str(len(signatures)) + ' docs took %.2f sec.' % (time.time() - t0))
r = float(n_hashes / band_size)
similarity = (1 / r) ** (1 / float(band_size))                                                          