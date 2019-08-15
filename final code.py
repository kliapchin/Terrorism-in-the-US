import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 

df = pd.read_csv("C:\\Users\\sbortnem\\Desktop\\Summer 2019\\APAN 5210 - Python\\Final Project\\gtd\\globalterrorism.csv", encoding='ISO-8859-1',
                 usecols = [0,1,2,3,7,8,11,12,13,14,18,26,27,28,29,30,31,34,35,36,37,40,41,58,81,82,83,84,97,98,101],
                low_memory = False)

df = df.rename(
    columns={'eventid':'id', 'iyear':'year', 'imonth':'month', 'iday':'day', 'country':'country_code',
             'country_txt':'country', 'provstate':'state', 'attacktype1':'attack_type_code',
             'attacktype1_txt':'attack_type', 'attacktype2':'attack_type2_code', 'attacktype2_txt':'attack_type2',
             'targtype1':'target_type_code', 'targtype1_txt':'target',
             'targsubtype1' : 'target_subtype_code', 'targsubtype1_txt' : 'target_subtype',
             'natlty1':'nationality_code', 'natlty1_txt':'nationality', 'gname':'group_name',
             'weaptype1':'weapon_code','weaptype1_txt':'weapon', 'weapsubtype1':'weapon_subtype_code',
             'weapsubtype1_txt':'weapon_subtype', 'weapdetail':'weapon_detail',
             'nkill':'fatalities','nwound':'wounded', })

## Subsetting only US data
df = df[df.country == 'United States']
df.country = df.country.astype('category')
country_list = df.country.cat.categories.tolist()
len(country_list)

## Checking for NAs
nnull = df.isnull()
nnull.sum()

## Imputing NAs
#States
df[df.state.isnull()]
df.loc[df['id'] == 199512080005,'state'] = 'New York'
df.loc[df['id'] == 197209280011,'state'] = 'District of Columbia'
df.loc[df['id'] == 201701070015,'state'] = 'Texas'
df.loc[df['id'] == 201702060025,'state'] = 'New Hampshire'

#Longitude, latitude (among other missing values) - 1 affected row
df[df.longitude.isnull()]
df = df.loc[df['id'] != 197601010002] #removing the affected row due to limited data

#Summary
df.summary = df.summary.fillna('No Summary').astype(object)

#Attack type 2 - based on unknown values in existing records
df.attack_type2_code = df.attack_type2_code.fillna(9).astype(int)
df.attack_type2 = df.attack_type2.fillna('Unknown').astype(object)

#Target subtype - based on unknown values in existing records
df.target_subtype_code = df.target_subtype_code.fillna(20).astype(int)
df.target_subtype = df.target_subtype.fillna('Unknown').astype(object)

#Weapon subtype and detail - based on unknown values in existing records
df.weapon_subtype_code = df.weapon_subtype_code.fillna(13).astype(int)
df.weapon_subtype = df.weapon_subtype.fillna('Unknown').astype(object)
df.weapon_detail = df.weapon_detail.fillna('Unknown').astype(object)

#Nationality - creating an "Unknown" value
df.nationality_code = df.nationality_code.fillna(0).astype(int)
df.nationality = df.nationality.fillna('Unknown').astype(object)

#Fatalities
df.fatalities = df.fatalities.fillna(0).astype(int)

#Wounded
df.wounded = df.wounded.fillna(0).astype(int)


#adjusting data types
for col in ['country','state','city','success','suicide','attack_type','attack_type2','target','target_subtype','nationality','group_name','weapon','weapon_subtype','weapon_detail']:
    df[col] = df[col].astype('category')
    
for col in ['attack_type2_code','target_subtype_code', 'nationality_code', 'weapon_subtype_code']:
    df[col] = df[col].astype('int')

## Replacing ambigious values in the day column
df.loc[df['day'] == 0,'day'] = 1

## Combining date columns into one
df['date'] = pd.to_datetime(df[['day', 'month', 'year']])
df.drop(['day','month'], axis=1, inplace=True)


## Checking for duplicates
df = df.sort_values(['fatalities', 'wounded'], ascending = False)

## Removing duplicates
df = df.drop_duplicates(['latitude', 'longitude', 'fatalities', 'date'])

