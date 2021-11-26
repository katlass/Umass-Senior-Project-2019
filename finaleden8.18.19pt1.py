#import required packages

import pandas as pd
import numpy as np
import scipy
import statsmodels.api as sm
import datetime
import statsmodels.formula.api as smf
import operator
import itertools
from scipy.stats import chi2
#df_adv = pd.read_csv("EdensSKLEARNY.csv")
#df_adv = pd.read_csv("EdenCategorical.csv")
#df_adv = pd.read_csv("Eden2Categorical.csv")
df_adv = pd.read_csv("Eden2CategoricalTest.csv")
#df_adv = pd.read_csv("EdenTesting.csv")
#df_adv = pd.read_csv("FinalRun.csv")
#df_adv = pd.read_csv("Finals.csv")
#df_adv = pd.read_csv("Finals1.csv")
#df_adv = pd.read_csv("moretest.csv")
#df_adv = pd.read_csv("gettingmad.csv")
#df_adv = pd.read_csv("mess.csv")
#df_adv = pd.read_csv("last.csv")
#df_adv = pd.read_csv("withdist.csv")
CurrentDate = datetime.datetime.now()
CurrentYear=CurrentDate.year
SeasonDictionary={'Monthly': 12, 'Quarterly': 4, 'Yearly':1}
MonthList=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
QuarterList=['1','2','3','4']
AllBinaryList=["January","February","March","April","May","June","July","August","September","October","November","December","Quarter 1","Quarter 2","Quarter 3","Quarter 4"]
SeasonalWords={'Quarterly':'Quarter','Monthly':'Month'}
MonthDictionary={1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
QuarterDictionary={1:"Quarter 1",2:"Quarter 2",3:"Quarter 3",4:"Quarter 4"}

#Need to work on what to do if users enter a categorical variable or a non int/float like $,
#Need to make a test set for accurateness, but don't know how to generate a disturbance
#norm.inv , rand()


#Finding the target dependent variable
def FindingDependent():
    ListVariables=[]
    Counter=1
    AskUserTarget=input("What is the variable name you are trying to predict? ")
    while AskUserTarget not in list(df_adv):
        print("You made a typo")
        AskUserTarget=input("What is the variable name you are trying to predict? ")
    return AskUserTarget


#Making sure they enter a correct start year
def GettingStartYear():
    AskUserStartYear=input("What year does your data start? ")
    while True:
        if 1900<int(AskUserStartYear)<=CurrentYear:
            break
        else:
            print("That year is either too long ago or hasn't happened yet, try again!")
            AskUserStartYear=input("What year does your data start? ")
    return AskUserStartYear


#taking out their time variables
def TakingOutTime(): 
    TimeVariablesList=[]
    NumberTimeVariables=input("How many time variables to you have recorded in your data?")
    #protecting from them taking out all variables other than dependant
    while int(NumberTimeVariables)>(len(list(df_adv))-1):
        print("You entered more variables than you have!")
        NumberTimeVariables=input("How many time variables to you have recorded in your data?")
    #actually removing time variables
    for X in range(int(NumberTimeVariables)):
        AskUserTimeVariablesToDrop=input("Do you currently have any time information in your dataset?")
        #protecting them from entering a variable not in their dataset
        while AskUserTimeVariablesToDrop not in list(df_adv):
            print("That variable does not exist in your dataset.You have made a typo, try again!")
            AskUserTimeVariablesToDrop=input("Do you currently have any time information in your dataset?")
        else:
            TimeVariablesList=TimeVariablesList+[AskUserTimeVariablesToDrop]
    return TimeVariablesList



#Adding Time to capture Trend
#Generates a time series of 1....the total number of rows they have in their dataset
def AddingTrendVariable():
    Time=0
    TimeList=[]
    for X in range(len(df_adv)):
        Time=Time+1
        TimeList=TimeList+[Time]
    #adds this column to their dataset
    df_adv['Time']=TimeList



#Making Categorical Variables Binary

def CategoricalBinary(AskUserVariable,CategoricalVariable):
    Stopper=0
    CategoricalList=[]
    #For each unique value in the categorical variable
    for X in CategoricalVariable:
        #Added a stopper so we avoid the dummy variable trap
        if Stopper==0:
            Stopper=1
        else:
            #creating a column in the dataframe that has the same values as the categorical variable
            df_adv[X]=df_adv[AskUserVariable]
            #if it is equal to that unqiue value in the column, it is equal to 1 in the new column created for that unique value
            df_adv.loc[df_adv[AskUserVariable] == X, X] = 1
            #if it is not equal to that unqiue value in the column, it is equal to 0 in the new column created for that unique value
            df_adv.loc[df_adv[AskUserVariable] != X, X] = 0
            #Creating a list of the actually created dummy variables, again to avoid the dummy variable trap (m-1)
            CategoricalList=CategoricalList+[X]
    return CategoricalList
            
def Categorical():
    CategoricalLists=[]
    #Find out if the user has any variables with letters instead of numeric values
    AskUserCat=input("Do you have any variables that are described by words and not numbers (i.e Quality is Low, Medium, High)? Y/N ")
    print(df_adv.head())
    TextVariables=[]
    if AskUserCat=="Y":
        AskUserNumber=input("How many word variables do you have? ")
        for X in range(int(AskUserNumber)):
            AskUserVariable=input("Which variable? ")
            #Making sure they list a variable actually in their data
            while AskUserVariable not in list(df_adv):
                print("That variable is not in the data you gave me")
                AskUserVariable=input("Which variable? ")
            TextVariables=TextVariables+[AskUserVariable]
            #Finding the unique values in the variable (ex. High, Medium, Low)
            CategoricalVariable=df_adv[AskUserVariable].unique()
            #Creating unique binary variables for each possible value of that text column
            CategoricalList=CategoricalBinary(AskUserVariable,CategoricalVariable)
            #Creating a list of the actually created dummy variables for each entered categorical variable, again to avoid the dummy variable trap (m-1)
            CategoricalLists=CategoricalLists+CategoricalList
            #Deleteing the old column containing text values
            del df_adv[AskUserVariable]
    return CategoricalLists,TextVariables


#Addressing misbehaving datatypes like %,$,commas, etc

#Finding the misbehavior
def DataMisbehavior():
    Index=0
    print(df_adv.dtypes)
    Columns=list(df_adv)
    Misbehavior=[]
    for X in df_adv.dtypes:
        if X!='int64' and X!='float64':
            Variable=Columns[Index]
            Misbehavior=Misbehavior+[Variable]
            print("I have detected that "+str(Variable)+" is not a numeric variable, i.e it contains letters, dollar signs, commas, percentages, etc.")
        Index=Index+1
    print(Misbehavior)
    return Misbehavior
    





def ReplaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the strings to be replaced
    for elem in toBeReplaces :
        print(elem)
        # Check if string is in the main string
        if elem in mainString["Price"] :
            # Replace the string
            mainString = mainString.replace(elem, newString)
            print(mainString)
    return  mainString


#def MyReplacer(df,ListBadValues,Replacement):
   # for i in ListBadValues:
      #  if Value in df:
        #   True= df.str.replace('$','')





#Fixing it
def FixingBehavior(Misbehavior):
    CategoricalLists=Categorical()
    TextVariables=CategoricalLists[1]
    BadCharacters=['$',',']
    for X in Misbehavior:
        #print(X)
        if X not in TextVariables:
            print(X)
            for i in BadCharacters:
                X=df_adv[str(X)].str.replace(i,'')
                print(X)
            #Variable=str(X)
            #df_adv[X].astype('int64')
            #Der=ReplaceMultiple(df_adv, ['$',','], '')
           # print(Der)
            #print([df_adv[str(X)])
            print(df_adv['Price'].isin(['$']))
            #if df_adv[str(X)].str.replace('$','')
          #  except:
             #   X=df_adv[str(X)].str.replace(',','')
           # print(X)
            #for X in 
            #df_adv.Price=[x[1:] for x in df_adv.Price]
            #print(df_adv.Price)
            #print(df_adv['Price'])
           # print (X)



    #AskUser=input("Do you h
    #ser.astype('int64')
    


#Isolating the explanatory variables before Binary. To avoid specification bias, i.e that some important variable will be left out and its correlation to another variable will magnify the importance of another variable, I have chosen to not give the user an option to omit variables in their file. All financial information is likely related to the target variable, and it does not hurt to add the variable so long as it is accounted for later i.e a penalty for additional variables
def ExplanatoryWithoutBinary(AskUserTarget,TimeVariablesList):
    ListBeforeVariables=[]
    for X in list(df_adv):
        if X!=AskUserTarget and X not in TimeVariablesList:
            ListBeforeVariables=ListBeforeVariables+[X]
    return ListBeforeVariables
        


#Adding Dummy Variables for Seasonality
#Counter=0
def DummyGenerator(N,Period):
    Counter=0
    NewValues=[]
    #adding the cushion of zeros before and after the start time indicated by a 1
    while Counter<SeasonDictionary[Period]:
        Before=int(N)-1
        After=SeasonDictionary[Period]-int(N)
        listofzerosbefore = [0] * int(Before)
        listofzerosafter = [0] * int(After)
        AdditionalPadding=listofzerosbefore+[1]+listofzerosafter
        Counter=Counter+1
    Cutoff=int(N)-1
    #the binary variable starts in the first month entered by user
    Starter=AdditionalPadding[Cutoff:]
    Length=int(len(df_adv)/SeasonDictionary[Period])
    LengthTrue=len(df_adv)
    #this means they have less that a single year of data
    if Length<1:
        print("You need more data, sorry! I only work well if you have at least 1 year or more worth of data")
    #this means the length of the data is the an exact calender year
    if Length==1:
        AdditionalPadding=AdditionalPadding
    #this means addtional padding must be added to replicate pattern of binary variables for other years
    elif Length>=2:
        #deals with monthly/quarterly lengths
        if int(N)<9:
            for X in range(Length):
                if X==0: #this means it is the starting string for the data i.e starts in period 2 so 100 
                    NewValues=NewValues+Starter
                else: #this means that after the first starter it adds padding accordingly so after 100 - 0100 -0100
                    NewValues=NewValues+AdditionalPadding
        else:
             for X in range(Length+1):
                if X==0: #when its greater than 9 the start legth gets funny so needed this block to accomdate 
                    NewValues=NewValues+Starter
                else:
                    NewValues=NewValues+AdditionalPadding   
        LeftOver=LengthTrue-len(NewValues)
        FullString=AdditionalPadding[:LeftOver]
        AdditionalPadding=NewValues+FullString
    return(N,AdditionalPadding)


#so, the dummy generator will start with the period you entered and the last period will be the intercept
#Also getting a list of dummies DummyNames[] for the model builder later 

def CreatingDummies(N,Period):
    DummyNames=[]
    #comes from DummyGenerator (N,Period)
    InitialSequence=DummyGenerator(N,Period)
    #this is grabbing the additonal binary padding sequence from Dummy Generator
    ModifiedSequence=InitialSequence[1]
    #Number of dummy variables is always seasonal periods-1
    DummyLength=SeasonDictionary[Period]-1
    for X in range(DummyLength):
        if X==0: #this generates a column in your data of binary variables for the first period you entered
            #if the Period is Monthly, it picks names for the binary variables from the MonthDictionary
            if SeasonalWords[Period]=="Month":
                NamingDumbies=str(MonthDictionary[int(N)])
                #NamingDumbies="Dummy"+str(SeasonalWords[Period])+str(N)
                DummyNames=DummyNames+[NamingDumbies]
                df_adv[NamingDumbies]=ModifiedSequence
                N=int(N)+1
            else:
                NamingDumbies=str(QuarterDictionary[int(N)])
                DummyNames=DummyNames+[NamingDumbies]
                df_adv[NamingDumbies]=ModifiedSequence
                N=int(N)+1
        else: #this creates different name columns for the different binary variables for different periods
            if SeasonalWords[Period]=="Month":
                if N<=12:
                    NamingDumbies=str(MonthDictionary[int(N)])
                    DummyNames=DummyNames+[NamingDumbies]
                    ModifiedLength=len(ModifiedSequence)-1
                    ModifiedSequence=[0]+ModifiedSequence[:ModifiedLength]
                    df_adv[NamingDumbies]=ModifiedSequence
                    N=int(N)+1
                else:
                    N=1
                    NamingDumbies=str(MonthDictionary[int(N)])
                    DummyNames=DummyNames+[NamingDumbies]
                    ModifiedLength=len(ModifiedSequence)-1
                    ModifiedSequence=[0]+ModifiedSequence[:ModifiedLength]
                    df_adv[NamingDumbies]=ModifiedSequence
                    N=int(N)+1
            else:
                if N<=4:
                    NamingDumbies=str(QuarterDictionary[int(N)])
                    DummyNames=DummyNames+[NamingDumbies]
                    ModifiedLength=len(ModifiedSequence)-1
                    ModifiedSequence=[0]+ModifiedSequence[:ModifiedLength]
                    df_adv[NamingDumbies]=ModifiedSequence
                    N=int(N)+1
                else:
                    N=1
                    NamingDumbies=str(QuarterDictionary[int(N)])
                    DummyNames=DummyNames+[NamingDumbies]
                    ModifiedLength=len(ModifiedSequence)-1
                    ModifiedSequence=[0]+ModifiedSequence[:ModifiedLength]
                    df_adv[NamingDumbies]=ModifiedSequence
                    N=int(N)+1
    return(DummyNames)





def Seasonality():
    #Highlighting Seasonality
    AskUserSeason=input("How often is your data collected? Monthly/Quarterly/Yearly? " )
    #Protecting them from entering a season Eden doesn't account for
    while AskUserSeason not in SeasonDictionary:
        print("You made a typo")
        AskUserSeason=input("How often is your data collected? Monthly/Quarterly/Yearly?" )
    #Finding out what month/quarter they started collecting their data in for dummy variables
    #Chose not to include Yearly because it won't matter for seasonality
    #---------------------------------
    #Monthly
    if AskUserSeason=='Monthly':
        AskUserStartDate=input("What month did you start collecting your data? For example, if it was the first month of the year January, enter 1. If it was the last month of the year, December, enter 12")
        #protecting them from entering a number that is for monthly 0 or >12
        while AskUserStartDate not in MonthList:
            print ("You have made an error")
            AskUserStartDate=input("What month did you start collecting your data? For example, if it was the first month of the year January, enter 1. If it was the last month of the year, December, enter 12" )
        #actually generating the dummy variables for their dataset correctly
        DummyVariables=CreatingDummies(AskUserStartDate,'Monthly')
    #---------------------------------
    #Quarterly
    if AskUserSeason=='Quarterly':
        AskUserStartDate=input("What quarter did you start collecting your data? For example, if it was the first quarter of the year, enter 1. If it was the last quarter, enter 4" )
        #protecting them from entering a number that is for Quarter 0 or >4
        while AskUserStartDate not in QuarterList:
            print ("You have made an error")
            AskUserStartDate=input("What quarter did you start collecting your data? For example, if it was the first quarter of the year, enter 1. If it was the last quarter, enter 4" )
        #actually generating the dummy variables for their dataset correctly
        DummyVariables=CreatingDummies(AskUserStartDate,'Quarterly')
    #---------------------------------
    #Yearly
    #For model builder ensuring no dummies are added for yearly
    if AskUserSeason=='Yearly':
        DummyVariables=[]
    return DummyVariables

#Isolating the explanatory variables including binary. To avoid specification bias, i.e that some important variable will be left out and its correlation to another variable will magnify the importance of another variable, I have chosen to not give the user an option to omit variables in their file. All financial information is likely related to the target variable, and it does not hurt to add the variable so long as it is accounted for later i.e a penalty for additional variables
def ExplanatoryWithBinary(AskUserTarget,TimeVariablesList):
    ListVariables=[]
    for X in list(df_adv):
        if X!=AskUserTarget and X not in TimeVariablesList:
            ListVariables=ListVariables+[X]
    return ListVariables


#In the ModelFitter(), the independent variable is regressed against the dependant in various shapes: log, linear, quadratic, cubic, inverse
#The shape yeilding the highest adjusted r^2 is the optimal relationship between the indepedent and the dependent
def ModelFitter(ListBeforeVariables,y):
    #These Lists will contain the various adjusted R^2 for each shape
    ListRSquareLinear=[]
    ListRSquareLog=[]
    ListRSquareQuad=[]
    ListRSquareCub=[]
    ListRSquareInverse=[]
    
    #Types of shape being tested
    Types=['Lin','Log','Quad','Cub','Inv']
    Counter=0
    
    #Creating a Dictionary associating each variable in each shape with the associated adjusted R^2
    Dictionary={}

    #Also generating a list of variables that couldn't be logged i.e contain zeros for later purposes with addressing multicolinearty via log-log or semi-log models
    ListOfVariablesThatContainZeros=[]
    
    for X in ListBeforeVariables:           #For every variable thats not a dummy variable
        X=df_adv[X]                         #Grabbing the independent variable from the dataframe
        X = sm.add_constant(X)              #Adding a constant
        #-------------------------------------------------------------
        #Try Linear
        model = sm.OLS(y, X).fit()
        Dictionary[Types[0]+ListBeforeVariables[Counter]]=model.rsquared_adj   #Now in dictionary is LinIndepentVariable : adjusted R^2
        ListRSquareLinear=ListRSquareLinear+[model.rsquared_adj]               #Adjusted R^2 for each shape now in a list for the linear shape of different variables to find the max in the function below
        #-------------------------------------------------------------
        #try log
        #A try except block is used in case of divide by zero errors in the uploaded sheet
        #Numpy automatically gives error message for zero, I already dealt with this with the try except so I can safely ignore this
        np.seterr(all='ignore')
        try:
            model = smf.ols(formula='y ~ np.log(X)', data=df_adv).fit()
            Dictionary[Types[1]+ListBeforeVariables[Counter]]=model.rsquared_adj
            ListRSquareLog=ListRSquareLog+[model.rsquared_adj]
        except:
            ListOfVariablesThatContainZeros=ListOfVariablesThatContainZeros+[X]
        #-------------------------------------------------------------
        #try parabolic
        model = smf.ols(formula = 'y ~ X + I(X**2)', data = df_adv).fit()
        ListRSquareQuad=ListRSquareQuad+[model.rsquared_adj]
        Dictionary[Types[2]+ListBeforeVariables[Counter]]=model.rsquared_adj
        #-------------------------------------------------------------
        #try cubic
        model = smf.ols(formula = 'y ~ X + I(X**2) + I(X**3)', data = df_adv).fit()
        ListRSquareCub=ListRSquareCub+[model.rsquared_adj]
        Dictionary[Types[3]+ListBeforeVariables[Counter]]=model.rsquared_adj
        #-------------------------------------------------------------
        #try Inverse
        #A try except block is used in case of divide by zero errors in the uploaded sheet
        try:
            model = smf.ols(formula = 'y ~ I(1/X)', data = df_adv).fit()
            ListRSquareInverse=ListRSquareInverse+[model.rsquared_adj]
            Dictionary[Types[4]+ListBeforeVariables[Counter]]=model.rsquared_adj
        except:
            pass
        #try exponential
        # model = sm.OLS(y, X).fit()
        # model=np.exp(model.params*X)
        #ListRSquareExponential=ListRSquareExponential+[model.rsquared]
        Counter=Counter+1
    return Dictionary,ListRSquareLinear,ListRSquareLog,ListRSquareQuad,ListRSquareCub,ListRSquareInverse,ListOfVariablesThatContainZeros


def BestRSquare(ListRSquareLinear,ListRSquareLog,ListRSquareQuad,ListRSquareCub,ListRSquareInverse):
    # Finding the largest adj R^2 for each variable of all the shapes from the lists made in ModelFitter()
    # A try except block is used in case of divide by zero errors in the uploaded sheet means only Lin, Quad, Cub exist
    #-------------------------------------------------------------
    MaxRSquare=[] 
    for X in range(len(ListRSquareLinear)):
        try:  
            MaxRSquare=MaxRSquare+[max(ListRSquareLinear[X],ListRSquareLog[X],ListRSquareQuad[X],ListRSquareCub[X],ListRSquareInverse[X])]
        except:   
            MaxRSquare=MaxRSquare+[max(ListRSquareLinear[X],ListRSquareQuad[X],ListRSquareCub[X])]
    return MaxRSquare

#It is a list of the best shapes selected from BestRSquare() and linked to the shape in the Dictionary in AssociatingShapeAndRSquare()
def AssociatingShapeAndRSquare(MaxRSquare,Dictionary):
    #Finding Keys (shapes) in your Dictionary for the highest R^2 values in MaxRSquare
    print("Your Best Shapes Are:")
    BestShapes=[]
    for X in MaxRSquare:
        print(list(Dictionary.keys())[list(Dictionary.values()).index(X)])
        BestShapes=BestShapes+[list(Dictionary.keys())[list(Dictionary.values()).index(X)]]
    return BestShapes




def SMFAssembler(BestShapes,ListBeforeVariables):
    #assembling the statement to go into the smf.ols regression 
    TotalFormula=str()
    Counter=0
    ListForGLS=[]
    for X in BestShapes:                                        #Best shapes looks like this ex. ['InvPrice', 'LinAdvetisement', 'CubRelated_Price', 'CubTime']
        if X=='Lin'+str(ListBeforeVariables[Counter]):          #If its linear in shape
            Formula=str(ListBeforeVariables[Counter])           #Formula is just the variable because no transformation needed for linear regression
            if Counter==0:                                      #If it is the first Variable added to the formula, no "+" is needed between variables smf.ols("y ~ X + 
                TotalFormula=TotalFormula+Formula        
            else:
                TotalFormula=TotalFormula+'+'+Formula
            df_adv[str(X)]=df_adv[str(ListBeforeVariables[Counter])]    #Creating a column in the dataframe that is LinXvariable transformed to the correct linear shape
            ListForGLS=ListForGLS+[str(X)]                              #This is done so if GLS must be done, the column tranformed like that exists because there is only sm.GLS not smf.GLS
            #print(df_adv[str(X)])                                      #It is then added to a list for the above described procedure
        if X=='Quad'+str(ListBeforeVariables[Counter]):                                                #If its quadratic in shape
            Formula=str(ListBeforeVariables[Counter])+' + I('+str(ListBeforeVariables[Counter])+'**2) ' #Formula is the variable and the variable squared for OLS regression
            if Counter==0:                                                                             #If it is the first Variable added to the formula, no "+" is needed between variables smf.ols("y ~ X + 
                TotalFormula=TotalFormula+Formula
            else:
                TotalFormula=TotalFormula+'+'+Formula
            ListForGLS=ListForGLS+[str(ListBeforeVariables[Counter])]       #Variable name is then added to a list so if GLS must be done, the column is included because there is only sm.GLS not smf.GLS
            df_adv[str(X)]=df_adv[str(ListBeforeVariables[Counter])]**2  #Creating a column in the dataframe that is just the Xvariable transformed by squaring it so it can be used for GLS regression
            ListForGLS=ListForGLS+[str(X)]                                #Still want to include just the variable not trasnformed in the list for GLS 
            #print(df_adv[str(X)])
        if X=='Cub'+str(ListBeforeVariables[Counter]):                  #If its cubic in shape
            Formula=str(ListBeforeVariables[Counter])+' + I('+str(ListBeforeVariables[Counter])+'**2) + I('+str(ListBeforeVariables[Counter])+'**3)' #Formula is the variable, the variable squared, and the variable cubed for OLS regression
            if Counter==0:                                              #If it is the first Variable added to the formula, no "+" is needed between variables smf.ols("y ~ X +
                TotalFormula=TotalFormula+Formula
            else:
                TotalFormula=TotalFormula+'+'+Formula
            ListForGLS=ListForGLS+[str(ListBeforeVariables[Counter])]    #Variable name is then added to a list so if GLS must be done, the column is included because there is only sm.GLS not smf.GLS
            df_adv["Quad"+str(ListBeforeVariables[Counter])]=df_adv[str(ListBeforeVariables[Counter])]**2   #Creating a column in the dataframe that is just the Xvariable transformed by squaring it so it can be used for GLS regression
            #print(df_adv["Quad"+str(ListBeforeVariables[Counter])])
            ListForGLS=ListForGLS+["Quad"+str(ListBeforeVariables[Counter])]                                #It is then added to a list for the above described procedure
            df_adv[str(X)]=df_adv[str(ListBeforeVariables[Counter])]**3    #Creating a column in the dataframe that is just the Xvariable transformed by cubing it so it can be used for GLS regression
            #print((df_adv[str(X)]))
            ListForGLS=ListForGLS+[str(X)]                                  #Still want to include just the variable not trasnformed in the list for GLS 
        if X=='Log'+str(ListBeforeVariables[Counter]):                      #If its logarithmic in shape
            Formula='np.log('+str(ListBeforeVariables[Counter])+')'         #Formula is the variable logged for OLS regression
            if Counter==0:                                                  #If it is the first Variable added to the formula, no "+" is needed between variables smf.ols("y ~ X +
                TotalFormula=TotalFormula+Formula
            else:
                TotalFormula=TotalFormula+'+'+Formula
            df_adv[str(X)]=np.log(df_adv[str(ListBeforeVariables[Counter])])#Creating a column in the dataframe that is just the Xvariable transformed by logging it so it can be used for GLS regression
            #print((df_adv[str(X)]))
            ListForGLS=ListForGLS+[str(X)]                                  #It is then added to a list for the above described procedure                                
        if X=='Inv'+str(ListBeforeVariables[Counter]):                      #If its inverse in shape
            Formula='I(1/'+str(ListBeforeVariables[Counter])+')'            #Formula is the 1/variable for OLS regression
            if Counter==0:                                                  #If it is the first Variable added to the formula, no "+" is needed between variables smf.ols("y ~ X +
                TotalFormula=TotalFormula+Formula
            else:
                TotalFormula=TotalFormula+'+'+Formula
            df_adv[str(X)]=1/(df_adv[str(ListBeforeVariables[Counter])])    #Creating a column in the dataframe that is just the Xvariable transformed by taking its inverse so it can be used for GLS regression
            #print((df_adv[str(X)]))
            ListForGLS=ListForGLS+[str(X)]                                  #It is then added to a list for the above described procedure
        Counter=Counter+1                           #Counter brings us through all the independent variables excluding the dummy variables
    return TotalFormula,ListForGLS






def DummyBuilder(DummyVariables,TotalFormula):
#adding dummy variables to equation
    for X in DummyVariables:
        TotalFormula=TotalFormula+"+"+str(X)
    return TotalFormula





#Getting interactioon Terms for Whites Test
def IsolatingMostBasicRelationship(ListForGLS,ListBeforeVariables):
    TermsToInteract=[]
    for X in ListForGLS:
        ActualWord=X[3:]
        if ActualWord in ListBeforeVariables and X[:3] != 'Cub':
           TermsToInteract=TermsToInteract+[X]
        if X in ListBeforeVariables:
            TermsToInteract=TermsToInteract+[X]
    return TermsToInteract


def GeneratingInteractions(TermsToInteract):
    Interactions=list(itertools.combinations(TermsToInteract, 2))
    ListOfInteractionTerms=[]
    for X in Interactions:
        TupleToList=list(X)
        Interaction=TupleToList[0]+TupleToList[1]
        ListOfInteractionTerms=ListOfInteractionTerms+[Interaction]
        df_adv[Interaction]=df_adv[X[0]]*df_adv[X[1]]
    return ListOfInteractionTerms

def BinaryInteractions(TermsToInteract,DummyVariables):
    ListOfBinaryInteractions=[]
    for Term in TermsToInteract:
        for Month in DummyVariables:
            Interaction=Term+Month
            ListOfBinaryInteractions=ListOfBinaryInteractions+[Interaction]
            df_adv[Interaction]=df_adv[Term]*df_adv[Month]
    return ListOfBinaryInteractions


def IsolatingSignificantVariables(GLSAllVariables,AskUserConfidence,PValueDictionary,LevelOfSignificance):
    SignificantVariables=[]
    for X in GLSAllVariables:
       # print(X)
        if (float(PValueDictionary[X])/2.0)<=LevelOfSignificance[AskUserConfidence]:
            SignificantVariables=SignificantVariables+[X]
            #print(str(X)+" is signifant")
    return SignificantVariables




def Loggable(ListOfVariablesThatContainZeros):
    LogModel="Yes"
    if len(ListOfVariablesThatContainZeros)>0:
        LogModel="No"
        print("Can't deal with multicolinearity by log log model")
    return LogModel




#-------------------------------------------------------------------------------------------------
#Creating the Chi Square Test
def ChiSquaredCritical(p,df):
    ChiSquaredCritical = chi2.ppf(p, df)
    #print(ChiSquaredCritical)
    #print(value)
    # confirm with cdf (Chi-Squared Percent Point Function)
    #p = chi2.cdf(value, df)
    #print(p)
    return ChiSquaredCritical
    
def HypothesisTest(Crit,Calc):
    if Crit>=0:
        if Calc>Crit:
            Result="Reject Null"
        else:
            Result="FTR"
    else:
        if Calc<Crit:
            Result="Reject Null"
        else:
            Result="FTR"
    return Result

def ChiSquaredCalc(RSquare,n):
    ChiSquaredCalc=RSquare*n
    #print(ChiSquaredCalc)
    return ChiSquaredCalc


#-------------------------------------------------------------------------------------------------
#Performing Whites Test For Heteroskedactitcy
#include the sqaures?

def WhitesTest(Residuals,n,p,df,y,GLSAllVariables,model,AllInteractionList,TrueVariables):
    #e^2=a1+a2X2+a3X is an auxillary regression of the models variables agaianst the models errors square
    ResidualsSquared=Residuals**2
    #model = smf.ols(formula='ResidualsSquared ~ '+str(TotalFormula), data=df_adv).fit()
    #auxillary regressions r^2
    #print("***********************")
    #print("In order to do a White's Test, we need all the interaction terms to be included, So I've done just that!")
    #print("The goal is to examine the R^2, multiply by N and then run a Chi Test")
    X=df_adv[GLSAllVariables]
    X = sm.add_constant(X)
    model = sm.OLS(ResidualsSquared,X).fit()
    #print(model.summary())
    #results = model
    #model=sm.OLS(ResidualsSquared,GLSAllVariables)
    RSquare=model.rsquared
    #chi calc calculated as auxillary r^2 * number observations
    ChiCalc=ChiSquaredCalc(RSquare,n)
    #chi critcal comes from the chi table based on degrees of freedom which is number of explanatory variables except intercept and probability user selected
    ChiCritical=ChiSquaredCritical(p,df)
    #hypothesis test to see if chi crit < chi calc, thus there would be heteroskedacity
    Test=HypothesisTest(ChiCritical,ChiCalc)
    #You can decide for hetero if auxillary regression chi hypothesis test fails
    #what R squared is high????
    if Test=="Reject Null":
        print("You have Heteroskedactitcy")
        #NewResults=ModifiedGeneralizedLeastSquares(Residuals,Actual,Lagged,ListForGLS,y,X)
        NewResults=ModifiedGeneralizedLeastSquares(y,TrueVariables)
        model=NewResults
    else:
        print("You don't have heteroskedacticity")
        model=model
    return model


#The GLS procedure
def ModifiedGeneralizedLeastSquares(y,TrueVariables):
    #-------------------------------------------------------------------------------------------------
   #Assigning the tranformed independent variables as the indepedent variables in the GLS model
    X=df_adv[TrueVariables]
    X = sm.add_constant(X)
   #This is my GLSAR model
    glsar_model = sm.GLSAR(y, X, 1)
    #olsmodel=sm.OLS(y,X)
    #results = olsmodel.fit()
    #print(results.summary())
    #glsar_results = glsar_model.iterative_fit(1)
    model=glsar_model.iterative_fit(1)
    #Pvalues=model.pvalues
    #print(Pvalues)
    #Parameters=model.params
    #CoefficientDictionary=dict(model.params)
    #print(CoefficientDictionary)
    #print("hdfgergeggrege")
    #PValueDictionary=dict(model.pvalues)

    #print(glsar_results.summary())
    #---------
    #print(model.summary())
    #----------
    #what values would be indicative of needing an AR process?
    return model




def BreuschGodfreyTest(model,LevelOfSignificance,AskUserConfidence,y,TrueVariables,nlags=3,store=False):
    BreuschGodfrey=sm.stats.diagnostic.acorr_breusch_godfrey(model, nlags, store)
    BGTestStat=BreuschGodfrey[0]
    BGPValue=BreuschGodfrey[1]
    Results=HypothesisTest(LevelOfSignificance[AskUserConfidence],BGPValue)
    if Results == "Reject Null":
        #print(Results)
        print("You have autocorrelation")
        model=ModifiedGeneralizedLeastSquares(y,TrueVariables)
    else:
        model=model
    return model


#------------------------------------------------------
#interpretations
def Significance(SignificantVariables,CoefficientDictionary,AskUserTarget,UserInquiry=1):
    ActualWords=[]
    for X in SignificantVariables:
        if X not in AllBinaryList:
            Message="one unit"
            Effect=0
            if X[:3]=='Cub':
                PartialEffects=[]
                ActualWord=X[3:]
                ActualWords=ActualWords+[ActualWord]
                PartialEffects=PartialEffects+[CoefficientDictionary[ActualWord]]
                PartialEffects=PartialEffects+[CoefficientDictionary['Quad'+str(ActualWord)]]
                PartialEffects=PartialEffects+[CoefficientDictionary['Cub'+str(ActualWord)]]
                Effect=PartialEffects[0]+(2.0*PartialEffects[1]*UserInquiry)+(3.0*PartialEffects[2]*(UserInquiry**2))
            elif X[:3]=="Lin":
                ActualWord=X[3:]
                ActualWords=ActualWords+[ActualWord]
                Effect=CoefficientDictionary[str(X)]*UserInquiry
            elif X[:3]=="Inv":
                ActualWord=X[3:]
                ActualWords=ActualWords+[ActualWord]
                PartialEffect=-CoefficientDictionary[str(X)]*float(1/UserInquiry**2)
                Effect=CoefficientDictionary[str(X)]
            elif X[:3]=="Log":
                #need to see how to log out quantity
                ActualWord=X[3:]
                ActualWords=ActualWords+[ActualWord]
                Effect=CoefficientDictionary[str(X)]
                #Ask dan
                #Effect=(100.0*Effect)
                Effect=(100.0*Effect*UserInquiry)
                Message="1%"
            elif X[:3]=="Qua":
                PartialEffects=[]
                ActualWord=X[4:]
                ActualWords=ActualWords+[ActualWord]
                if 'Cub'+str(ActualWord) not in SignificantVariables:
                    PartialEffects=PartialEffects+[CoefficientDictionary[ActualWord]]
                    PartialEffects=PartialEffects+[CoefficientDictionary['Quad'+str(ActualWord)]]
                    Effect=PartialEffects[0]+(2.0*PartialEffects[1]*UserInquiry)
                else:
                    pass
            if Effect>0 and UserInquiry==1:
                print("A "+str(Message)+" increase in "+str(ActualWord)+" results in a "+str(round(Effect,2))+ " unit increase in "+str(AskUserTarget))
            elif Effect<0 and UserInquiry==1:
                print("A "+str(Message)+" increase in "+str(ActualWord)+" results in a "+str(round(Effect,2))+ " unit decrease in "+str(AskUserTarget))
            if Effect>0 and UserInquiry!=1:
                print("If you use "+str(UserInquiry)+" units of "+str(ActualWord)+", this results in a "+str(round(Effect,2))+ " unit increase in "+str(AskUserTarget))
            elif Effect<0 and UserInquiry!=1:
                print("If you use "+str(UserInquiry)+" units of "+str(ActualWord)+", this results in a "+str(round(Effect,2))+ " unit decrease in "+str(AskUserTarget))
    else:
        pass
    return ActualWords



def BinarySignificance(SignificantVariables,AskUserTarget,CoefficientDictionary):
    for X in AllBinaryList:     # AllBinaryList=["January","February","March","April","May","June","July","August","September","October","November","December","Quarter 1","Quarter 2","Quarter 3","Quarter 4"]                       
        if X in SignificantVariables:   #If eden has found them to be significant at the user selected confidence it is in a List i.e [June,July,December]
            Effect=CoefficientDictionary[X]     #There is a dictionary of the variables names and their coefficents (i.e {linadvertisement:5690, June:771,etc}) 
            if Effect>0:                #If its a positive change, use the word "increase"
                print("When it is "+str(X)+" there is a "+str(round(Effect,2))+ " unit increase in "+str(AskUserTarget))
            else:                       #If its a negative change, use the word "decrease"
                print("When it is "+str(X)+" there is a "+str(round(Effect,2))+ " unit decrease in "+str(AskUserTarget))



#------------------------------------------------------------
#Now we want the user to be able to play around with varying the amount of inputs, cause the could incorrectly surmise a constant rate of growth if they had,
#say a cubic variable a 2 unit increae is not the same as 2 1unit increase
#ask dan to check my partial effects :)
def VaryingInputs(AskUserVaryingInputs,ActualWords,ListForGLS,AskUserConfidence,CoefficientDictionary,AskUserTarget):
    if AskUserVaryingInputs=="Y":   #If the user says yes I'd like to vary inputs, then 
        AskUserHowManyVariables=int(input("How many variables are you looking to calculate?"))
        while AskUserHowManyVariables>len(ActualWords): #making sure they are only asking about the max number of variables significant at their selected level of confidence
            print("The maximum number of variable you can explore is "+str(len(ActualWords))+" because this is the number of varibles I can predict with "+str(AskUserConfidence)+"% confidence ")
            AskUserHowManyVariables=int(input("How many variables are you looking to calculate?"))
        for X in range(AskUserHowManyVariables):
            print("Please enter one of the following")
            print(str(ActualWords))     #Showing them their signigficnat variables
            AskUserVariable=input("Which Variable ")
            while AskUserVariable not in ActualWords:   #making sure they are only asking about variables significant at their selected level of confidence
                print("This variable is not statistically significant at the "+str(AskUserConfidence)+"% level.")
                print("Please enter one of the following")
                print(str(ActualWords))
                AskUserVariable=input("Which Variable? ")
            else:
                AskUserValueOfX=int(input("How many units of "+str(AskUserVariable)+" where you planning on utilizing? "))  #Ask them what number they are testing i.e 50 units of advertising
                #They are telling us the actual variable name, i.e advetisement
                #We need to know what shape Eden picked for that variable so
                #We get back the shape from out ListForGLS which contains [linadvertisement,cubrelatedprice,quadrelatedprice,logsubstitue,etc]
                for X in ListForGLS:
                    if AskUserVariable==X[4:]:                          #if the letters after the first 4 are the variable name the user is asking about, we know there is a Quadratic relationship (i.e QuadPrice)
                        #However, there could aslo be a cubic term!
                        if "Cub"+str(AskUserVariable) not in ListForGLS:
                            #if there is not also a cubic term in the ListForGLS, then there must be only a quadratic, not cubic relationship
                            #i.e cubPrice and quadPrice could both be in ListForGLS, in which case we want it to run through the procedure for cubic not quadratic in Significance(AskUserVariable,AskUserValueOfX)
                            #Because cubPrice not in ListGLS, we know there is only a quadratic term.
                            AskUserVariable=[X]
                            #Now AskUserVariable is equal to i.e QuadPrice instead of just the user entered Price, thus we know the relationship
                            print(AskUserVariable)
                        else:
                            #if there is also a cubic term in the ListForGLS, then there must not only be a quadratic, but also a cubic relationship
                            #i.e cubPrice and quadPrice could both be in ListForGLS, in which case we want it to run through the procedure for cubic not quadratic in Significance(AskUserVariable,AskUserValueOfX)
                            #Because cubPrice is in ListGLS, we know there is a quadratic and cubic term.
                            AskUserVariable=["Cub"+AskUserVariable]
                            #Artificially forcing it to use cubic instead of the quadratic
                            print(AskUserVariable)
                    elif AskUserVariable==X[3:]:
                        #All the other relationships start with 3 letters, i.e invPrice, logPrice, cubPrice, linPrice
                       AskUserVariable=[X]
                #print(AskUserVariable)
                #print(AskUserValueOfX)
                #Now we are running the significance function to get a feel for how the partial effects are different with different units of inputs
                Significance(AskUserVariable,CoefficientDictionary,AskUserTarget,UserInquiry=AskUserValueOfX)
                #Significance(SignificantVariables,UserInquiry=1)




#-----------------------------------------------------
#Need to log out depend variable
#Need to deal with if they have categorical variables or binary variables
def Main():
    print("Hello beloved user, today we are going to understand how to predict our future sales, and likewise what factors affect them and what can be done to manipulate these sales.")
    print("Sounds cool, right? Now all I need is for you to tell me what variable you are looking to predict. I've taken the liberty to tell you what your choices are based on the file you uploaded. Please type the variable below.")
    print(list(df_adv))
    AskUserTarget=FindingDependent()
    AskUserStartYear=GettingStartYear()
    TimeVariablesList=TakingOutTime()
    Misbehavior=DataMisbehavior()
    FixingBehavior(Misbehavior)
    AddingTrendVariable()
    #Categorical()
    ListBeforeVariables=ExplanatoryWithoutBinary(AskUserTarget,TimeVariablesList)
    DummyVariables=Seasonality()
    #print(DummyVariables)
    #This is what the dataframe we will be analyzing looks like
    #print (df_adv)
    ListVariables=ExplanatoryWithBinary(AskUserTarget,TimeVariablesList)
    #Naming target and explanatory variables X and y
    X = df_adv[ListVariables]
    y = df_adv[AskUserTarget]
    #Adding a constant
    #X = sm.add_constant(X)
    BestFit=ModelFitter(ListBeforeVariables,y)
    Dictionary=BestFit[0]                       #XShapeXVariable: AdjR^2 for ex. {LinPrice : .81,CubPrice : .12,....QuadAdvertisement : .21, LinAdvertisement : .91...}
    ListRSquareLinear=BestFit[1]                #List of adj r^2 for linear fit for each independent variable against the dependent for ex. [.12,.23,.66,.78.....]
    ListRSquareLog=BestFit[2]                   #List of adj r^2 for log fit for each independent variable against the dependent for ex. [.12,.23,.66,.78.....]
    ListRSquareQuad=BestFit[3]                  #List of adj r^2 for quadratic fit for each independent variable against the dependent for ex. [.12,.23,.66,.78.....]
    ListRSquareCub=BestFit[4]                   #List of adj r^2 for cubic fit for each independent variable against the dependent for ex. [.12,.23,.66,.78.....]
    ListRSquareInverse=BestFit[5]               #List of adj r^2 for inverse (1/X) fit for each independent variable against the dependent for ex. [.12,.23,.66,.78.....]
    ListOfVariablesThatContainZeros=BestFit[6]  #All variables that had to be handled by the except in log because they have a zero somewhere
    MaxRSquare=BestRSquare(ListRSquareLinear,ListRSquareLog,ListRSquareQuad,ListRSquareCub,ListRSquareInverse)  #Returns a single list of the highest adj r^2 for each variable in the model
    BestShapes=AssociatingShapeAndRSquare(MaxRSquare,Dictionary) #Best shapes looks like this ex. ['InvPrice', 'LinAdvetisement', 'CubRelated_Price', 'CubTime']
    FormulaBuilder=SMFAssembler(BestShapes,ListBeforeVariables)
    TotalFormula=FormulaBuilder[0]
    ListForGLS=FormulaBuilder[1]
    #print(ListForGLS)
    print("Your regression equation looks like this")
    TotalFormula=DummyBuilder(DummyVariables,TotalFormula)
    print(TotalFormula)
    #ListDummies=ListDum(ListVariables,ListBeforeVariables)
    #print(ListDummies)
    TermsToInteractWithTime=IsolatingMostBasicRelationship(ListForGLS,ListBeforeVariables)
    TermsToInteract=[X for X in TermsToInteractWithTime if "Time" not in X]
    #might have to come back to because cubtime/quadtime
    ListOfBinaryInteractions=BinaryInteractions(TermsToInteract,DummyVariables)   
    ListOfInteractionTerms=GeneratingInteractions(TermsToInteract)
    #-------------------------------------------------------------------------------------------------
    #Confidence
    AskUserConfidence=input("How confident do you want to be in my estimates? Enter 50, 80, 90, 92, 95, 98, 99: ")
    LevelOfSignificance={'50':0.50,'80':0.20,'90':0.10,'92':0.08,'95':0.05,'98':0.02,'99':0.01}
    LevelOfConfidence={'50':0.50,'80':0.80,'90':0.90,'92':0.92,'95':0.95,'98':0.98,'99':0.99}
    #-------------------------------------------------------------------------------------------------
    GLSAllVariables=ListForGLS+DummyVariables+ListOfInteractionTerms+ListOfBinaryInteractions
    AllInteractionList=ListOfInteractionTerms+ListOfBinaryInteractions
    ActualVariables=ListForGLS+DummyVariables
    #This is your standard OLS with every possible interaction term and real variables
    X=df_adv[GLSAllVariables]
    X = sm.add_constant(X)
    model = sm.OLS(y,X).fit()
    #print(model.summary())
    #-------------------------------------------------------------------------------------------------
    #Cutting out insignificant interaction terms
    Pvalues=model.pvalues
    Parameters=model.params
    CoefficientDictionary=dict(model.params)
    PValueDictionary=dict(model.pvalues)
    SignificantInteractionVariables=IsolatingSignificantVariables(AllInteractionList,AskUserConfidence,PValueDictionary,LevelOfSignificance)
    #Interpetation of this is not nailed down, this is what would happen if it was:
    
    #RealVariablesAndInteractions=ActualVariables+SignificantInteractionVariables
    #X=df_adv[RealVariablesAndInteractions]
    #X = sm.add_constant(X)
    #model = sm.OLS(y,X).fit()
    
    #might not need
    #SignificantVariables=IsolatingSignificantVariables(RealVariablesAndInteractions,AskUserConfidence)
    
    #TrueVariables=ListForGLS+ListDummies+SignificantInteractionVariables
    
    #might not need
    #SignificantVariables=IsolatingSignificantVariables(ActualVariables,AskUserConfidence,PValueDictionary,LevelOfSignificance)
    #print("6666666")
    #print(SignificantVariables)
    TrueVariables=ListForGLS+DummyVariables
    X=df_adv[TrueVariables]
    X = sm.add_constant(X)
    model = sm.OLS(y,X).fit()
    #print(model.summary())
    #----------------------------------------------------------------------------------------
    #What it all means
    Pvalues=model.pvalues
    Parameters=model.params
    CoefficientDictionary=dict(model.params)
    PValueDictionary=dict(model.pvalues)
    #----------------------------------------------------------------------------------------
    #Multicolinearity
    LogModel=Loggable(ListOfVariablesThatContainZeros)
    
    # define probability
    p = LevelOfConfidence[AskUserConfidence]
    df=model.df_model
    #Number of observations
    n=len(df_adv)
    #Getting residuals of model
    Residuals=model.resid
    #Doing a White's General Heteroscedasticity Test
    model=WhitesTest(Residuals,n,p,df,y,GLSAllVariables,model,AllInteractionList,TrueVariables)
    #----------------------------------------------------------------------------------------
    #Autocorrelation
    model=BreuschGodfreyTest(model,LevelOfSignificance,AskUserConfidence,y,TrueVariables,nlags=3,store=False)
    #----------------------------------------------------------------------------------------
    #Interpretation of finalized model
    Pvalues=model.pvalues
    Parameters=model.params
    CoefficientDictionary=dict(model.params)
    PValueDictionary=dict(model.pvalues)
    print(model.summary())
    SignificantVariables=IsolatingSignificantVariables(TrueVariables,AskUserConfidence,PValueDictionary,LevelOfSignificance)
    print("*************")
    print("These variables are statistically significant")
    print(SignificantVariables)
    ActualWordsWithDuplicates=Significance(SignificantVariables,CoefficientDictionary,AskUserTarget)
    #taking out Duplicates
    ActualWords = list(set(ActualWordsWithDuplicates))
    BinarySignificance(SignificantVariables,AskUserTarget,CoefficientDictionary)
    #Starting a loop for user to play with varyig the levels of inputs
    AskUserVaryingInputs=input("Are you interested finding what your demand will increase by if you increase a variable by more than one unit? Y/N ")
    while AskUserVaryingInputs=="Y":
        VaryingInputs(AskUserVaryingInputs,ActualWords,ListForGLS,AskUserConfidence,CoefficientDictionary,AskUserTarget)
        AskUserVaryingInputs=input("Are you interested finding what your demand will increase by if you increase a variable by more than one unit? Y/N ")

    
#Ask Dr.Bill about lambda
#Dan just emailed me literature on BoxCox, need to do this before can be sure to log dependent
#struggling to get max and min, should i used eigenvalues?
#
Main()


#######
#Holt-Winters
print('Now Lets Try Holt-Winters')
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from random import random
# Target Data
data = df_adv[AskUserTarget]

# fit model with different types of Winters
def FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend,seasonal,seasonal_periods,TestType):
    np.seterr(all='ignore')
    #they said this would fix RuntimeWarning: overflow encountered in multiply
    #RuntimeWarning: overflow encountered in double_scalars
    #I take this to mean we will lose some precision at the e308+ level which i'm okay with
    model = ExponentialSmoothing(endog=data,trend=trend,seasonal=seasonal,seasonal_periods=seasonal_periods)
    model_fit = model.fit()
    #-------------------------------------------------------
    # make prediction for entire set: ex. within-index = 0...127 post-index=128...159
    yhats= model_fit.predict(0,DataIndexLength)
    # compare post sample predictions and actual
    PostSampleActual=data.iloc[LengthWithin:TotalLength]
    PostSamplePredictions=yhats.iloc[LengthWithin:TotalLength]
    #-------------------------------------------------------
    #Finding Error
    WINTERSRMSE=math.sqrt(mean_squared_error(PostSamplePredictions, PostSampleActual))
    return(WINTERSRMSE,TestType)

