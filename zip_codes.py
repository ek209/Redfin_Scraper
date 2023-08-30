states_dict = { 'Alaska' : [num for num in range(99501,99950)],
               'Alabama' : [num for num in range(35004, 36926)],
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
               'Iowa' : [num for num in range(50001,52810)] + [68119, 68120],
               }
us_zip_list = []
for zip_codes_list in states_dict.values():
    us_zip_list += zip_codes_list
states_dict['United States'] = us_zip_list