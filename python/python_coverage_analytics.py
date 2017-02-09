from numpy import *
from numpy.random import *
from matplotlib.pyplot import *
import sys,time,random,bisect

#---------------------------------------------#
#   InsertCoord: Place coordinate into list   #
#                if it meets distance requ-   #
#                irements.                    #
#---------------------------------------------#

def insertCoord(coord, coor_list,insert_list, metric):
    for coor in coor_list:
        dist = sqrt( abs(coord[0]-coor[0]) + abs((coord[1]-coor[1]))**3 )
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

metric = 0.05                               # Lower limit on distance
if(len(sys.argv) == 2):                     # Check params for new metric
    metric = float(sys.argv[1])             # ... and set it if exists

m = 5                                       # Number of columns
n = 5                                       # number of rows


max_post = [0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,0.96,0.97,0.98,0.99,0.999]

runtime_data = []                           # instantiate arrays for variance
pct_cov_data = []                           # data in runtime and coverage

for i in range(1,10):                        # performs n-1 trials (default = 5)

    percent_coverage = []                   # runtime and percent coverage data
    runtime = []                            # for each try number stored here

    for MAX_POST in max_post:
        print('Metric: ',metric,'; Maximum Posterior: ',MAX_POST,';')

        num_tries = 0                       # intansiate dynamic try counter
        num_points = 0                      # total number of coordinates placed

        coor_list = []
        coor_tiles = [[ [] for x in range(n)] for y in range(m)]

        grid_accept = [[0 for x in range(n)] for y in range(m)]
        grid_reject = [[0 for x in range(n)] for y in range(m)]


        start_time = time.time()            # hold start time to check difference
        random.seed(time.time())            # seed the rng from clock time

        try_other_grid = 0                  # After a number of posterior rejects,
                                            # use the typical search strategy

        while True:
            x = random.random()             # Instantiate x and y as
            y = random.random()             # a random coordinate
            new_coord = [x,y]

            r, c = getTile(new_coord, m, n)
            test_val = random.random()

            posterior = calcPost(grid_accept,grid_reject)

            if posterior[r][c] < test_val or try_other_grid == 50:
                try_other_grid = 0
                short_list = getTileList(coor_tiles,r,c)
                sc = insertCoord(new_coord, short_list,coor_list,metric) # attempt to insert

                if sc == 0:                     # the coord was accepted
                    num_points += 1
                    grid_accept[r][c] += 1
                    coor_tiles[r][c].append(new_coord)
                else:                           # ''   ''   ''  rejected
                    grid_reject[r][c] += 1
            else:
                grid_reject[r][c] += 1
                try_other_grid += 1

            status = testPost(posterior, MAX_POST)
            if status == 0:
                break
        runtime.append(time.time()-start_time)  # add runtime data


#---------------- PRINTING SCATTERPLOTS ----------------------------------

        x_l = []
        y_l = []
        for coor in coor_list:
            x_l.append(coor[0])
            y_l.append(coor[1])
        fig_num = MAX_POST*1000
        figure(fig_num+8*i)
        scatter(x_l,y_l,color='blue')

        x_grid = arange(0,1,metric)
        y_grid = arange(0,1,metric)
        grid_list = []


        # calculate the grid size
        test_coord_list = []
        for x in x_grid:
            for y in y_grid:
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



#---------------- COVERAGE/RUNTIME PLOTS ---------------------------------

    figure(7+8*i)
    ax = gca()
    scatter(max_post,percent_coverage)
    cov_title = 'coverage_'+str(i)+'.png'
    savefig(cov_title)

    figure(8+8*i)
    ax = gca()
    scatter(max_post,runtime)
    run_title = 'runtime_'+str(i)+'.png'
    savefig(run_title)


    pct_cov_data.append(percent_coverage)
    runtime_data.append(runtime)


#---------------- ERROR PLOTS --------------------------------------------

run_var = []
cov_var = []
run_avg = []
cov_avg = []

for j in range(len(runtime_data[0])):
    a = []
    for k in range(len(runtime_data)):
        a.append(runtime_data[k][j])
    run_var.append(std(a))
    run_avg.append(mean(a))


for j in range(len(pct_cov_data[0])):
    a = []
    for k in range(len(pct_cov_data)):
        a.append(pct_cov_data[k][j])
    cov_var.append(std(a))
    cov_avg.append(mean(a))


figure(400)
ax = gca()
errorbar(max_post,run_avg,yerr=run_var,fmt='o')
xlabel('$p_{reject}$')
ylabel('Clock Runtime (s)')
savefig('runtime.png')


figure(401)
ax = gca()
errorbar(max_post,cov_avg,yerr=cov_var,fmt='o')
xlabel('$p_{reject}$')
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