DataIndexLength=len(data)-1
data = df_adv[AskUserTarget]
LengthWithin=len(train)
TotalLength=len(data)
seasonal_periods=SeasonDictionary[AskUserSeason]

#if AskUserTarget=ListOfVariablesThatContainZeros:
   # pass

#This is because if it is yearly there is no seasonality
if AskUserSeason=='Yearly':
    Result4=FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="additive",seasonal="none",seasonal_periods=seasonal_periods,TestType="Winter's Additive Trend")
    Result5=FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="multiplicative",seasonal="none",seasonal_periods=seasonal_periods,TestType="Winter's Multiplicative Trend")

else:
    Result1=FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="additive",seasonal="additive",seasonal_periods=seasonal_periods,TestType="Winter's Additive Trend and Additive Seasonal")
    Result2=FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="additive",seasonal="multiplicative",seasonal_periods=seasonal_periods,TestType="Winter's Additive Trend and Multiplicative Seasonal")
#FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="multiplicative",seasonal="multiplicative",seasonal_periods=seasonal_periods)
#This one is like nahhhhh, got to look into it
    Result3=FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="multiplicative",seasonal="additive",seasonal_periods=seasonal_periods,TestType="Winter's Multiplicative Trend and Additive Seasonal")

#Using Nones
#FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="none",seasonal="add",seasonal_periods=seasonal_periods)
#FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="none",seasonal="multiplicative",seasonal_periods=seasonal_periods)
#I think these can't happen
    Result4=FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="additive",seasonal="none",seasonal_periods=seasonal_periods,TestType="Winter's Additive Trend")
    Result5=FittingWinters(TotalLength,LengthWithin,DataIndexLength,data,trend="multiplicative",seasonal="none",seasonal_periods=seasonal_periods,TestType="Winter's Multiplicative Trend")