#Number of attacks over time
grouped_year_id = pd.DataFrame(df,columns = ['year','id'])
grouped_year_id = grouped_year_id.groupby(['year']).count()
grouped_year_id = grouped_year_id.rename(columns = {'id':'number_of_attacks'})

plt.figure(figsize=(12, 9))
plt.plot(grouped_year_id)
plt.ylabel('Number of Attacks')
plt.xlabel('Year')

#Number of victims over time
grouped_year_victims = pd.DataFrame(df,columns = ['year','fatalities','wounded'])
grouped_year_victims['victims'] = df.fatalities + df.wounded
grouped_year_victims = grouped_year_victims.groupby(['year']).sum()

plt.figure(figsize=(12, 9))
plt.plot(grouped_year_victims.victims)
plt.ylabel('Number of Victims')
plt.xlabel('Year')

#Analysis of attack types

top_5_attack_types=df[df['attack_type'].isin(df['attack_type'].value_counts()[0:5].index)]
pd.crosstab(top_5_attack_types.year,top_5_attack_types.attack_type).plot()
fig=plt.gcf()
fig.set_size_inches(20,14)
plt.ylabel('Number of attacks')
plt.xlabel('Year')
plt.show()

#Top 10 perpetrator groups
top_10_groups=df[df['group_name'].isin(df['group_name'].value_counts()[0:10].index)]
pd.crosstab(top_10_groups.year,top_10_groups.group_name).plot()
fig=plt.gcf()
fig.set_size_inches(20,14)
plt.show()


#Number of victims for armed assault and facility/infrastructure attacks over time
df2 = df[df.attack_type.isin(['Armed Assault','Facility/Infrastructure Attack'])]

grouped_year_victims2 = pd.DataFrame(df2,columns = ['year','fatalities','wounded'])
grouped_year_victims2['victims'] = df2.fatalities + df2.wounded
grouped_year_victims2.drop(['fatalities', 'wounded'], axis=1, inplace=True)
grouped_year_victims2 = grouped_year_victims2.groupby(['year']).sum()

plt.figure(figsize=(12, 9))
plt.plot(grouped_year_victims2)
plt.ylabel('Number of Victims')
plt.xlabel('Year')


#Top 10 perpetrator groups for armed assault and facility attacks
top_10_groups2=df2[df2['group_name'].isin(df2['group_name'].value_counts()[0:10].index)]
pd.crosstab(top_10_groups2.year,top_10_groups2.group_name).plot()
fig=plt.gcf()
fig.set_size_inches(20,14)
plt.show()


#Top target groups before and after 9/11
df2_before = df2[df2.date < '2001-09-11']
df2_after = df2[df2.date > '2001-09-11']
df2_before['target'].value_counts(normalize=True)[0:10] * 100

#Changes in religious attacks before and after 9/11
total_religious_attacks = df2_after.id[df2_after['target'] == 'Religious Figures/Institutions'].count()
total_attacks = df2_after.id.count()
religious_attacks_after = total_religious_attacks / total_attacks * 100
religious_attacks_after
total_religious_attacks_before = df2_before.id[df2_before['target'] == 'Religious Figures/Institutions'].count()
total_attacks_before = df2_before.id.count()
religious_attacks_before = total_religious_attacks_before / total_attacks_before * 100
religious_attacks_before

religious_attacks_increase = (religious_attacks_after - religious_attacks_before) / religious_attacks_before *100
religious_attacks_increase



###### Detailed analysis of attacks (armed assault, facility attacks) for religious motives
#Before 9/11
#used below to manually see which summaries have 'christian|church' as the victim
christian_before_list = df2_before.summary.str.contains('christian|church',case= False)
christian_before_list.sum()
df2_before[christian_before_list]

christian_before_target = christian_before_list.sum()
christian_before_target -= 13
christian_before_target

christian_before_perp = 8
christian_before_perp

#used below to manually see which summaries have 'jewish|synagogue|jew' as the victim
judaism_before_list = df2_before.summary.str.contains('jewish|synagogue|jew',case= False)
judaism_before_list.sum()

judaism_before_target = judaism_before_list.sum()
judaism_before_target -= 15
judaism_before_target

judaism_before_perp = 14
judaism_before_perp

#used below to manually see which summaries have 'muslim|islam|mosque|arab' as the victim
islam_before_list = df2_before.summary.str.contains('muslim|islam|mosque|arab',case= False)
islam_before_list.sum()

