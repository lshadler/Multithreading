using PyPlot
m = 5
n = 5
metric = 0.05
max_post = [0.95,0.96,0.97,0.98,0.99,0.999]
#-----------------------------------
#  insert coord
#-----------------------------------
function insertCoord(coord, coor_list, insert_list, metric)
    for coor in coor_list
        dist = sqrt( abs(coord[1]-coor[1]) + abs(coord[2] - coor[2])^3)
        if( dist < metric )
            return 1
        end
    end
    push!(insert_list,coord)
    return 0
end



#-----------------------------------
#  getTileList
#-----------------------------------
function getTileList(coor_tiles,r,c)
    
    short_list = []
    append!(short_list,coor_tiles[r,c])

    if r > 1
        append!(short_list,coor_tiles[r-1,c])
        if c > 1
            append!(short_list,coor_tiles[r-1,c-1])
        end
        if c < n
            append!(short_list,coor_tiles[r-1,c+1])
        end
    end
    if r < m
        append!(short_list,coor_tiles[r+1,c])
        if c > 1
            append!(short_list,coor_tiles[r+1,c-1])
        end
        if c < n
            append!(short_list,coor_tiles[r+1,c+1])
        end
    end
    if c > 1
        append!(short_list,coor_tiles[r,c-1])
    end
    if c < n
        append!(short_list,coor_tiles[r,c+1])
    end
    return short_list
end



#-----------------------------------
#  getTile
#-----------------------------------
function getTile(coord,m,n)
    mp = np = -1
    dx = 1/m
    dy = 1/n
    x = coord[1]
    y = coord[2]

    
    for i in 1:m
        if( x >= dx*(i-1) && x <= dx*(i))
            mp = i
            break
        end
    end
    
    
    for j in 1:n
        if( y >= dy*(j-1) && y <= dy*(j))
            np = j
            break
        end
    end

    return [np,mp]
end


function calcPost(accept,reject)
    post = zeros(n,m)
    
    for r in 1:m
        for c in 1:n
            if( reject[r,c] != 0 || accept[r,c] != 0 )
                post[r,c] = reject[r,c]/(accept[r,c] + reject[r,c])
            else
                post[r,c] = 0
            end
        end
    end
    return post
end



function testPost(post,maxPost)
    for i in post
            if i < maxPost
                return 1
            end
    end
    return 0
end



#-------------------------------
#
#   Main Program
#
#-------------------------------

runtime_data = []
pct_cov_data = []

for i in 1:5
    percent_coverage = []
    runtime = []
    
    for MAX_POST in max_post
        println("Metric: $metric; Maximum Posterior: $MAX_POST;")
        
        num_tries = 0
        num_points = 0

        coor_list = []
        coor_tiles = Array(Any,m,n) 
        fill!(coor_tiles,[])
        grid_accept = zeros(n,m)
        grid_reject = zeros(n,m)

        srand(tic())
        
        try_other_grid = 0

        while true
            new_coord = [rand(),rand()]
            rc = getTile(new_coord, m, n)
            r = rc[1]
            c = rc[2]
            test_val = rand()
            
            posterior = calcPost(grid_accept,grid_reject)
            if( posterior[r,c] < test_val || try_other_grid == 50)
                try_other_grid = 0
               short_list = getTileList(coor_tiles,r,c)
                sc = insertCoord(new_coord,  short_list, coor_list, metric)
                
                if( sc == 0)
                    num_points += 1
                    grid_accept[r,c] += 1
                    push!(coor_tiles[r,c], new_coord)
                else   
                    grid_reject[r,c] += 1
                end
            else
                grid_reject[r,c] += 1
                try_other_grid += 1
            end
            if testPost(posterior, MAX_POST) == 0
                break
            end
        end
        eltime = toc()
        push!(runtime, eltime)

        x_l = []
        y_l = []
        for coor in coor_list
            push!(x_l,coor[1])
            push!(y_l,coor[2])
        end
        fig_num = MAX_POST*1000
        figure(fig_num+8*i)
        scatter(x_l,y_l,color="blue")

        x_grid = 0:metric:1
        y_grid = 0:metric:1
        grid_list = []


        # calculate the grid size
        test_coord_list = []
        for x in x_grid
            for y in y_grid
                grid_coord = [x,y]
                sc = insertCoord(grid_coord,coor_list,coor_list,metric)
                sc2 = insertCoord(grid_coord,test_coord_list,test_coord_list,metric)
                if sc == 0
                    push!(grid_list,grid_coord)
                end
            end
        end
        grid_size = length(test_coord_list)


        this_pct_cov = (1 - length(grid_list)/grid_size)*100
        println("Percent Coverage: ",this_pct_cov)
        push!(percent_coverage,this_pct_cov)

        x_gl = []
        y_gl = []

        for cor in grid_list
            push!(x_gl,cor[1])
            push!(y_gl,cor[2])
        end
        scatter(x_gl,y_gl,color="red")

        fig_title = "scatter_" * string(i) * "_" * string(fig_num) * ".png"
        xlabel("x")
        ylabel("y")
        savefig(fig_title)



   end

    figure(7+8*i)
    ax = gca()
    scatter(max_post,percent_coverage)
    cov_title = "coverage_" * string(i) * ".png"
    savefig(cov_title)

    figure(8+8*i)
    ax = gca()
    scatter(max_post,runtime)
    run_title = "runtime_" * string(i) * ".png"
    savefig(run_title)


    push!(pct_cov_data,percent_coverage)
    push!(runtime_data,runtime)

end