try:
    BESTWINTERSRMSE=min(Result1[0],Result2[0],Result3[0],Result4[0],Result5[0])
except:
    BESTWINTERSRMSE=min(Result4[0],Result5[0])


#need to figure out how to resturn best name type
print(BESTWINTERSRMSE)



#BestChecker(BESTWINTERSRMSE,VARRMSE,"Holt-Winters","Vector Autoregression")
BestChecker(BESTWINTERSRMSE,RMSEOLS,"Holt-Winters","Ordinary Least Squares Regression")







#----------------------------------------------------------------------------------------
#Starting off with OLS regression

#Splitting it into Pre and Post Sample
def TestTrain(ListVariables,AskUserTarget): 
    #Getting within-sample observations
    train = df_adv[:int(0.8*(len(df_adv[ListVariables])))]
    #Post-sample observations
    valid = df_adv[int(0.8*(len(df_adv[AskUserTarget]))):]
    #Identifying Post Sample Target Information
    YPostSample=valid[AskUserTarget]



#print(ListForGLS)
print("*********")






#-------------------------------------------------------------------------------------------------
#Running the best fit regression

#model = smf.ols(formula='y ~ '+str(TotalFormula), data=df_adv).fit()

#print(model.summary())

#print(model.params)












#print(model.params)





