from numpy import *
from numpy.random import *
from matplotlib.pyplot import *
import sys,time,random,bisect
from subprocess import call
#---------------------------------------------#
#   InsertCoord: Place coordinate into list   #
#                if it meets distance requ-   #
#                irements.                    #
#---------------------------------------------#

def insertCoord(coord, coor_list,insert_list, metric):
    for coor in coor_list:
        dist = sqrt( abs(coord[0]-coor[0])**2 + abs((coord[1]-coor[1]))**2 )
        if( dist < metric ):
            return 1
    insert_list.append(coord)
    return 0


#---------------------------------------------#
#                                             #
#   getTileList: Returns list of elements in  #
#            tiles adjacent to the current    #
#            tile.                            #
#                                             #
#---------------------------------------------#

def getTileList(coor_tiles,r,c):

    short_list = []

    m = len(coor_tiles)             # number of rows
    n = len(coor_tiles[0])          # number of columns

    short_list.extend(coor_tiles[r][c])

    if r > 0:
        short_list.extend(coor_tiles[r-1][c])
        if c > 0:
            short_list.extend(coor_tiles[r-1][c-1])
        if c < n-1:
            short_list.extend(coor_tiles[r-1][c+1])
    if r < m-1:
        short_list.extend(coor_tiles[r+1][c])
        if c > 0:
            short_list.extend(coor_tiles[r+1][c-1])
        if c < n-1:
            short_list.extend(coor_tiles[r+1][c+1])
    if c > 0:
        short_list.extend(coor_tiles[r][c-1])
    if c < n-1:
        short_list.extend(coor_tiles[r][c+1])

    return short_list


#---------------------------------------------#
#                                             #
#   getTile: Returns the coordinate location  #
#            of the tile in the grid that     #
#            this point lives, -1 if err      #
#                                             #
#---------------------------------------------#

def getTile(coord,m,n):
    mp = np = -1
    dx = 1/m
    dy = 1/n
    x = coord[0]
    y = coord[1]
    for i in range(m):
        if( x >= dx*i and x <= dx*(i+1) ):
                mp = i
                break
    for j in range(n):
        if( y >= dy*j and y <= dy*(j+1) ):
                np = j
                break

    return np,mp

#---------------------------------------------#
#                                             #
#       calcPost: calculates the posterior    #
#                 for each grid value in      #
#                 the set. returns 2D array   #
#                                             #
#---------------------------------------------#

def calcPost(accept,reject):
    post = [[0 for x in range(n)] for y in range(m)]
    for r in range(len(accept)):
        for c in range(len(accept[0])):
            if reject[r][c] != 0 or accept[r][c] != 0:
                post[r][c] = reject[r][c]/(accept[r][c] + reject[r][c])
            else:
                post[r][c] = 0
    return post

#---------------------------------------------#
#                                             #
#       testPost: tests posterior for exit    #
#                 case of each cell having    #
#                 above a threshold post      #
#                                             #
#---------------------------------------------#

def testPost(post,maxPost):

    for i in range(len(post)):
        for j in range(len(post[0])):
            if post[i][j] < maxPost :
                return 1
    return 0


#---------------------------------------------#
#                                             #
#       Main Program: generate and plot       #
#                     list based on metric    #
#                     requirements            #
#                                             #
#---------------------------------------------#

metric = 0.05                                # Lower limit on distance
if(len(sys.argv) == 2):                     # Check params for new metric
    metric = float(sys.argv[1])             # ... and set it if exists

m = 5                                       # Number of columns
n = 5                                       # number of rows


max_try = [10,100,1000,10000,10000,100000]

runtime_data = []                           # instantiate arrays for variance
pct_cov_data = []                           # data in runtime and coverage

for MAX_TRY in max_try:
    print('Metric: ',metric,'; Maximum Posterior: ',MAX_TRY,';')
    percent_coverage = []

    call(["./template",str(MAX_TRY)])

#------------ PRINTING SCATTERPLOTS ----------------------------------
    for i in range(0,5):
        filename = "data"+str(i)+".txt"
        coor_list = loadtxt(filename,delimiter=",").tolist()
        x_l = []
        y_l = []
        for coor in coor_list:
            x_l.append(coor[0])
            y_l.append(coor[1])
        fig_num = MAX_TRY
        figure(fig_num+8*i)
        scatter(x_l,y_l,color='blue')

        x_grid = arange(0,1,metric/2)
        y_grid = arange(0,1,metric/2)
        grid_list = []


        #    calculate the grid size
        test_coord_list = []
        for x in x_grid:
            for y in y_grid:
                if(x<0.5):
                    base = 0.5-x
                else:
                    base = x-0.5
                height = sqrt(0.25-base**2)
                if(y > 0.5+height or y < 0.5-height):
                    continue
                grid_coord = [x,y]
                sc = insertCoord(grid_coord,coor_list,coor_list,metric)
                sc2 = insertCoord(grid_coord,test_coord_list,test_coord_list,metric)
                if sc == 0:
                    grid_list.append(grid_coord)

        grid_size = len(test_coord_list)


        this_pct_cov = (1 - len(grid_list)/grid_size)*100
        print('Percent Coverage: ',this_pct_cov)
        percent_coverage.append(this_pct_cov)

        x_gl = []
        y_gl = []

        for cor in grid_list:
            x_gl.append(cor[0])
            y_gl.append(cor[1])
        scatter(x_gl,y_gl,color='red')

        fig_title = 'scatter_'+ str(i) +'_'+ str(fig_num) + '.png'
        xlabel('x')
        ylabel('y')
        savefig(fig_title)
    runtime_data.append(loadtxt("runDat.txt").tolist())
    pct_cov_data.append(percent_coverage)



#---------------- COVERAGE/RUNTIME PLOTS ---------------------------------



#---------------- ERROR PLOTS --------------------------------------------

run_var = []
cov_var = []
run_avg = []
cov_avg = []

for tryal in runtime_data:
    run_var.append(std(tryal))
    run_avg.append(mean(tryal))


for a in pct_cov_data:
    cov_var.append(std(a))
    cov_avg.append(mean(a))


figure(400)
ax = gca()
errorbar(max_try,run_avg,yerr=run_var,fmt='o')
ax.set_xscale('log')
xlim(1,1000000)
xlabel('Maximum Posterior')
ylabel('Clock Runtime (s)')
savefig('runtime.png')


figure(401)
ax = gca()
errorbar(max_try,cov_avg,yerr=cov_var,fmt='o')
ax.set_xscale('log')
xlim(1,1000000)
ylim(85,101)
xlabel('Maximum Posterior')
ylabel('Percent Coverage')
savefig('coverage.png')


figure(403)
ax = gca()
errorbar(run_avg,cov_avg,xerr=run_avg,yerr=cov_var,fmt='o')
xlabel('Clock Runtime (s)')
ylabel('Percent Coverage')
savefig('run_coverage.png')








#-------------------------------------------------------------------------#
#                        END OF TEMPLATE.PY                               #
#-------------------------------------------------------------------------#
