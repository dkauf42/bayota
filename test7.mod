# Tests For LRSEGS N51133RL0_6450_0000 in Northumberland, VA (LRSEGSid=1677)
# Land Segment (geographyid=6465) (with geographytypeid=17)
# FIPS=51133
# countyid=65
# stateid=7
# totalacres=58,040.90
# totalacresincludingtidalwetlands=60,642.83
#
# BaseYear=2010 (Baseconditionid=29)
# CostProfile=Watershed (costprofileid=4)
#
# Agencies present (Only one!) : agencyid=9 (NONFED), with 58,040.90 acres
#   So, we're neglecting to include the AGENCY set for now
#
# Data sources:
#   The (PLTNTS) pollutant set elements are just {N, P, S}
#   The (LRSEGS) land river segment set elements are in source.TblLandRiverSegment
#
#   The (LOADSRCS) load source set elements are in source.TblLoadSource
#   The (LOADSRCGRPS) load source group set elements are in source.TblLoadSourceGroup
#
#   The (BMPs) BMPS set elements are in source.TblBMPS
#   The (BMPGRPS) BMP-group set elements are in source.TblBMPS
#
#
#   The (c) cost parameter data is in metadata.TblCostBMPSLand
#   The (E) efficiency parameter data is in source.TblBmpEfficiency
#
#   The (tau) target percent load reduction (tau) are currently made-up values
#   The (phi) base loading rate of pollutants (phi) come from a CAST report of EOS loads for a "No-Action scenario"
#
#   The (T) total acres available are in source.TblLandUsePreBmp
#
# 2018

model;

# ---- Sets ---- #
set PLTNTS;                      # Pollutants N, P, S
set LRSEGS;                      # Land River Segments

set BMPS;
set BMPGRPS;
set BMPGRPING within {BMPS, BMPGRPS};  # BMPGRPING is one large set of pairs,
                                       # such that (b, gamma) is a member
                                       # of GRPING if and only bmp b belongs
                                       # to group gamma.

set LOADSRCS;         # Load Sources that belong to a group with a sinlge load source
#set SINGLEGRPLOADSRCS within LOADSRCS;         # Load Sources that belong to a group with a sinlge load source
#set LOADSRCGRPS;      # Load Source Groups
#set SINGLELSGRPS within LOADSRCGRPS;

# set BMPSINGLELSGRPING within {BMPS, SINGLELSGRPS}

set BMPSRCLINKS within {BMPS, LOADSRCS};

set BMPGRPSRCLINKS within {BMPGRPS, LOADSRCS};

#set BMPLOADSRCGRPS {b in BMPS} within LOADSRCGRPS;
#set GRPLOADSRCS {LOADSRCGRPS} within LOADSRCS;

# We want to be able to condition the sum by: Does this gamma exist for a specific lambda?!?
#set BMPLOADSRCGRPS {psi in LOADSRCGRPS} within BMPS;
#set GRPLOADSRCS {lambda in LOADSRCS} within LOADSRCGRPS;#

#set LOADSRCGRPSBYBMP {b in BMPS} within LOADSRCGRPS;
#set LOADSRCSBYLOADSRCGRPS {psi in LOADSRCGRPS} within LOADSRCS;

#set LOADSRCSBYBMP {b in BMPS} within LOADSRCGRPS;

# set SINGLESRCGRPING within {LOADSRCS, SINGLELSGRPS};  # SINGLESRCGRPING is one large set of pairs,
                                                   # such that (lambda, psi) is a member
                                                   # of GRPING if and only if loadsource lambda
                                                   # is the only load source belonging to group psi.

#set SRCBMPFIT {b in BMPS} within {BMPS, LOADSRCGRPSS};  # SRCBMPFIT is one large set of pairs,
                                           # such that (b, psi) is a member
                                           # of SRCBMPFIT if and only bmp b can
                                           # be applied to load source group psi.

#  set GRPING {BMPGRPS} within BMPS
# For each gamma in BMPGRPS,
# there is a separate set GRPING[gamma],
# which is the set of BMPSs belonging to bmp-group gamma.

# ---- Parameters ---- #
param c {b in BMPS} >= 0;  # cost per acre of BMP b
param E {b in BMPS, p in PLTNTS, l in LRSEGS, lambda in LOADSRCS} >= 0;  # effectiveness per acre of BMP b

param tau {l in LRSEGS, p in PLTNTS};  # target percent load reduction
param phi {l in LRSEGS, lambda in LOADSRCS, p in PLTNTS};  # base nutrient load per load source
    # or should it be "acresavail {LRSEGS}"?

param T {l in LRSEGS, lambda in LOADSRCS} >= 0;  # total acres available in an lrseg/load source

#param r {l in LRSEGS} >= 0;  # total number of load sources in each LRSEG
#param m {psi in LOADSRCGRPS} >= 0;  # total number of load sources in each LOADSRCGRP
#param n {gamma in BMPGRPS} >= 0;  # total number of BMPs in each BMPGRP
# ^ These parameters (r, m, n) might not be necessary

param originalload {l in LRSEGS, p in PLTNTS} =
    sum {lambda in LOADSRCS} phi[l, lambda, p] * T[l, lambda];

#param reducedload {l in LRSEGS, p in PLTNTS};  # will be calculated as a constraint

# for each group gamma, the sum should be over all BMPs b such that (b,gamma) is a valid pair
# will be calculated as a constraint
#param Fb {b in BMPS, l in LRSEGS, lambda in LOADSRCS, p in PLTNTS};  # In-bmp Pass Through Factor
#param F {gamma in BMPGRPS, l in LRSEGS, lambda in LOADSRCS, p in PLTNTS};  # In-group Pass Through Factor
#param Fstar {l in LRSEGS, lambda in LOADSRCS, p in PLTNTS};  # All-group Pass Through Factor


# ---- Variables ---- #
var x {b in BMPS, LRSEGS, lambda in LOADSRCS: (b,lambda) in BMPSRCLINKS} >= 0;

var reducedload {l in LRSEGS, p in PLTNTS} = sum {lambda in LOADSRCS}
    phi[l,lambda,p] * T[l,lambda] *
    prod {gamma in BMPGRPS: (gamma,lambda) in BMPGRPSRCLINKS}
         (1 - sum {b in BMPS: (b,gamma) in BMPGRPING &&
                              (b,lambda) in BMPSRCLINKS
                   }
                   (if T[l,lambda] <= 1e-6 then 0 else (x[b,l,lambda]/
                                                         T[l,lambda]
                                                         )
                    ) * E[b,p,l,lambda]
          );

var percentreduction {l in LRSEGS, p in PLTNTS} =
    ( (originalload[l,p] - reducedload[l,p]) / originalload[l,p] ) * 100;


# ---- Constraints ---- #
    # (main)
subject to TargetReduction {l in LRSEGS, p in PLTNTS}:
    percentreduction[l,p] >= tau[l,p];

    # BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC
subject to AdditiveBMPSAcreBound {gamma in BMPGRPS, l in LRSEGS, lambda in LOADSRCS}:
    sum {b in BMPS: (b,gamma) in BMPGRPING &&
                    (b,lambda) in BMPSRCLINKS}
        x[b,l,lambda] <= T[l,lambda];


# ---- Objective ---- #
minimize Total_Cost:
    sum {l in LRSEGS, lambda in LOADSRCS, b in BMPS: (b,lambda) in BMPSRCLINKS}
        c[b] * x[b,l,lambda];


            #sum {j in 1..4} a[i,j]/x[j]<=b[i];

#
#let x[1] := 1;
#let x[2] := 1;
#let x[3] := 1;
#let x[4] := 1;
