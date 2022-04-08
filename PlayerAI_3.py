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
    a=0.0
    b=1.0 #equal weights for right now, need to figure out how I want to loop over these 
    wm=[]
    #value chosen for weight matrix to make the anchoring outweigh 
    #this was tuned a little bit/worked out by hand on smaller scales
    def empty_cells(self, grid):
        a= grid.getAvailableCells()
        u=len(a)
        #the cost is set as the number of non-zero spaces
        #cost to merge all cells if all cells are of equal value
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
                    if v<u:
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
                    if v<u:
                        c= u/v
                        util+= math.log(c,2)
                        #this would be the number of necessary moves to keep merge the two without having to build any extras
                else:
                    continue
        #summing over these costs gives minimum number of moves to merge all cells-1 
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

    def expectimax(self, grid, depth=0):
        
        moveset=grid.getAvailableMoves()
        cs=self.generate_player_children(moveset, grid)
        maxu=0
        bestmove=None
        if time.process_time()>= self.t_end:
            for c in cs:
                u=self.util(c[1])
                if u > maxu or (maxu==0 and u==0):
                    maxu=u
                    bestmove=c[0]
            return bestmove, maxu

        for c in cs:
            u=self.chance(c[1], depth+1)
            if u >maxu or (maxu==0 and u==0):
                maxu=u
                bestmove=c[0]
        return bestmove, maxu
    def chance(self, grid, depth=0):
        nempt=self.empty_cells(grid)
        if time.process_time() >=self.t_end or depth>=100:
            return self.util(grid)
        if nempt==0:
            _, u = self.expectimax(grid, depth+1)
            return u
        poss=[]
        chance_2=(0.9*(1/nempt))
        chance_4=(0.1*(1/nempt))
        for e in grid.getAvailableCells():
            poss.append([e, 2, chance_2])
            poss.append([e, 4, chance_4])
        usum=0
        for t in poss:
            chance_grid=grid.clone()
            chance_grid.insertTile(t[0], t[1])
            _, u =self.expectimax(chance_grid)
            usum+=u*t[2]
        return usum
        
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
