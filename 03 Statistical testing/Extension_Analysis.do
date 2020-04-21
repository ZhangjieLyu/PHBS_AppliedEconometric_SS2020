
/// With filler
import delimited C:\Users\augus\Desktop\data_rollingReg_drop30.csv
edit
reg mreturn mkt smb vmg
/// Chnge the name of monthyReturn variable to mreturn
reg mreturn mkt smb vmg rmw cma 

predict resid, residuals
sktest resid
estat hettest 
estat ovtest 
margin, at(rmw= (0.1 0.2 0.3 0.4 0.5))
marginsplot
margin, at(cma= (0.1 0.2 0.3 0.4 0.5))
predict r, resid

reg mreturn mkt smb vmg rmw cma 
predict r, resid
swilk r
outreg2 using test.doc, replace
edit
/// Without filler
import delimited C:\Users\augus\Desktop\data_rollingReg_nonDrop30.csv
reg mreturn mkt smb vmg rmw cma 