islam_before_target = islam_before_list.sum()
islam_before_target -= 13
islam_before_target

islam_before_perp = 12
islam_before_perp

#used below to manually see which summaries have 'hare krishna|hindu|hindi|buddhist|buddhism' as the victim
hindu_before_list = df2_before.summary.str.contains('hare krishna|hindu|hindi|buddhist|buddhism',case= False)
hindu_before_list.sum()
#df2_before[hindu_before_list].iloc[1].summary
#none have to be removed

hindu_before_target = hindu_before_list.sum()
hindu_before_target

#the result is 0, so do not need to review summaries
sikh_before = df2_before.summary.str.contains('sikh',case= False).sum()


#Percentage Calculations of all Armed Assults and Facility Attacks Before 9/11:
total_before = len(df2_before)
christian_before_target_percentage = christian_before_target / total_before * 100
christian_before_target_percentage
christian_before_perp_percentage = christian_before_perp / total_before * 100
christian_before_perp_percentage
judaism_before_target_percentage = judaism_before_target / total_before * 100
judaism_before_target_percentage
judaism_before_perp_percentage = judaism_before_perp / total_before * 100
judaism_before_perp_percentage
islam_before_target_percentage = islam_before_target / total_before * 100
islam_before_target_percentage
islam_before_perp_percentage = islam_before_perp / total_before * 100
islam_before_perp_percentage
hindu_before_target_percentage = hindu_before_target / total_before * 100
hindu_before_target_percentage

#After 9/11
#used below to manually see which summaries have 'christian|church' as the victim
christian_after_list = df2_after.summary.str.contains('christian|church',case= False)
christian_after_list.sum()
#none with words 'christian|church' related to perpetrators
christian_after_target = christian_after_list.sum()
christian_after_target -= 2
christian_after_target

#used below to manually see which summaries have 'jewish|synagogue|jew' as the victim
judaism_after_list = df2_after.summary.str.contains('jewish|synagogue|jew',case= False)
judaism_after_list.sum()
#none with words'jewish|synagogue|jew' related to perpetrators
judaism_after_target = judaism_after_list.sum()
judaism_after_target


#used below to manually see which summaries have 'muslim|islam|mosque|arab' as the victim
islam_after_list = df2_after.summary.str.contains('muslim|islam|mosque|arab|muhammad|mohammad',case= False)
islam_after_list.sum()
df2_after[islam_after_list].iloc[52].summary

islam_after_target = islam_after_list.sum()
islam_after_target -= 22
islam_after_target

islam_after_perp = 14
islam_after_perp

#used below to manually see which summaries have 'hare krishna|hindu|hindi|buddhist|buddhism' as the victim
hindu_after_list = df2_after.summary.str.contains('hare krishna|hindu|hindi|buddhist|buddhism',case= False)
hindu_after_list.sum()
#all need to be kept for target list
hindu_after_target = hindu_after_list.sum()
hindu_after_target

#used below to manually see which summaries have 'sikh' as the victim
sikh_after_list = df2_after.summary.str.contains('sikh',case= False)
sikh_after_list.sum()
df2_after[sikh_after_list].iloc[1].summary
#all need to be kept for target list
sikh_after_target = sikh_after_list.sum()
sikh_after_target

#Percentage Calculations of all Armed Assults and Facility Attacks After 9/11:
total_after = len(df2_after)

christian_after_target_percentage = christian_after_target / total_after * 100
christian_after_target_percentage

judaism_after_target_percentage = judaism_after_target / total_after * 100
judaism_after_target_percentage

islam_after_target_percentage = islam_after_target / total_after * 100
islam_after_target_percentage

islam_after_perp_percentage = islam_after_perp / total_after * 100
islam_after_perp_percentage

sikh_after_target_percentage = sikh_after_target / total_after * 100
sikh_after_target_percentage


#Percentage Changes
christian_target_percent_change = (christian_after_target_percentage - christian_before_target_percentage) / christian_before_target_percentage * 100
christian_target_percent_change

christian_perp_percent_change = (0 - christian_before_perp_percentage ) / christian_before_perp_percentage *100
christian_perp_percent_change
#we know there are still "christian" perpetrator groups, but they are no longer associated in name with christianity