#print(Parameters)













#results = model
#print("******************")
#print("Seeing as how most of these interaction terms will be irrelavent, I will only include those statistically significant at your desired level of confidence")
#print("I am programmed to be able to do this but KATE doesn't like the way I interperet parameters with an inverse")
#print("She is going to ask Dan about it and then adjust")
#print("These would be included")
#print(SignificantInteractionVariables)
#print("***************")











# Make predictions by the model
AllPredictions = model.predict() 
PostPredictions=AllPredictions[int(0.8*(len(df_adv[AskUserTarget]))):]  #Break out the post sample for fit evaluation
print (PostPredictions)


from statsmodels.tools.eval_measures import rmse

#Calculating Root Mean Squared Error, the meaure of choice in comparing the fit of models
RMSEOLS = rmse(YPostSample, PostPredictions)
print("The root mean square error for Ordinary Least Squares regression is "+str(RMSEOLS))
#need to go back and check this with SAS


#deal with multicollinearity, would like to lag :)

#want to add log transformations, so perhaps we should to MAPE


#-------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------
#Handling Problems with OLS Assumptions 1-6

#-------------------------------------------------------------------------------------------------
#Dealing with multicolinearity
#Definition: The presence of linear association among independent variables – i.e. linear association or correlation between X1 and X2
#SampleProblem– the problem lies in your sample data
#There is no causal relationship between X2 and the other independent variables.
# Consequences:
#OLS estimators–remain unbiased.(BLUE!)
#Standard errors are inflated.
#Calculated t-statistics are deflated.
#Increase prob of type 2 error aka fail to reject false null aka say a signifant variable not significant

