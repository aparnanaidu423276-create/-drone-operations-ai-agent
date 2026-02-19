import streamlit as st
from google.oauth2.service_account import Credentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]

creds = Credentials.from_service_account_info(creds_dict, scopes=scope)

client = gspread.authorize(creds)


sheet_url = "https://docs.google.com/spreadsheets/d/1Vm5MdEiAUbGFga71A-wlqc10juyewYW1q7UCP1ignxE/edit?gid=0#gid=0"
spreadsheet = client.open_by_url(sheet_url)


pilot_sheet = spreadsheet.worksheet("Pilot_Roster")
drone_sheet = spreadsheet.worksheet("drone_fleet")
mission_sheet = spreadsheet.worksheet("missions")


pilot_data = pilot_sheet.get_all_records()
drone_data = drone_sheet.get_all_records()
mission_data = mission_sheet.get_all_records()


pilot_df = pd.DataFrame(pilot_data)
drone_df = pd.DataFrame(drone_data)
mission_df = pd.DataFrame(mission_data)


print("\n--- PILOT DATA ---")
print(pilot_df)

print("\n--- DRONE DATA ---")
print(drone_df)

print("\n--- MISSION DATA ---")
print(mission_df)

def match_pilots(mission, pilot_df):
    suitable = pilot_df[
        (pilot_df['status'] == 'Available') &
        (pilot_df['skills'].str.contains(mission['required_skills'], case=False)) &
        (pilot_df['location'] == mission['location'])
    ]
    return suitable

for _, mission in mission_df.iterrows():
    print(f"\nMission: {mission['project_id']}")
    print(match_pilots(mission, pilot_df))

    def match_drones(mission, drone_df):
        if mission['weather'] == "Rainy":
            return drone_df[
                (drone_df['status'] == 'Available') &
                (drone_df['capabilities'].str.contains("IP43"))
        ]
        else:
            return drone_df[drone_df['status'] == 'Available']
    
def check_skill(pilot, mission):
    if mission['required_skills'].lower() not in pilot['skills'].lower():
        return "Skill mismatch"
    
def check_budget(pilot, mission):
    cost = pilot['daily_rate_inr'] * 3  # assume 3 days
    if cost > mission['budget']:
        return "Budget exceeded"
def check_budget(pilot, mission):
    cost = pilot['daily_rate_inr'] * 3  # assume 3 days
    if cost > mission['budget']:
        return " Budget exceeded"     

def check_weather(drone, mission):
    if mission['weather'] == "Rainy" and "IP43" not in drone['capabilities']:
        return " Weather risk" 
def check_location(pilot, mission):
    if pilot['location'] != mission['location']:
        return " Location mismatch" 
    
def urgent_reassign(mission, pilot_df):
    return pilot_df[
        (pilot_df['status'] == 'Available') &
        (pilot_df['skills'].str.contains(mission['required_skills'], case=False))
    ]

def urgent_reassign(mission, pilot_df):
    
    # 1. Try same skill (ignore location)
    backup = pilot_df[
        (pilot_df['status'] == 'Available') &
        (pilot_df['skills'].str.contains(mission['required_skills'], case=False))
    ]
    
    if not backup.empty:
        return backup
    
    # 2. Last option: ignore status also
    backup = pilot_df[
        pilot_df['skills'].str.contains(mission['required_skills'], case=False)
    ]
    
    return backup

pilot_sheet.update_cell(2, 6, "Assigned")

import streamlit as st

st.title("Drone Coordinator AI")

if st.button("Run Matching"):
    for _, mission in mission_df.iterrows():
        st.write(match_pilots(mission, pilot_df))

for _, mission in mission_df.iterrows():
    print("\n======================")
    print("Mission:", mission['project_id'])

    pilots = match_pilots(mission, pilot_df)

    if pilots.empty:
        print(" No pilot available for this mission")
        
        backup = urgent_reassign(mission, pilot_df)
        
        if backup.empty:
            print("No backup available")
        else:
            print(" Suggested backup:")
            print(backup[['name', 'location', 'skills', 'status']])
    
    else:
        print(" Suitable pilots:")
        print(pilots[['name', 'location', 'skills']])    

def match_drone(mission, drone_df):
    if mission['weather'] == "Rainy":
        return drone_df[
            (drone_df['status'] == 'Available') &
            (drone_df['capabilities'].str.contains("IP43"))
        ]
    else:
        return drone_df[drone_df['status'] == 'Available']            

def get_warnings(pilot, mission):
    warnings = []

    if pilot is not None:
        if pilot['location'] != mission['location']:
            warnings.append("Location mismatch")

        cost = pilot['daily_rate_inr'] * 3
        if cost > mission['budget']:
            warnings.append("Budget exceeded")

    if mission['weather'] == "Rainy":
        warnings.append("Weather risk")

    return warnings  

drone = match_drone(mission, drone_df)

if not drone.empty:
    print(" Drone Assigned:", drone.iloc[0]['model'])
else:
    print(" No suitable drone")

warnings = get_warnings(
    pilots.iloc[0] if not pilots.empty else None, mission)

if warnings:
    print(" Warning:")
    for w in warnings:
        print("-", w)
else:

    print("✔ No conflicts")

