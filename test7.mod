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
#   The (tau) target percent load reduction (tau) are  user-specified for a problem instance
#   The (phi) base loading rate of pollutants (phi) come from a CAST report of EOT loads for a "No-Action scenario"
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

set BMPSRCLINKS within {BMPS, LOADSRCS};  # BMPSRCLINKS is one large set of pairs,
                                          # such that (b, lambda) is a member
                                          # if and only bmp b can be applied
                                          # to loadsource lambda.

set BMPGRPSRCLINKS within {BMPGRPS, LOADSRCS};  # BMPGRPSRCLINKS is one large set of pairs,
                                                # such that (gamma, lambda) is a member
                                                # if and only bmpgrp gamma can be applied
                                                # to loadsource lambda.

# ---- Parameters ---- #
param c {b in BMPS} >= 0;  # cost per acre of BMP b
param E {b in BMPS, p in PLTNTS, l in LRSEGS, lambda in LOADSRCS} >= 0;  # effectiveness per acre of BMP b

param tau {l in LRSEGS, p in PLTNTS};  # target percent load reduction
param phi {l in LRSEGS, lambda in LOADSRCS, p in PLTNTS};  # base nutrient load per load source
    # or should it be "acresavail {LRSEGS}"?

param T {l in LRSEGS, lambda in LOADSRCS} >= 0;  # total acres available in an lrseg/load source

param originalload {l in LRSEGS, p in PLTNTS} =
    sum {lambda in LOADSRCS} phi[l, lambda, p] * T[l, lambda];

# ---- Variables ---- #
var x {b in BMPS, LRSEGS, lambda in LOADSRCS: (b,lambda) in BMPSRCLINKS} >= 0;

var newload {l in LRSEGS, p in PLTNTS} = sum {lambda in LOADSRCS}
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

# ---- Constraints ---- #
    # Relative load reductions must be greater than the specified target percentages (tau)
subject to TargetPercentReduction {l in LRSEGS, p in PLTNTS}:
    (( (originalload[l,p] - newload[l,p]) / originalload[l,p] ) * 100) >= tau[l,p];

    # BMPs within a BMPGRP cannot use more than the acres in a LRSEG,LOADSRC
subject to AdditiveBMPSAcreBound {gamma in BMPGRPS, l in LRSEGS, lambda in LOADSRCS}:
    sum {b in BMPS: (b,gamma) in BMPGRPING &&
                    (b,lambda) in BMPSRCLINKS}
        x[b,l,lambda] <= T[l,lambda];


# ---- Objective ---- #
minimize Total_Cost:
    sum {l in LRSEGS, lambda in LOADSRCS, b in BMPS: (b,lambda) in BMPSRCLINKS}
        c[b] * x[b,l,lambda];