#xxs = np.random.randn(100, 5)      # independent variables
#corr = np.corrcoef(ListVariables, rowvar=0)  # correlation matrix
#w,v = np.linalg.eig(corr)        # eigen values & eigen vectors

#print(w,v)






#-------------------------------------------------------------------------------------------------
#Random Regressor
#The problem – independent variable is really a random variable – violates CRMA#2.
#Endogenous variable – another dependent variable
#Measurement error – X is measured with error
#TheXvariablenowhasadisturbanceanditwillbe related to part of the new composite disturbance (ε):
#cov(X,E) no longer zero
#OLSisbiasedandinconsistent(the bias will not disappear as n increases)–degreedependson the amount of measurement error
#statsmodels.sandbox.regression.gmm.GMM
#import statsmodels.sandbox.regression.gmm.GMM



#-------------------------------------------------------------------------------------------------
#Dealing with heteroskedacity
#Definition: One of our CRM assumptions is violated. The disturbances do not have constant variances.
#Homoskedastic Disturbances (CRMA #4): Var(ui) = E[ui2] = sigma^2
#Heteroskedastic Disturbances: Var(ui) = E[ui2] = sigmai^2
#OLS uses the wrong formula – OLS results would give you the “wrong standard errors”


#Bruesch‐Pagan Test

