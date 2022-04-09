import random
from BaseAI_3 import BaseAI
import math
import time
#have 3 heuristics, with optional 4th 
#this is prioritizing bottom left corner
#prioritizing empty spaces
#prioritizing decreasing values

class PlayerAI(BaseAI):
    s=0
    t_end=None
    a=0.2
    b=0.5 #equal weights for right now, need to figure out how I want to loop over these 
    wm=[]
    good_move=None
    #value chosen for weight matrix to make the anchoring outweigh 
    #this was tuned a little bit/worked out by hand on smaller scales
    def empty_cells(self, grid):
        a= grid.getAvailableCells()
        u=len(a)
        u=u/pow(self.s,2)
        #the util is set as the number of non-zero spaces
        return u
    def monocity(self, grid):
        util=0 #utility associated is given by the size of the jump
        for y in range(self.s):
            for x in range(self.s-1):
                if grid.crossBound([x,y]) and grid.crossBound([x+1, y]):
                    v=grid.getCellValue([x,y])
                    u=grid.getCellValue([x+1, y])
                    if u==0 or v==0 or v==u:
                        continue
                    c= u/v
                    util+=math.log(c,2) 
                    #util increases by powers of 2 
                    #penalty of the power
                    #this would be the number of necessary moves to keep merge the two without having to build any extras 
                else:
                    continue
            #this has taken care of increases in the horizontal
            #personally, I play in a slightly differnet manner but that is less systematic, 
            #I like to build bottom left to right then right to left otherwise
            #but that would probably mess with the other heuristics as well
            #and its a less systematic

        for x in range(self.s):
            for y in range(self.s-1):
                if grid.crossBound([x,y]) and grid.crossBound([x, y+1]):
                    v=grid.getCellValue([x,y])
                    u=grid.getCellValue([x, y+1])
                    if u==0 or v==0 or v==u:
                        continue
                    c= u/v
                    util+= math.log(c,2)
                        #this would be the number of necessary moves to keep merge the two without having to build any extras
                else:
                    continue
        #summing over these costs gives minimum number of moves to merge all cells-1 
        #normalize by getting value if all are in proper order
        vals=sorted([grid.getCellValue([x,y]) for x in range(self.s) for y in range(self.s)])
        mutil=0
        for x in range(len(vals)-1):
            v= vals[x]
            u=vals[x+1]
            if u==0 or v==0 or v==u:
                continue
            c= u/v
            mutil+= math.log(c,2)
            #given current board, if all the values were in order what would
            #the utility be. Use this to normalize
        if mutil==0:
            mutil=1
        util=util/mutil
        return util
    def weight_matrix(self, grid):
        #this is a bit trickier, idea is to want to put things as a triangle out from the bottom left
        utility=0 
        for x in range(self.s):
            for y in range(self.s):
                utility+=self.wm[x][y]*grid.getCellValue([x,y])
        mutility=0
        vals=sorted([grid.getCellValue([x,y]) for x in range(self.s) for y in range(self.s)])
        weights=sorted([self.wm[x][y] for x in range(self.s) for y in range(self.s)])
        for x in range(len(vals)):
            mutility+=vals[x]*weights[x] 

        utility=utility/mutility
        return utility
    def util(self, grid):
        w=self.weight_matrix(grid)
        e=self.empty_cells(grid)
        m=self.monocity(grid)
        #a and b are weights for each heuristic
        return self.a*w+self.b*e+(1-self.a-self.b)*m
#right now I have fully written the heuristics 
#need to run over multiple weights, but that should be done in a script outside of this
#for right now give the weights as they are, then fix them later
#will take as an input for the run

    def expectimax(self, grid, depth=1, alpha=float('-inf'), beta=float('inf'), found_move=False):
        #will perform search on a config to a given depth
        #idea is to implement s.t. IDS can be used 
        #default searching to depth 1
        #output to dictionary to 
        moveset=grid.getAvailableMoves()
        cs=self.generate_player_children(moveset, grid)
        if depth=0 and found_move or time.process_time >= self.t_end:
            utility=self.util(grid)
            output={"alpha": alpha, 
                    "beta": beta,
                    "move": self.good_move, 
                    "utility": utility}
            return output

        if found_move:
            for c in cs:
                d=expectimax(c[1], depth-1, alpha, beta)
                alpha=max(alpha, d["alpha"])
        else:
            for c in cs:
                l=c[1]
                o=chance_node(l, depth+1, alpha, beta)
                if o> alpha:
                    self.good_move=c[0]
                alpha=max(alpha, o)
                if beta<= alpha:
                    found_move=true
                    utility=self.util(grid)
                    output={"alpha": alpha,
                    "beta": beta,
                    "move": self.good_move,
                    "utility": utility}
            return output

            
    def chance_node(self, l, depth, alpha, beta):
                empty=l.getAvailableCells()
                n_empty=len(empty)
                chance_2=(0.9*(1/n_empty))
                chance_4=(0.1*(1/n_empty))
                #nodes are set up by inserting the chance nodes
                for e in empty:
                    lc2=l.clone()
                    lc4=l.clone()
                    lc2.insertTile(e,2)
                    lc4.insertTile(e,4)
                    #create grids with inserted of 2, 4
                    s2=self.expectimax(lc2, depth-1, alpha, beta, True)
                    s4=self.expectimax(lc4, depth-1, alpha, beta, True)
                    u=s2["utility"]*chance_2+s4["utility"]*chance_4
                    beta=min(beta, u)
                    if alpha >= beta:
                        break
                return beta
                    #stores the children with the relevant chance
                    
    def generate_player_children(self, moveset, grid):
        children_grids=[]
        for m in moveset:
            child=grid.clone()
            child.move(m)
            children_grids.append((m,child))
        return children_grids
    def getMove(self, grid):
    	# sets the max time one can take before forcing the returned best move
        self.t_end=time.process_time()+0.15
        self.s=grid.size
        self.wm=[[pow(self.s, i+j) for i in range(self.s)] for j in range(self.s)] 
        move,_=self.expectimax(grid)
        return move[0]
    	#moveset = grid.getAvailableMoves()
    	#return best_move(moveset, grid) if moveset else None
