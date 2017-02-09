#include <stdio.h>
#include <omp.h>
#include <stddef.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>

#define rand_num ((double)rand()/(double)RAND_MAX)
#define ROW_SIZE 5
#define COL_SIZE 5

double      **createArrayDbl(void);


int main(int argc, char *argv[])
{
    
    //---Variables---
    double metric = 0.05;
    size_t num_trials = 5;
    size_t num_vals = 1;
    int try = atoi(argv[1]);
    double maxTry[] = {try};
    //---------------

	// Store analytics as 2D arrays
    double runtime_data[num_trials][num_vals];
    double pct_cov_data[num_trials][num_vals];

	//Open discrete files for individual runs
    FILE *files[5];
    files[0] = fopen("data0.txt","w");
    files[1] = fopen("data1.txt","w");
    files[2] = fopen("data2.txt","w");
    files[3] = fopen("data3.txt","w");
    files[4] = fopen("data4.txt","w");    
    FILE *runtimes = fopen("runDat.txt","w");

	//run over several trials
    for(size_t trial_ID = 0; trial_ID < num_trials; ++trial_ID)
    {
        double runtime[num_vals], percent_coverage[num_vals];
        for(size_t post_ID = 0; post_ID < num_vals; ++post_ID)
        {
            int MAX_TRY = maxTry[post_ID];

            printf("Set %lu; Metric: %f; Maximum Trial: %d;\n",trial_ID,
														metric,MAX_TRY);
														
            size_t num_tries = 0;
            size_t num_points_total = 0;

            double coor_list[100000][2];
            int coor_size;


            struct timespec start = {0,0}, finish = {0,0};
            clock_gettime(CLOCK_MONOTONIC, &start);
            omp_set_num_threads(ROW_SIZE*COL_SIZE);
    #pragma omp parallel shared(files,coor_size,coor_list)
    {
            int thd_ID = omp_get_thread_num();
            
            srand(time(NULL)*(thd_ID+1));
            int num_points = 0,num_tried=0;
            double grid_accept = 0, grid_reject = 0;
            while(1)
            {
                int row = thd_ID / ROW_SIZE;
                int col = thd_ID % ROW_SIZE;
                

                double x = (rand_num+(double)row)/(double)ROW_SIZE;
                double y = (rand_num+(double)col)/(double)COL_SIZE;
               
                double base,height,y_min,y_max;
                if( x < 0.5 )
                {
                    base = 0.5-x;
                }
                else
                {
                    base = x-0.5;
                }
                height = sqrt(0.25-base*base);
                y_min = 0.5-height;
                y_max = 0.5+height;
                if(y > y_max || y < y_min)continue;


                double new_coord[2] = {x,y};
                //printf("New_Coord: %f,%f\n",new_coord[0],new_coord[1]); 
                double exitStat;
                if( grid_reject != 0 || grid_accept != 0 )
                    exitStat = grid_reject/(grid_accept + grid_reject);
                else
                    exitStat = 0;


                int shouldAdd = 1;
                int index = -1;
                for( int i = 0; i < 100000; ++i )
                {
                    if(coor_list[i][0]==0 && coor_list[i][1] == 0)
                    {
                        shouldAdd = 1;
                        index = i;
                        break;
                    }
                    double testCoord[2] = {coor_list[i][0],coor_list[i][1]};
                    double del_x = fabs(new_coord[0] - testCoord[0]);
                    double del_y = fabs(new_coord[1] - testCoord[1]);

                    double dist  = sqrt(del_x*del_x + del_y*del_y);
                    if( dist < metric )
                    {
                        shouldAdd = 0;
                        break;
                    }
                }
            

                if(shouldAdd == 1)
                {
                    num_tried = 0;
                    num_points++;
                    grid_accept++;
                    coor_list[index][0] = new_coord[0];
                    coor_list[index][1] = new_coord[1];
                }
                else
                {
                    num_tried++;
                    grid_reject++;
                }

                if( num_tried == MAX_TRY  )
                {
                    break;
                }
           
            }

    }//end parallel        
            for(int j = 0; j < 100000; ++j)
            {
                if(coor_list[j][0] == 0 && coor_list[j][1] == 0) break;
                else
                    fprintf(files[trial_ID], "%f , %f\n",coor_list[j][0],coor_list[j][1]);
            }
            clock_gettime(CLOCK_MONOTONIC, &finish);
            double runtime = -((double)start.tv_sec + 1.0e-9*start.tv_nsec) +
                              ((double)finish.tv_sec + 1.0e-9*finish.tv_nsec);
            
            printf("Runtime: %f seconds\n",runtime); 
            fprintf(runtimes,"%f\n",runtime);

        }
        fclose(files[trial_ID]);
    }
    
}

double  **createArrayDbl(void)
{
    double *values = calloc(ROW_SIZE*COL_SIZE, sizeof(double));
    double  **rows = malloc(COL_SIZE * sizeof(double*));
    for(int i = 0; i<COL_SIZE; ++i)
    {
        rows[i] = values + i*ROW_SIZE;
    }
    return rows;
}
