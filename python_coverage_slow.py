from numpy import *
from numpy.random import *
from matplotlib.pyplot import *
import sys
import time
import random
#---------------------------------------------#
#   InsertCoord: Place coordinate into list   #
#                if it meets distance requ-   #
#                irements.                    #
#---------------------------------------------#

def insertCoord(coord, coor_list, metric):
    for coor in coor_list:
        dist = sqrt( abs(coord[0]-coor[0]) + abs((coord[1]-coor[1]))**3 )
        if( dist < metric ):
            return 1
    coor_list.append(coord)
    return 0

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
#       Main Program: generate and plot       #
#                     list based on metric    #
#                     requirements            #
#                                             #
#---------------------------------------------#

metric = 0.1                                # Lower limit on distance
if(len(sys.argv) == 2):                     # Check params for new metric
    metric = float(sys.argv[1])             # ... and set it if exists

m = 5                                       # Number of columns
n = 5                                       # number of rows

max_tries = [10,100,1000,10000]             # logarithmic tries test nums

runtime_data = []                           # instantiate arrays for variance
pct_cov_data = []                           # data in runtime and coverage

for i in range(1,6):                        # performs n-1 trials (default = 5)

    percent_coverage = []                   # runtime and percent coverage data
    runtime = []                            # for each try number stored here

    for try_max in max_tries:
        print('Metric: ',metric,'; Number of Tries: ',try_max,';')

        num_tries = 0                       # intansiate dynamic try counter
        num_points = 0                      # total number of coordinates placed

        coor_list = []

        grid_accept = [[0 for x in range(n)] for y in range(m)]
        grid_reject = [[0 for x in range(n)] for y in range(m)]


        start_time = time.time()            # hold start time to check difference
        random.seed(time.time())            # seed the rng from clock time


        while True:
            x = random.random()             # Instantiate x and y as
            y = random.random()             # a random coordinate
            new_coord = [x,y]

            r, c = getTile(new_coord, m, n)
            test_val = random.random()
            posterior = 0
            if grid_reject[r][c] != 0 or grid_accept[r][c] != 0:
                posterior = grid_reject[r][c]/(grid_accept[r][c] + grid_reject[r][c])

            if posterior < test_val:

                sc = insertCoord(new_coord, coor_list,metric) # attempt to insert

                if sc == 0:                     # the coord was accepted
                    num_points += 1
                    grid_accept[r][c] += 1
                    num_tries = 0
                else:                           # ''   ''   ''  rejected
                    num_tries += 1
                    grid_reject[r][c] += 1
            else:
                num_tries += 1
                grid_reject[r][c] += 1

            if num_tries == try_max :       # if number of tries met, stop
                break

        runtime.append(time.time()-start_time)  # add runtime data


#---------------- PRINTING SCATTERPLOTS ----------------------------------

        x_l = []
        y_l = []
        for coor in coor_list:
            x_l.append(coor[0])
            y_l.append(coor[1])
        fig_num = log10(try_max)
        figure(fig_num+8*i)
        scatter(x_l,y_l,color='blue')

        x_grid = arange(0,1,metric)
        y_grid = arange(0,1,metric)
        grid_list = []
        grid_size = (1/metric)**2
        for x in x_grid:
            for y in y_grid:
                grid_coord = [x,y]
                sc = insertCoord(grid_coord,coor_list,metric)
                if sc == 0:
                    grid_list.append(grid_coord)


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
        savefig(fig_title)



#---------------- COVERAGE/RUNTIME PLOTS ---------------------------------

    figure(7+8*i)
    ax = gca()
    scatter(max_tries,percent_coverage)
    ax.set_xscale('log')
    cov_title = 'coverage_'+str(i)+'.png'
    savefig(cov_title)

    figure(8+8*i)
    ax = gca()
    scatter(max_tries,runtime)
    ax.set_xscale('log')
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
errorbar(max_tries,run_avg,yerr=run_var,fmt='o')
ax.set_xscale('log')
xlim([0.1,10000000])
savefig('runtime.png')


figure(401)
ax = gca()
errorbar(max_tries,cov_avg,yerr=cov_var,fmt='o')
ax.set_xscale('log')
xlim([0.1,10000000])
savefig('coverage.png')


figure(403)
ax = gca()
errorbar(run_avg,cov_avg,xerr=run_avg,yerr=cov_var,fmt='o')
savefig('run_coverage.png')








#-------------------------------------------------------------------------#
#                        END OF TEMPLATE.PY                               #
#-------------------------------------------------------------------------#
