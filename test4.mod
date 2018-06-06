# Tests For LRSEGS N51133RL0_6450_0000 in Northumberland, VA (LRSEGSid=1677)
# Land Segment (geographyid=6465) (with geographytypeid=17)
# FIPS=51133
# countyid=65
# stateid=7
# totalacres=58,040.90
# totalacresincludingtidalwetlands=60,642.83
#
# BaseYear=2010 (Baseconditionid=29)
#
# Agencies present (Only one!) : agencyid=9 (NONFED), with 58,040.90 acres
#   So, we're neglecting to include the AGENCY set for now
#
# Data sources:
#   The pollutant set elements (PLTNTS) are just {N, P, S}
#   The land river segment set elements (LRSEGS) are in source.TblLandRiverSegment
#
#   The load source set elements (LOADSRCS) are in source.TblLoadSource
#   The load source group set elements (LOADSRCGRPS) are in source.TblLoadSourceGroup
#
#   The BMPS set elements (BMPS) are in source.TblBMPS
#   The BMP-group set elements (BMPGRPS) are in source.TblBMPS
#  
#   The cost parameter data (cost) is in metadata.TblCostBMPSLand
#   The efficiency parameter data (e) is in source.TblBmpEfficiency
#
#   The target percent load reduction (tau)
#   The total acres available come from 
#
#   The base nutrient loads come from a CAST report of EOS loads for a "No-Action scenario"
# 
# 2018

model;

# ---- Sets ---- #
set PLTNTS;  # Pollutants N, P, S
set LRSEGS;  # Land River Segments

set LOADSRCS;  # Load Sources
set LOADSRCGRPS;  # Load Source Groups
set LOADSRCGRPING within {LOADSRCS, LOADSRCGRPS};

set BMPS;
set BMPGRPS;
set BMPGRPING within {BMPS, BMPGRPS};  # BMPGRPING is one large set of pairs,
                                       # such that (b, gamma) is a member
                                       # of GRPING if and only bmp b belongs 
                                       # to group gamma.

#  set GRPING {BMPGRPS} within BMPS
# For each gamma in BMPGRPS,
# there is a separate set GRPING[gamma],
# which is the set of BMPSs belonging to bmp-group gamma. 

# ---- Parameters ---- #
param c {b in BMPS} >= 0;  # cost per acre of BMP b
param E {b in BMPS, p in PLTNTS, l in LRSEGS, lambda in LOADSRCS};  # effectiveness per acre of BMP b
param tau {l in LRSEGS, p in PLTNTS};  # target percent load reduction
param T {l in LRSEGS, lambda in LOADSRCS} >= 0;  # total acres available in an lrseg/load source
    # or should it be "acresavail {LRSEGS}"?

#param r {l in LRSEGS} >= 0;  # total number of load sources in each LRSEG
#param m {psi in LOADSRCGRPS} >= 0;  # total number of load sources in each LOADSRCGRP
#param n {gamma in BMPGRPS} >= 0;  # total number of BMPs in each BMPGRP
# ^ These parameters (r, m, n) might not be necessary

param phi {l in LRSEGS, lambda in LOADSRCS, p in PLTNTS};  # base nutrient load per load source

param originalload {l in LRSEGS, p in PLTNTS} = 
    sum {lambda in LOADSRCS} phi[l, lambda, p] * T[l, lambda];
param reducedload {l in LRSEGS, p in PLTNTS};  # will be calculated as a constraint
    
# for each group gamma, the sum should be over all BMPs b such that (b,gamma) is a valid pair
# will be calculated as a constraint
param F {gamma in BMPGRPS, l in LRSEGS, lambda in LOADSRCGRPS, p in PLTNTS};  # In-group Pass Through Factor
param Fstar {l in LRSEGS, lambda in LOADSRCGRPS, p in PLTNTS};  # In-group Pass Through Factor


# ---- Variables ---- #
var x {BMPS, LRSEGS, LOADSRCS} >= 0;


# ---- Constraints ---- #
    # Achieve the Target Load Reduction
    # (Intermediate Calculation) In-Group Pass Through Factor
subject to InGroupFactor {gamma in BMPGRPS, l in LRSEGS, lambda in LOADSRCS, p in PLTNTS}:
    F[gamma,l,lambda,p] = 
    1 - sum {b in BMPS: (b,gamma) in BMPGRPING} (x[b,l,lambda]/T[l,lambda]) * E[b,p,l,lambda];
    # (Intermediate Calculation) All-Group Pass Through Factor
subject to AllGroupFactor {l in LRSEGS, lambda in LOADSRCGRPS, p in PLTNTS}:
    Fstar[l,lambda,p] = prod {gamma in BMPGRPS} F[gamma,l,lambda,p];
    # (Intermediate Calculation) Reduced Pollutant Load
subject to ReducedLoadCalc {l in LRSEGS, p in PLTNTS}:
    reducedload[l,p] = 
    sum {lambda in LOADSRCS} phi[l,lambda,p] * T[l,lambda] * Fstar[l,lambda,p];
    # (main)
subject to TargetReduction {l in LRSEGS, p in PLTNTS}:
    ( (originalload[l,p] - reducedload[l,p]) / originalload[l,p] ) * 100 >= tau[l,p];

    # BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC
subject to AdditiveBMPSAcreBound {gamma in BMPGRPS, l in LRSEGS, lambda in LOADSRCS}:
    sum {b in BMPS: (b,gamma) in BMPGRPING} x[b,l,lambda] <= T[l,lambda];

# ---- Objective ---- #
minimize Total_Cost:
    sum {l in LRSEGS, lambda in LOADSRCS, b in BMPS} c[b] * x[b,l,lambda];
    
          
            #sum {j in 1..4} a[i,j]/x[j]<=b[i];

# 
#let x[1] := 1;
#let x[2] := 1;
#let x[3] := 1;
#let x[4] := 1;