#for X in ListBeforeVariables:
    #print(df_adv[X])
    #print(Residuals)
    #BrueschPaganTest=sm.stats.diagnostic.het_breuschpagan(resid=Residuals, exog_het=df_adv[X])
    #BrueschPaganTest=sm.stats.diagnostic.het_breuschpagan(model.resid, model.model.exog)
    #print(BrueschPaganTest)

#print(model.model.exog)
#BrueschPaganTest=sm.stats.diagnostic.het_breuschpagan(model.resid, model.model.exog)
#print(BrueschPaganTest)

#If the regression fails both the Whites Test and The Chi Test, we will modify for hetero






#-------------------------------------------------------------------------------------------------
#Creating the solution to heteroskedacity, FGLS:
#Doing generalized least squares instead of feasable least squares becaue statsmodels doesnt have it.
#Of course, the exact rho in this instance is not known so it it might make more sense to use feasible gls, which currently only has experimental support.
#We can use the GLSAR model with one lag, to get to a similar result:

#the resdiduals of the model we estimated earlier        
Residuals=model.resid

#Had to make lists because the indeces were not aligned when the following was done:
#Actual=residual[:(n-1)]
#Lagged=resdidual[1:]
#df_adv["LaggedError"]=Residuals[:-1]
#print(df_adv["LaggedError"])
#df_adv["Error"]=Residuals[1:]
#print(df_adv["Error"])

