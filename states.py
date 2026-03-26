# Mapping of NOAA Climate at a Glance state IDs to state names
# 1-48 are alphabetical
# 49 is skipped
# 50 is Alaska
# 51 is Hawaii
state_dict = {
    1: 'Alabama', 2: 'Arizona', 3: 'Arkansas', 4: 'California', 5: 'Colorado',
    6: 'Connecticut', 7: 'Delaware', 8: 'Florida', 9: 'Georgia', 10: 'Idaho',
    11: 'Illinois', 12: 'Indiana', 13: 'Iowa', 14: 'Kansas', 15: 'Kentucky',
    16: 'Louisiana', 17: 'Maine', 18: 'Maryland', 19: 'Massachusetts', 20: 'Michigan',
    21: 'Minnesota', 22: 'Mississippi', 23: 'Missouri', 24: 'Montana', 25: 'Nebraska',
    26: 'Nevada', 27: 'New Hampshire', 28: 'New Jersey', 29: 'New Mexico', 30: 'New York',
    31: 'North Carolina', 32: 'North Dakota', 33: 'Ohio', 34: 'Oklahoma', 35: 'Oregon',
    36: 'Pennsylvania', 37: 'Rhode Island', 38: 'South Carolina', 39: 'South Dakota', 40: 'Tennessee',
    41: 'Texas', 42: 'Utah', 43: 'Vermont', 44: 'Virginia', 45: 'Washington',
    46: 'West Virginia', 47: 'Wisconsin', 48: 'Wyoming', 50: 'Alaska', 51: 'Hawaii'
}

# List of state names in the order of their IDs (1-48, 50, 51)
ordered_state_names = [state_dict[i] for i in sorted(state_dict.keys())]