judaism_target_percent_change = (judaism_after_target_percentage - judaism_before_target_percentage) / judaism_before_target_percentage * 100
judaism_target_percent_change

judaism_perp_percent_change = (0 - judaism_before_perp_percentage)/judaism_before_perp_percentage * 100
judaism_perp_percent_change

islam_target_percent_change = (islam_after_target_percentage - islam_before_target_percentage) / islam_before_target_percentage * 100
islam_target_percent_change

#can't calculate percent Sikh increase because there were 0 records before 9/11



###### Detailed analysis of attacks (armed assault, facility attacks) for racial motives
#Before 9/11
white_before_list = df2_before.summary.str.contains('white|Ku Klux Klan|KKK|white american|neo-nazi|nazi|fascist',case= False)
white_before_list.sum()

#manually went through each summary to determine whether the perpetrator or the victim was associated with the races
white_before_target = white_before_list.sum()
white_before_target -= 42
white_before_target

white_before_perp = 42+1
white_before_perp


arabic_before_list = df2_before.summary.str.contains('arab|islamic|islamic state|iran|iraq|afghanistan|islamophobic|iraqi|arabic',case= False)
arabic_before_list.sum() 

arabic_before_target = arabic_before_list.sum()
arabic_before_target -= 6
arabic_before_target

arabic_before_perp = 0
arabic_before_perp


nativeamerican_before_list = df2_before.summary.str.contains('native american|dakota',case= False)
nativeamerican_before_list.sum()

nativeamerican_before_target = nativeamerican_before_list.sum()
nativeamerican_before_target -= 1
nativeamerican_before_target

nativeamerican_before_perp = 0
nativeamerican_before_perp

asian_before_list = df2_before.summary.str.contains('asia|chinese|vietnam',case= False)
asian_before_list.sum()

asian_before_target = asian_before_list.sum()
asian_before_target

asian_before_perp = 2
asian_before_perp

black_before_list = df2_before.summary.str.contains('black|african american|african-american',case= False)
black_before_list.sum()

black_before_target = black_before_list.sum()
black_before_target -= 49
black_before_target

black_before_perp = 46
black_before_perp


latin_before_list = df2_before.summary.str.contains('latina|latino|latin|hispanic|mexican|mexico|cuba|puerto rico|puerto rican|venezuela',case= False)
latin_before_list.sum()

latin_before_target = latin_before_list.sum()
latin_before_target -= 24
latin_before_target

latin_before_perp = 14
latin_before_perp

#Percentage Calculations of all Armed Assults and Facility Attacks Before 9/11:
white_before_target_percentage = white_before_target / total_before * 100
white_before_target_percentage

white_before_perp_percentage = white_before_perp / total_before * 100
white_before_perp_percentage

arabic_before_target_percentage = arabic_before_target/total_before *100
arabic_before_target_percentage

arabic_before_perp_percentage = arabic_before_perp/total_before *100
arabic_before_perp_percentage

nativeamerican_before_target_percentage = nativeamerican_before_target/total_before *100
nativeamerican_before_target_percentage

nativeamerican_before_perp_percentage = nativeamerican_before_perp/total_before *100
nativeamerican_before_perp_percentage

asian_before_target_percentage = asian_before_target/total_before *100
asian_before_target_percentage

asian_before_perp_percentage = asian_before_perp/total_before *100
asian_before_perp_percentage

black_before_target_percentage = black_before_target / total_before *100
black_before_target_percentage

black_before_perp_percentage = black_before_perp / total_before *100
black_before_perp_percentage

latin_before_target_percentage = latin_before_target / total_before * 100
latin_before_target_percentage

latin_before_perp_percentage = latin_before_perp / total_before * 100
latin_before_perp_percentage

#After 9/11
white_after_list = df2_after.summary.str.contains('white|Ku Klux Klan|KKK|white american|neo-nazi|nazi|fascist',case= False)
white_after_list.sum()

#manually went through each summary to determine whether the perpetrator or the victim was associated with the races
white_after_target = white_after_list.sum()
white_after_target -= 22
white_after_target

white_after_perp = 22+1
white_after_perp

arabic_after_list = df2_after.summary.str.contains('arab|islamic state|islamic|iran|iraq|afghanistan|islamophobic|iraqi|arabic',case= False)
arabic_after_list.sum()

