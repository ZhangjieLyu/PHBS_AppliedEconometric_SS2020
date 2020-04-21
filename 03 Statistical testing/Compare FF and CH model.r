CH_3_select = CH5_onlyFilterTradingDaysAndOnlist[7:203,c("MKT","SMB","VMG")]
FF_3_select = FF5_onlyFilterTradingDaysAndOnlist[7:203,c("MKT","HML","SMB")]

library(lmtest)
library(sandwich)
library(GRS.test)
# FFSMB versus CH3
model_FFSMB = lm(FF_3_select$SMB~CH_3_select$MKT + 
                   CH_3_select$SMB + 
                   CH_3_select$VMG)
# summary(model_FFSMB)

# HC t-stat
coeftest(model_FFSMB, vcov = vcovHC(model_FFSMB))

# FFHML
model_FFHML = lm(FF_3_select$HML~CH_3_select$MKT  + 
                 CH_3_select$SMB + 
                 CH_3_select$VMG)
# summary(model_FFHML)

# HC t-stat
coeftest(model_FFHML, vcov = vcovHC(model_FFHML))

# SMB versus FF3
model_SMB = lm(CH_3_select$SMB~FF_3_select$MKT +
                 FF_3_select$SMB +
                 FF_3_select$HML)
coeftest(model_SMB, vcov = vcovHC(model_SMB))

# VMG versus FF3
model_VMG = lm(CH_3_select$VMG~FF_3_select$MKT +
                 FF_3_select$SMB +
                 FF_3_select$HML)
coeftest(model_VMG, vcov = vcovHC(model_VMG))

#GRS test 1, use FF3 to explain CH3
mat_CH3 = CH_3_select[,c( "SMB", "VMG")]
mat_FF3 = FF_3_select[,c( "SMB", "HML")]
GRS.test(mat_CH3, mat_FF3)$GRS.stat
GRS.test(mat_CH3, mat_FF3)$GRS.pval

# GRS test 2, use CH3 to explain FF3
GRS.test(mat_FF3, mat_CH3)$GRS.stat
GRS.test(mat_FF3, mat_CH3)$GRS.pval