Counter=0
Actual=[]
Lagged=[]
for X in Residuals:
    if Counter!=0:
        Lagged=Lagged+[X]
    Actual=Actual+[X]
    Counter=Counter+1
    
Actual=Actual[1:]     
#Would like to fix this so not so slow with list iteration if data set was big


#Getting Dummies and adding them to the GLS variables. I needed to do this because there is no statsmodelformula (SMF) for GLS
#ListDummies=[]
#for X in ListVariables:
   # if X not in ListBeforeVariables:
      #  ListDummies=ListDummies+[X]

#print(ListDummies)
#GLSAllVariables=ListForGLS+ListDummies
#print("########")
#print(GLSAllVariables)


#X=df_adv[GLSAllVariables]
#X = sm.add_constant(X)
#olsmodel=sm.OLS(y,X)
#results = olsmodel.fit()
#print(results.summary())


from scipy.linalg import toeplitz







#The GLS procedure
def ModifiedGeneralizedLeastSquaresNotDone(Residuals,Actual,Lagged,ListForGLS,y,GLSAllVariables,ActualVariables,TrueVariables):
    #-------------------------------------------------------------------------------------------------
    #This is the GLS model. It does not work for some reason because it hates me. Error is: Sigma must be a scalar, 1d of length 160 or a 2d array of shape 160 x 160
    #Need to ask dan if GLSAR can be safely used in its place (the internet says so but who knows)
    #rho is simply the correlation of the residual a consistent estimator for rho is to regress the residuals on the lagged residuals
    
    #resid_fit = sm.OLS(Lagged, sm.add_constant(Actual)).fit()
    #print(resid_fit.tvalues[1])
    #print(resid_fit.pvalues[1])
    #rho = resid_fit.params[1]
    #order = toeplitz(range(len(Actual)))
   # sigma = rho**order
    #gls_model = sm.GLS(y, X, sigma=sigma)
   #-------------------------------------------------------------------------------------------------
   #Assigning the tranformed independent variables as the indepedent variables in the GLS model
    X=df_adv[TrueVariables]
    X = sm.add_constant(X)
   #This is my GLSAR model
    glsar_model = sm.GLSAR(y, X, 1)
    #olsmodel=sm.OLS(y,X)
    #results = olsmodel.fit()
    #print(results.summary())
    #glsar_results = glsar_model.iterative_fit(1)
    model=glsar_model.iterative_fit(1)
    #print(glsar_results.summary())
    print("**************")
    print("An OLS assumption is violated so I am running GLSAR")
    print(model.summary())
    #what values would be indicative of needing an AR process?
    return model









#print(GLSAllVariables)
#print("#####90")
#print(X)


#Calling the function
#Der=ModifiedGeneralizedLeastSquares(Residuals,Actual,Lagged,ListForGLS,y,X)



#-------------------------------------------------------------------------------------------------

#Statsmodels has a chai square test but I couldn't get it to work correctly so I made my own

#Yhats=model.fittedvalues
#not sure if this is right
#import scipy as sp
#def ChiSquaredTest(y,Yhats):
  #  ChiTest=sp.stats.chisquare(y, f_exp=Yhats)#, ddof=0, axis=0)
  #  print(ChiTest)
  #  return (ChiTest)

#ChiTest=ChiSquaredTest(y,Yhats)
#ChiCalc=ChiTest[0]
#PValue=ChiTest[1]
#print (ChiCalc,PValue)












#Critical values for durbin watson not availble in python (maybe I should make a module with it?)
#Performing Durbin Watson Test for Autocorrelation
#def DurbinWatson(Residuals):
    #dCalc=sm.stats.stattools.durbin_watson(Residuals)
    
#Instead we will
#do statsmodels.stats.diagnostic.acorr_ljungbox(x, lags=None, boxpierce=False
#Ljung-Box test for no autocorrelation

#Dum=sm.stats.diagnostic.acorr_ljungbox(Residuals, lags=None, boxpierce=False)
#print(Dum[0])
#Need to do more research before I use this
   #   lbvalue (float or array) – test statistic
#pvalue (float or array) – p-value based on chi-square distribution
#bpvalue ((optional), float or array) – test statistic for Box-Pierce test
#bppvalue ((optional), float or array) – p-value based for Box-Pierce test on chi-square distribution)

FittedValues=model.fittedvalues



#se, anova
#glsar
#pvale dw

#-------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------
#What it all means
#print(model.summary())
Pvalues=model.pvalues
#print(Pvalues)
Parameters=model.params

CoefficientDictionary=dict(model.params)
#print(CoefficientDictionary)

