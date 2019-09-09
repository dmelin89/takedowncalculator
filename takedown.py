import pandas as pd
import datetime

#  DQ export of CE List
ce_list = pd.read_csv('C:\\Users\dmelin\PycharmProjects\TakedownCalculator\InputFiles\july.csv')
ce_hh_types = ce_list[['FamilyAcctID', 'EnrollDate', 'ExitDate', 'ChronicHomeless',
                       'VeteranStatus', 'YouthHousehold', 'enrollid', 'clientid']].copy()
#  CE Referrals
ref = pd.read_excel('C:\\Users\dmelin\PycharmProjects\TakedownCalculator\InputFiles\MonthlyReferrals\july.xlsx')

# move ins/housed report
housed = pd.read_excel('C:\\Users\dmelin\PycharmProjects\TakedownCalculator\InputFiles\MoveIns\july.xlsx')
ce_ref = ref.merge(ce_hh_types, how='left', left_on='ClientID', right_on='clientid')
hh_housed = housed.merge(ce_hh_types, how='left', left_on='ClientID', right_on='clientid')

#  sets enrolldate as datetime
ce_list['EnrollDate'] = pd.to_datetime(ce_list['EnrollDate'])

#  monthly total DFs
mo_tot = ce_list[ce_list['ExitDate'].isnull()]

ch_month_total_df = mo_tot[mo_tot['ChronicHomeless'].isin(['Individual', 'By Association'])]
vet_month_total_df = mo_tot[mo_tot['VeteranStatus'] == 'Yes (1)']
youth_month_total_df = mo_tot[mo_tot['YouthHousehold'] == 'Yes']

#  deduplicate dfs
#  mo_tot_dedup = mo_tot.drop_duplicates(subset=['FamilyAcctID'], keep='first')
ch_dedup = ch_month_total_df.drop_duplicates(subset=['FamilyAcctID'], keep='first')
vet_dedup = vet_month_total_df.drop_duplicates(subset=['FamilyAcctID'], keep='first')
youth_dedup = youth_month_total_df.drop_duplicates(subset=['FamilyAcctID'], keep='first')

#  get monthly totals
ch_month_total = int(ch_dedup['FamilyAcctID'].nunique())
vet_month_total = int(vet_dedup['FamilyAcctID'].nunique())
youth_month_total = int(youth_dedup['FamilyAcctID'].nunique())

#  filters ce list by new enrollments for that month
vet_inflow = vet_dedup[(vet_dedup['EnrollDate'] >= pd.Timestamp(datetime.date(2019, 7, 1))) &
                       (vet_dedup['EnrollDate'] <= pd.Timestamp(datetime.date(2019, 7, 31)))]

inflow = ce_list[(ce_list['EnrollDate'] >= pd.Timestamp(datetime.date(2019, 7, 1)))
                 & (ce_list['EnrollDate'] <= pd.Timestamp(datetime.date(2019, 7, 31)))]

#  all family account IDs before reporting period
fam_accounts = pd.read_excel(
    'C:\\Users\dmelin\PycharmProjects\TakedownCalculator\InputFiles\Households\\fam_accounts_july.xlsx')
fam_accounts.drop_duplicates(subset=['FamilyAcctID'], keep='first', inplace=True)

#  condenses full DQ export to bare minimum columns
household_type = inflow[['FamilyAcctID', 'EnrollDate', 'ExitDate', 'ChronicHomeless',
                         'VeteranStatus', 'YouthHousehold', 'enrollid']].copy()
household_type.drop_duplicates(subset=['FamilyAcctID'], keep='first', inplace=True)

# get vets, deduplicates by household
vet_inf_households = household_type.loc[household_type['VeteranStatus'] == 'Yes (1)'].copy()

#  filters out non-chronically homeless households
ch_df = household_type.dropna(axis='index', subset=['ChronicHomeless'], inplace=False)

#  Youth Households
youth = household_type.loc[household_type['YouthHousehold'] == 'Yes'].copy()

prev_on_list = fam_accounts.merge(ch_df, on='FamilyAcctID', how='inner', validate='1:1')
vet_prev = fam_accounts.merge(vet_inf_households, on='FamilyAcctID', how='inner', validate='1:1', indicator=True)
youth_prev = fam_accounts.merge(youth, on='FamilyAcctID', how='inner', validate='1:1')

#  counts family account ID numbers
print('Chronic Monthly Total:', ch_month_total)
ch = int(ch_df['FamilyAcctID'].nunique())
ch_prev = int(prev_on_list['FamilyAcctID'].nunique())
print('CH Inflow:', ch)
print('Number of CH Households previously on list:', ch_prev)
print('CH Newly Added:', (ch-ch_prev))
print('')

print('Vet Monthly Total:', vet_month_total)
vt = int(vet_inflow['FamilyAcctID'].nunique())
print('Vet Inflow:', vt)
vt_prev = int(vet_prev['FamilyAcctID'].nunique())
print('Vets Previously on list:', vt_prev)
print('Vets Newly Added:', (vt-vt_prev))
print('')

print('Youth Monthly Total:', youth_month_total)
yt = int(youth['FamilyAcctID'].nunique())
print('Youth Inflow:', yt)
yt_prev = int(youth_prev['FamilyAcctID'].nunique())
print('Youth Previously on the list:', yt_prev)
print('Youth Newly Added:', (yt - yt_prev))
print('')

with pd.ExcelWriter('C:\\Users\dmelin\PycharmProjects\TakedownCalculator\OutputFiles\\takedownnumbers.xlsx') as writer:
    ch_df.to_excel(writer, sheet_name='Chronic', index=False)
    vet_inf_households.to_excel(writer, sheet_name='Vets', index=False)
    youth.to_excel(writer, sheet_name='Youth', index=False)
    ce_ref.to_excel(writer, sheet_name='Referrals', index=False)
    hh_housed.to_excel(writer, sheet_name='Housed', index=False)
    mo_tot.to_excel(writer, sheet_name='MOTotalTest', index=False)

