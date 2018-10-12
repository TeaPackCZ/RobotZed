import numpy as np

def ang2cartezian(angle,distance):
    k = len(distance)
    if(len(angle) == len(distance)):
        pass
    else:
        print "Error: inputs has different lengths"
        print len(angle), len(distance)
        return "",""
    x = np.zeros(k,np.float32)
    y = np.copy(x)
    for j in range(k):
        x[j] = np.cos(angle[j]/180.0*np.pi)*distance[j]
        y[j] = np.sin(angle[j]/180.0*np.pi)*distance[j]
    return x,y

def ang_segmentation(scan, max_diff = 150):
    ## Segmentation returns: [start_id, len_of_segment, segment_data]
    segments = []
    segm_start = []
    segm_start.append(0)
    start_segm = 0
    end_segm = 0
    for j in range(len(scan)-1):
        if(scan[j] == 0):
            # throw out scans out of range
            start_segm = j+1
        else:
            diff = abs(scan[j]-scan[j+1])
            if diff > max_diff:
                if(start_segm == j):
                    # throw out single points
                    start_segm = j+1
                    pass
                else:
                    end_segm = j
                    segments.append([segm_start[-1],len(scan[start_segm:end_segm+1]),np.asarray(scan[start_segm:end_segm+1])])
                    segm_start.append(j+1)
                    start_segm = j+1
    segments.append([start_segm,len(scan[start_segm:-1]),np.asarray(scan[start_segm:-1])])
    return segments

def cut_on_edges(X,Y):
    #compute diff
    gradients = []
    new_gradient = np.arctan((X[1]-X[0])/(Y[1]+Y[0]))
    gradients.append(new_gradient)
    print new_gradient
    for j in range(1,len(X)-1):
        old_gradient = new_gradient
        new_gradient = np.arctan((X[j+1]-X[j])/(Y[j+1]+Y[j]))
        grad_change = old_gradient/new_gradient
        gradients.append(grad_change)
        #print new_gradient
    #if diff change rapidly value -> cut and create new segment
    #return all segments
    return gradients

def gradient_of_segment(segments):
    # compute slope over all points in each segment
    #for segment in segments:
    return 0   
        
