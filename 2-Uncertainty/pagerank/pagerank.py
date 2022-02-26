import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    result = {}
    for i in corpus:
        
        #Probability of randomly picking any page in corpus
        P_random = (1-damping_factor)/len(corpus)

        #Count how many times the link occurs from page
        occurance = 0
        links = corpus[page]

        for link in links:
            if link == i:
                occurance+=1
        P_link=0
        if len(links) > 0:
            P_link = damping_factor * occurance / len(links)
        result[i] = round(P_random + P_link,4)
    

    return result
    #raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    #Randomly choice initial page
    random_page = random.choice(list(corpus))

    results={}
    for i in corpus:
        results[i]= 0

    for x in range(n):

        page_weights = transition_model(corpus, random_page,damping_factor)

        weight_dict = list(page_weights.values())

        page_options = list(page_weights)
        random_page = random.choices(page_options, weights=weight_dict, cum_weights=None, k=1)[0]
        
        results[random_page] +=1

    for i in results:
        results[i]= results[i]/n

    return results
    #raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    ranks_dict={}
    for i in corpus:
        ranks_dict[i] = 1/len(corpus)
    page_options = list(corpus)
    page_links = list(corpus.values())
    
    finished = False
    while not finished:
        old_ranks = ranks_dict.copy()
        
        for page in page_options:
            P_link = 0
            index = 0

            for linked_pages in page_links:
                if page in linked_pages:
                    i_page = page_options[index]
                    P_link += ranks_dict[i_page]/len(linked_pages)
                index+=1

            P_page = ((1-damping_factor)/len(corpus)) + (damping_factor * P_link)
            ranks_dict[page] = P_page

        #Make sure probability add to one
        P_total = 0
        for page in ranks_dict:
            P_total += ranks_dict[page]
        for page in ranks_dict:
            ranks_dict[page] = ranks_dict[page]/P_total

        #Check if weights between previous and current differ by greater than 0.001
        for page in page_options:
            diff = old_ranks[page]-ranks_dict[page]
            if abs(diff)> 0.001:
                finished = False
                break
            else:
                finished = True
 
    return ranks_dict
    #raise NotImplementedError


if __name__ == "__main__":
    main()
