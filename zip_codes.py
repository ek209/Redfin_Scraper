import pandas as pd

#loads or creates bad_zipcode file into dataframe and list
def bad_zips_load(bad_zips_path):
    try:
        bad_zips_df = pd.read_csv(bad_zips_path)
    except FileNotFoundError:
        bad_zips_df = pd.DataFrame({'Zip Codes' : []})
        bad_zips_df.to_csv(bad_zips_path, index=False)
    return bad_zips_df, bad_zips_df['Zip Codes'].to_list()

states_dict = { 'Alabama' : [num for num in range(35004, 36926)],
               'Alaska' : [num for num in range(99501,99950)],
               'Arizona' : [num for num in range(85001, 86557)],
               'Arkansas' : [num for num in range(71601,72960)],
               'California' : [num for num in range(90001,96163)],
               'Colorado' : [num for num in range(80001,81659)],
               'Connecticut' : [num for num in range(6001, 6390)] + [num for num in range(6401,6929)],
               'District of Columbia': [num for num in range(20001,20040)] + [num for num in range(20042,20600)] + [20799],
               'Delaware' : [num for num in range(19701,19981)],
               'Florida' : [num for num in range(32004,34998)],
               'Georgia' : [num for num in range(30001,32000)] + [39901],
               'Hawaii' : [num for num in range(96701,96899)],
               'Idaho' : [num for num in range(83201,83878)],
               'Illinois' : [num for num in range(60001,63000)],
               'Indiana' : [num for num in range(46001,47998)],
               'Iowa' : [num for num in range(50001,52810)] + [68119, 68120],
               'Kansas' : [num for num in range(66002,67955)],
               'Kentucky' : [num for num in range(40003,42789)],
               'Louisiana' : [num for num in range(70001,71498)],
               'Maine' : [num for num in range(3901,4993)],
               'Maryland' : [num for num in range(20588,21931)],
               'Massachusettes' : [num for num in range(1001,5545)],
               'Michigan' : [num for num in range(48001,49972)],
               'Minnesota' : [num for num in range(55001,56764)],
               'Mississippi' : [num for num in range(38601,39777)],
               'Missouri' : [num for num in range(63001,65900)],
               'Montana' : [num for num in range(59001,59938)],
               'Nebraska' : [num for num in range(68001,69638)],
               'Nevada'	: [num for num in range(88901,89884)],
               'New Hampshire' : [num for num in range(3031,3898)],
               'New Jersey'	: [num for num in range(7001,8990)],
               'New Mexico'	: [num for num in range(87001,88440)],
               'New York' : [num for num in range(501,14926)],
               'North Carolina'	: [num for num in range(27006,28909)],
               'North Dakota' : [num for num in range(58001,58857)],
               'Ohio' : [num for num in range(43001,46000)],
               'Oklahoma' : [num for num in range(73001,74967)],
               'Oregon' : [num for num in range(97001,97921)],
               'Pennsylvania' : [num for num in range(15001,19641)],
               'Rhode Island' : [num for num in range(2801,2941)],
               'South Carolina' : [num for num in range(29001,29946)],
               'South Dakota' : [num for num in range(57001,57800)],
               'Tennessee' : [num for num in range(37010,38560)],
               'Texas' : [num for num in range(73301,88596)],
               'Utah' : [num for num in range(84001,84793)],
               'Vermont' : [num for num in range(5001,5908)],
               'Virginia' :	[num for num in range(20101,24659)],
               'Washington' : [num for num in range(98001,99404)],
               'West Virginia' : [num for num in range(24701,26886)],
               'Wisconsin' : [num for num in range(53001,54991)],
               'Wyoming' : [num for num in range(82001,83415)]
               }
               
us_zip_list = []
for zip_codes_list in states_dict.values():
    us_zip_list += zip_codes_list
states_dict['United States'] = us_zip_list