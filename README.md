# Umass-Senior-Project-2019
The purpose of my application was to solve a problem many businesses (small businesses in particular) face. 
They do not know how much to produce, where to price, how much to spend on advertising and many other questions. 
Eden’s purpose was to answer these questions for them easily and with no technical acumen required by the user, just inputting company data.  
Eden would model supply and demand equations using ordinary least squares (OLS) regression on the user’s data to form the best fitting supply and demand equations possible. 
The best fit was to be ensured by regressing each variable against demand or supply, determine the best shape via the highest adjusted R2, and then do an OLS regression and simplistically tell the user what the results mean. 
Eden would attempt multiple shapes like linear, logarithmic, cubic, quadratic, and inverse. 
It performs checks for violations of regression assumptions, autocorrelation and heteroskedasticity, and uses a modified version of OLS in these cases.
In addition, to predict future sales it tries some time series forecasting techniques, the Holt-Winters method and Vector Autoregression (VAR) in addition to the previously estimated model and selects the model with the lowest root mean squared error.
It includes a section for personal finance questions as well as investment decisions.