arabic_after_target = arabic_after_list.sum()
arabic_after_target -= 19
arabic_after_target

arabic_after_perp = 11
arabic_after_perp


nativeamerican_after_list = df2_after.summary.str.contains('native american|dakota',case= False)
nativeamerican_after_list.sum()

nativeamerican_after_target = nativeamerican_after_list.sum()
nativeamerican_after_target -= 5
nativeamerican_after_target

nativeamerican_after_perp = 0
nativeamerican_after_perp

asian_after_list = df2_after.summary.str.contains('asia|chinese|vietnam',case= False)
asian_after_list.sum()

asian_after_target = asian_after_list.sum()
asian_after_target

asian_after_perp = 0
asian_after_perp

black_after_list = df2_after.summary.str.contains('black|african american|african-american',case= False)
black_after_list.sum()
df2_after[black_after_list].iloc[19].summary

black_after_target = black_after_list.sum()
black_after_target -= 9
black_after_target

black_after_perp = 6
black_after_perp

latin_after_list = df2_after.summary.str.contains('latina|latino|latin|hispanic|mexican|mexico|cuba|puerto rico|puerto rican|venezuela',case= False)
latin_after_list.sum()
df2_after[latin_after_list].iloc[9].summary

latin_after_target = latin_after_list.sum()
latin_after_target -= 7
latin_after_target

latin_after_perp = 1
latin_after_perp

#Percentage Calculations of all Armed Assults and Facility Attacks After 9/11:
white_after_target_percentage = white_after_target / total_after * 100
white_after_target_percentage

white_after_perp_percentage = white_after_perp / total_after * 100
white_after_perp_percentage

arabic_after_target_percentage = arabic_after_target/total_after *100
arabic_after_target_percentage

arabic_after_perp_percentage = arabic_after_perp/total_after *100
arabic_after_perp_percentage

nativeamerican_after_target_percentage = nativeamerican_after_target/total_after *100
nativeamerican_after_target_percentage

nativeamerican_after_perp_percentage = nativeamerican_after_perp/total_after *100
nativeamerican_after_perp_percentage

asian_after_target_percentage = asian_after_target/total_after *100
asian_after_target_percentage

asian_after_perp_percentage = asian_after_perp/total_after *100
asian_after_perp_percentage

black_after_target_percentage = black_after_target / total_after * 100
black_after_target_percentage

black_after_perp_percentage = black_after_perp / total_after * 100
black_after_perp_percentage

latin_after_target_percentage = latin_before_target / total_after * 100
latin_after_target_percentage

latin_after_perp_percentage = latin_after_perp / total_after * 100
latin_after_perp_percentage

#Percentage Changes Before and After 9/11
white_target_percent_change = (white_after_target_percentage - white_before_target_percentage) / white_before_target_percentage * 100
white_target_percent_change

white_perp_percent_change = (white_after_perp_percentage - white_before_perp_percentage) / white_before_perp_percentage * 100
white_perp_percent_change

arabic_target_percent_change = (arabic_after_target_percentage-arabic_before_target_percentage)/arabic_before_target_percentage *100
arabic_target_percent_change
#can't calculate Arabic perpetrator increase because there were 0 records before 9/11

nativeamerican_target_percent_change = (nativeamerican_after_target_percentage-nativeamerican_before_target_percentage)/nativeamerican_before_target_percentage *100
nativeamerican_target_percent_change
#can't calculate Native American perpetrator increase because there were 0 records before 9/11

asian_target_percent_change = (asian_after_target_percentage-asian_before_target_percentage)/asian_before_target_percentage *100
asian_target_percent_change

asian_perp_percent_change = (asian_after_perp_percentage-asian_before_perp_percentage)/asian_before_perp_percentage *100
asian_perp_percent_change

black_target_percent_change = (black_after_target_percentage-black_before_target_percentage)/black_before_target_percentage *100
black_target_percent_change

black_perp_percent_change = (black_after_perp_percentage-black_before_perp_percentage)/black_before_perp_percentage *100
black_perp_percent_change

latin_target_percent_change = (latin_after_target_percentage-latin_before_target_percentage)/latin_before_target_percentage *100
latin_target_percent_change

latin_perp_percent_change = (latin_after_perp_percentage-latin_before_perp_percentage)/latin_before_perp_percentage *100
latin_perp_percent_change








