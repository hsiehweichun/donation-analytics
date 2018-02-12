import pandas as pd
import numpy as np
import sys

#f = open('../insight_testsuite/tests/test_1/input/itcont.txt','r')
#input file
f = open(sys.argv[1],'r')
#percentile input file
f_percentile = open(sys.argv[2],'r')
#output file
ofile = open(sys.argv[3],'w')

for line in f_percentile.readlines():
    percentile_input = int(line.strip())/100.
print("Percentile =",percentile_input)

def find_percentile(N, P):
    """
    Find the percentile of a list of values

    N - A list of values.  N must be sorted.
    P - A float value from 0.0 to 1.0

    return - The percentile of the value.
    """
    n = int(round(P * len(N) + 0.5))
    return N[n-1]

lines = f.readlines()
num_lines = len(lines)

#Find repeated donor
donors = {}
for i in range(num_lines):
    line = lines[i]
    row = line.split('|')
    name = row[7]
    zip_code =  row[10][:5]
    other_id = row[15]
    name_zip_code = name + zip_code
#Consider individual donor only
    if other_id == '': 
        counts = donors.get(name_zip_code,0)
        donors[name_zip_code] = counts + 1

repeated_donor = [k for k,v in donors.items() if v > 1]
print("Repeated donors: {0}".format("| ".join(str(donor) for donor in repeated_donor)))

#Extract records for repeated donors and save in the dataframe df_donation_output
donation_output = []
for i in range(num_lines):
    line = lines[i]
    row = line.split('|')

    cmte_id = row[0]
    name = row[7]
    zip_code =  row[10][:5]
    trans_dt = row[13]
    year = trans_dt[-4:]
    trans_amt = row[14]
    other_id = row[15]
    name_zip_code = name + zip_code
    if other_id == '' and name_zip_code in repeated_donor :
        donation_output.append([cmte_id,name_zip_code,year,trans_dt,trans_amt])

df_donation_output = pd.DataFrame.from_records(donation_output, columns=['CMTE_ID','Name_Zip_Code','Year','Trans_Dt','Trans_Amt'])

#Find the current year
current_year = max(df_donation_output['Year'])

#Filter data in the current year
df_donation_output_current = df_donation_output[df_donation_output['Year']==current_year]

#Create a dictionary where key is recipient of the contribution, and value saves the list of contribution amount from its donors 
cmte_dict = {}
for index, row in df_donation_output_current.iterrows():
    cmte = row['CMTE_ID']
    amt = row['Trans_Amt']
    zip = row['Name_Zip_Code'][-5:]
    year = row['Year']
    cmte_dict[cmte] = cmte_dict.get(cmte,[])
    cmte_dict[cmte] = cmte_dict[cmte]+[int(amt)]

    #Data for each CMTE record in the form of list
    cmte_records = cmte_dict[cmte]

    output_data = [cmte,zip,year,sum(cmte_records),find_percentile(sorted(cmte_records), percentile_input),len(cmte_records)]
    ofile.write("|".join(map(str, output_data))+"\n")