#ActualParameters=[]
#for X in ListVariables:
  #  if X in GLSAllVariables:
 #       ActualParameters=ActualParameters+[CoefficientDictionary[X]]
        #print(CoefficientDictionary[X])
    #elif 'I(1 / '+str(X)+')' in CoefficientDictionary:
       # ActualParameters=ActualParameters+[CoefficientDictionary['I(1 / '+str(X)+')']]
        #print(CoefficientDictionary['I(1 / '+str(X)+')'])

#Parameters=[]
#for X in ActualParameters:
 #   Parameters=Parameters+[list(CoefficientDictionary.keys())[list(CoefficientDictionary.values()).index(X)]]

#print(Parameters)
PValueDictionary=dict(model.pvalues)
#print(PValueDictionary)



#------------------------------------------------------
#interpretations
def Significance(SignificantVariables,UserInquiry=1):
    ActualWords=[]
    for X in SignificantVariables:
        Message="one unit"
        Effect=0
        if X[:3]=='Cub':
            PartialEffects=[]
            ActualWord=X[3:]
            ActualWords=ActualWords+[ActualWord]
            PartialEffects=PartialEffects+[CoefficientDictionary[ActualWord]]
            PartialEffects=PartialEffects+[CoefficientDictionary['Quad'+str(ActualWord)]]
            PartialEffects=PartialEffects+[CoefficientDictionary['Cub'+str(ActualWord)]]
            Effect=PartialEffects[0]+(2.0*PartialEffects[1]*UserInquiry)+(3.0*PartialEffects[2]*(UserInquiry**2))
        elif X[:3]=="Lin":
            ActualWord=X[3:]
            ActualWords=ActualWords+[ActualWord]
            Effect=CoefficientDictionary[str(X)]*UserInquiry
        elif X[:3]=="Inv":
            ActualWord=X[3:]
            ActualWords=ActualWords+[ActualWord]
            PartialEffect=-CoefficientDictionary[str(X)]*float(1/UserInquiry**2)
            Effect=CoefficientDictionary[str(X)]
        elif X[:3]=="Log":
            #need to see how to log out quantity
            ActualWord=X[3:]
            ActualWords=ActualWords+[ActualWord]
            Effect=CoefficientDictionary[str(X)]
            #Ask dan
            #Effect=(100.0*Effect)
            Effect=(100.0*Effect*UserInquiry)
            Message="1%"
        elif X[:3]=="Qua":
            PartialEffects=[]
            ActualWord=X[4:]
            ActualWords=ActualWords+[ActualWord]
            if 'Cub'+str(ActualWord) not in SignificantVariables:
                PartialEffects=PartialEffects+[CoefficientDictionary[ActualWord]]
                PartialEffects=PartialEffects+[CoefficientDictionary['Quad'+str(ActualWord)]]
                Effect=PartialEffects[0]+(2.0*PartialEffects[1]*UserInquiry)
            else:
                pass
        if Effect>0 and UserInquiry==1:
            print("A "+str(Message)+" increase in "+str(ActualWord)+" results in a "+str(round(Effect,2))+ " unit increase in "+str(AskUserTarget))
        elif Effect<0 and UserInquiry==1:
            print("A "+str(Message)+" increase in "+str(ActualWord)+" results in a "+str(round(Effect,2))+ " unit decrease in "+str(AskUserTarget))
        if Effect>0 and UserInquiry!=1:
            print("If you use "+str(UserInquiry)+" units of "+str(ActualWord)+", this results in a "+str(round(Effect,2))+ " unit increase in "+str(AskUserTarget))
        elif Effect<0 and UserInquiry!=1:
            print("If you use "+str(UserInquiry)+" units of "+str(ActualWord)+", this results in a "+str(round(Effect,2))+ " unit decrease in "+str(AskUserTarget))
    return ActualWords

ActualWordsWithDuplicates=Significance(SignificantVariables)
ActualWords = list(set(ActualWordsWithDuplicates))
#------------------------------------------------------------

#Finding Optimality









#box cox test
                




        
       # print(X)
                
                #    NamingDumbies=str(MonthDictionary[int(N)])

#for X in SignificantVariables:
    #if X[:3]=="New" or X[:5]=="Dummy":
#need to do it for dummy variables



print('#####')





#-------------------------------------------------------------------------------------------------
#Moving into VAR
print("Now we are moving onto Vector Autogression with X many lags")
import matplotlib.pyplot as plt
import sklearn
import math

#Want to do something like check if they have Time, Year, Month, Etc and drop them

#check the dtypes
print(df_adv.dtypes)

#Making Your Date so its user friendly
DateDictionary={'Monthly':'m','Quarterly':'q',"Yearly":'a'}

if AskUserSeason=='Yearly':
    DateFormat=str(AskUserStartYear)
else:
    DateFormat=str(AskUserStartYear)+str(DateDictionary[AskUserSeason])+str(AskUserStartDate)

from datetime import datetime
dates = sm.tsa.datetools.dates_from_range(DateFormat, length=len(df_adv[AskUserTarget]))


#checking stationarity
#In the Johansen test, we check whether lambda has a zero eigenvalue. When all the eigenvalues are zero, that would mean
#that the series are not cointegrated, whereas when some of the eigenvalues contain negative values,
#it would imply that a linear combination of the time series can be created, which would result in stationarity.
from statsmodels.tsa.vector_ar.vecm import coint_johansen
#since the test works for only 12 variables, I have randomly dropped
#in the next iteration, I would drop another and check the eigenvalues
#johan_test_temp = data.drop([ 'CO(GT)'], axis=1)

#StationarityTest=coint_johansen(df_adv,-1,1).eig
StationarityTest=coint_johansen(df_adv[ListBeforeVariables],-1,1).eig
print(StationarityTest)

def IsStationary(StationarityTest):
    ListZeros=[]
    for X in StationarityTest:
        if X==0:
            ListZeros=ListZeros+[0]
        else:
            ListZeros=ListZeros
    if ListZeros==len(StationarityTest):
        print("When all the eigenvalues are zero, that would mean that the series are not cointegrated!")
    for X in StationarityTest:
        if X<0:
            print("A linear combination of the time series can be created, which would result in stationarity")        
    else:
        print("No Stationarity Problems")

IsStationary(StationarityTest)



#creating the train and validation set
train = df_adv[:int(0.8*(len(df_adv)))]
valid = df_adv[int(0.8*(len(df_adv))):]
print(valid)

#shaio

#fit the model
from statsmodels.tsa.vector_ar.var_model import VAR

model = VAR(endog=train,dates=dates,freq=DateDictionary[AskUserSeason])
model_fit = model.fit()

# make prediction on validation
prediction = model_fit.forecast(model_fit.y, steps=len(valid))

#Converting predictions to a dataframe
cols = df_adv.columns
pred = pd.DataFrame(index=range(0,len(prediction)),columns=[cols])
for j in range(0,len(cols)):
    for i in range(0, len(prediction)):
       pred.iloc[i][j] = prediction[i][j]
print(pred)

#check rmse
from sklearn.metrics import mean_squared_error
for i in cols:
    if i==AskUserTarget:
        VARRMSE=math.sqrt(mean_squared_error(pred[i], valid[i]))
        print('rmse value for', i, 'is : ', math.sqrt(mean_squared_error(pred[i], valid[i])))    
#Creating a way to compare error terms for forecasts
def BestChecker(NewRMSE,OldRMSE,NewName,OldName):
    if NewRMSE<OldRMSE:
        BEST=NewRMSE
        BESTNAME=NewName
    else:
        BEST=OldRMSE
        BESTNAME=OldName
    print("The best so far is "+str(BESTNAME))
    return(BEST,BESTNAME)

BestChecker(VARRMSE,RMSEOLS,"Vector Autoregression","Ordinary Least Squares Regression")


#need to modify coht johnas for 12
#need to modify dummies for 52
#need to make sure the VAR is correct 

#print(BESTNAME)

#Moving Average
# VARMA example
from statsmodels.tsa.statespace.varmax import VARMAX
from random import random
# contrived dataset with dependency
#data = list()

# fit model, want to do varma

#model = VARMAX(endog=train,order=(1,1))
#model_fit = model.fit(disp=False)
# make prediction
#yhat = model_fit.forecast()
#print(yhat)




#ask bernie about multiplicative, multiplicative
#ask when to use dampened
#ask if there is some test for seaosnality or trend in and of themseleves
#ask about the different vars
#so if i get a more precise prediciton for forecasting, how could i then extend the forecasting technique to account for if we, say, increased advertising next month
#if a log transform is best for ols will this mean it is best for VAR as well and for holtwinters


#need to do the different shapes tomorrow for OLS
#Need to work on this 
#RMSELASTICNET = rmse(y, y_pred_enet)
#print("The root mean square error for Elastic Net is "+str(RMSELASTICNET))


#if BEST<RMSELASTICNET:
  #  print("So far your best model is "+str(BESTNAME))
#else:
 #   BEST=RMSELASTICNET
  #  BESTNAME="Elastic Net"
  #  print("So far your best model is Elastic Net")


#need to still do ridge regression, HuberRegressor,LassoLars,PassiveAggressiveRegressor








