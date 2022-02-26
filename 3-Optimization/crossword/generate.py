import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for variable in self.domains:
            variable_len = variable.length
            words_copy = self.domains[variable].copy()

            #Check if each word is the correct length for variable. If not remove word
            for word in words_copy:
                if variable_len != len(word):
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        #If there's no overlaps between x and y, then automatically arc consistent
        if self.crossword.overlaps[x,y] == None:
            return revised
        else:
            x_overlap =self.crossword.overlaps[x,y][0]
            y_overlap =self.crossword.overlaps[x,y][1]

        x_words = self.domains[x].copy()
        #Check each word in x has a letter that matches a word in y, else remove
        for x_word in x_words:
            word_found = False
            for y_word in self.domains[y]:
                if x_word[x_overlap] == y_word[y_overlap]:
                    word_found = True
                    break
            if not word_found:
                self.domains[x].remove(x_word)
                revised = True

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []
            #Create all arcs between neighboring variables
            for variable in self.domains:
                for variable2 in self.domains:
                    if variable != variable2 and self.crossword.overlaps[variable,variable2] != None:
                        arcs.append((variable,variable2))
        #for each arc, remove and check if consistent. If changes made, add new arcs accordingly
        while len(arcs) > 0:
            (X,Y) = arcs.pop(0)
            if self.revise(X, Y):
                if len(self.domains[X]) ==0:
                    return False
                for Z in self.crossword.neighbors(X):
                    if Z != Y:
                        arcs.append((Z,X))
        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(self.domains) == len(assignment):
            return True
        else:
            return False


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for key in assignment:
            #Check if word is correct length
            if key.length != len(assignment[key]):
                return False

            #Check if duplicate words
            if sum(x == assignment[key] for x in assignment.values())>1:
                return False
            
            #Check arc consistency 
            for neighbor in self.crossword.neighbors(key):
                if neighbor in assignment:
                    key_overlap =self.crossword.overlaps[key,neighbor][0]
                    neighbor_overlap =self.crossword.overlaps[key,neighbor][1]
                    key_letter = assignment[key][key_overlap]
                    neighbor_letter = assignment[neighbor][neighbor_overlap]
                    if key_letter!=neighbor_letter:
                        return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        #Create list will all words
        list_var = list(self.domains[var])

        var_dict = {}
        for word in self.domains[var]:
            count = 0
            #Create a count based on how many valuables get rules out using current word, add count to dictionary
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    #print(neighbor)
                    key_overlap =word[self.crossword.overlaps[var,neighbor][0]]
                    for neighbor_word in self.domains[neighbor]:
                        neighbor_space =self.crossword.overlaps[var,neighbor][1]
                        neighbor_overlap = neighbor_word[neighbor_space]
                        if key_overlap != neighbor_overlap:
                            count+=1
            var_dict[word]=count
        
        #Sort list based on dictionary value
        list_var.sort(key=lambda x: var_dict[x])

        return list_var
        #raise NotImplementedError

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        variable_list = []
        for variable in self.domains:
            #add every variable not in assignment to new list
            if variable not in assignment:
                variable_list.append(variable)        

        #Sort list but length of possible words, followed by number of neighbors
        variable_list.sort(key=lambda x: (len(self.domains[x]),-1*(len(self.crossword.neighbors(x)))))
        return variable_list[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
 
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            test_assignment = assignment.copy()
            test_assignment[var]=value
            if self.consistent(test_assignment):
                assignment = test_assignment.copy()
                result = self.backtrack(assignment)
                if result != None:
                    return result
                del assignment[var]
        return None



def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
