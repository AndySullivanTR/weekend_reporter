"""
Populate Weekend Reporter application with actual employee names from WEEKEND REPORTER ROTATION
121 reporters total
"""
import json
from werkzeug.security import generate_password_hash
import os

# Reporters from WEEKEND REPORTER ROTATION.docx
# Format: (Last name, First name, email prefix)
reporters = [
    ("Aboulenein", "Ahmed", "ahmed.aboulenein"),
    ("Ahmed", "Saqib", "saqib.ahmed"),
    ("Alleyne-Morris", "Shawana", "shawana.alleyne-morris"),
    ("Anand", "Nupur", "Nupur.Anand"),
    ("Azhar", "Saeed", "saeed.azhar"),
    ("Baertlein", "Lisa P.", "Lisa.Baertlein"),
    ("Banco", "Erin", "Erin.Banco"),
    ("Barbuscia", "Davide", "Davide.Barbuscia"),
    ("Bautzer", "Tatiana", "Tatiana.Bautzer"),
    ("Bensinger", "Greg", "greg.bensinger"),
    ("Binnie", "Isla", "Isla.Binnie"),
    ("Brettell", "Karen J.", "Karen.Brettell"),
    ("Brittain", "Blake", "Blake.Brittain"),
    ("Brown", "Nicholas P.", "Nicholas.P.Brown"),
    ("Cai", "Kenrick", "Kenrick.Cai"),
    ("Campos", "Rodrigo", "rodrigo.campos"),
    ("Carew", "Sinead M.", "Sinead.Carew"),
    ("Catchpole", "Dan", "Dan.Catchpole"),
    ("Cavale", "Siddharth", "siddharth.cavale"),
    ("Chavez", "Gertrude", "gertrude.chavez"),
    ("Cherney", "Max A.", "Max.Cherney"),
    ("Chmielewski", "Dawn C.", "Dawn.Chmielewski"),
    ("Chung", "Andrew", "andrew.chung"),
    ("Cohen", "Luc", "luc.cohen"),
    ("Conlin", "Michelle", "Michelle.Conlin"),
    ("Cooke", "Kristina R.", "Kristina.Cooke"),
    ("Culp", "Stephen R.", "Stephen.Culp"),
    ("Cunningham", "Waylon", "Waylon.Cunningham"),
    ("Dang", "Sheila", "Sheila.Dang"),
    ("Dastin", "Jeffrey", "Jeffrey.Dastin"),
    ("Delevingne", "Lawrence", "Lawrence.Delevingne"),
    ("Derby", "Michael", "Michael.Derby"),
    ("DiNapoli", "Jessica", "Jessica.DiNapoli"),
    ("DiSavino", "Scott P.", "scott.disavino"),
    ("Douglas", "Leah", "Leah.Douglas"),
    ("Eckert", "Nora", "Nora.Eckert"),
    ("Erman", "Michael D.", "Michael.Erman"),
    ("Flowers", "Bianca", "Bianca.Flowers"),
    ("Freifeld", "Karen", "Karen.Freifeld"),
    ("French", "David J.", "Davidj.French"),
    ("Gardner", "Timothy", "timothy.gardner"),
    ("Gillison", "Douglas", "Douglas.Gillison"),
    ("Godoy", "Jody", "Jody.Godoy"),
    ("Groom", "Nichola L.", "Nichola.Groom"),
    ("Hall", "Kalea", "Kalea.Hall"),
    ("Herbst", "Svea A.", "svea.herbst"),
    ("Hickman", "Renee", "Renee.Hickman"),
    ("Hood-Nuño", "David", "David.Hood"),
    ("Hu", "Krystal", "Krystal.Hu"),
    ("Huffstutter", "PJ", "PJ.Huffstutter"),
    ("Ingwersen", "Julie R.", "Julie.Ingwersen"),
    ("Jao", "Nicole", "Nicole.Jao"),
    ("Jeans", "David", "David.Jeans"),
    ("Jones", "Diana", "Diana.Jones2"),
    ("Kearney", "Laila", "laila.kearney"),
    ("Kerber", "Ross J.", "Ross.Kerber"),
    ("Khan", "Shariq A.", "Shariq.Khan"),
    ("Kirkham", "Chris", "Chris.Kirkham"),
    ("Knauth", "Dietrich", "Dietrich.Knauth"),
    ("Koh", "Gui Qing", "guiqing.koh"),
    ("Krauskopf", "Lewis S.", "Lewis.Krauskopf"),
    ("Landay", "Jonathan S.", "Jonathan.Landay"),
    ("Lang", "Hannah", "Hannah.Lang"),
    ("Levine", "Daniel R.", "Dan.Levine"),
    ("Levy", "Rachael", "Rachael.Levy"),
    ("Lynch", "Sarah N.", "Sarah.N.Lynch"),
    ("Matthews", "Laura", "Laura.Matthews"),
    ("McCartney", "Georgina", "Georgina.McCartney"),
    ("McCaskill", "Nolan", "Nolan.McCaskill"),
    ("McGee", "Suzanne", "Suzanne.McGee"),
    ("McKay", "Rich", "Rich.McKay"),
    ("McLaughlin", "Timothy J.", "Tim.McLaughlin"),
    ("MCLYMORE", "ARRIANA", "ARRIANA.MCLYMORE"),
    ("Mikolajczak", "Chuck", "Charles.Mikolajczak"),
    ("Mutikani", "Lucia V.", "Lucia.Mutikani"),
    ("Nellis", "Stephen", "Stephen.Nellis"),
    ("Niasse", "Amina", "Amina.Niasse"),
    ("Oguh", "Chibuike", "Chibuike.Oguh"),
    ("Oladipo", "Doyinsola", "Doyinsola.Oladipo"),
    ("Parraga", "Marianna", "Marianna.Parraga"),
    ("Paul", "Katie", "Katie.Paul"),
    ("Plume", "Karl", "karl.plume"),
    ("Polansek", "Tom", "Thomas.Polansek"),
    ("Prentice", "Chris", "christine.prentice"),
    ("Queen", "Jack", "Jack.Queen"),
    ("Randewich", "Noel", "Noel.Randewich"),
    ("Raymond", "Nate", "Nate.Raymond"),
    ("Respaut", "Robin", "Robin.Respaut"),
    ("Roulette", "Joey", "Joey.Roulette"),
    ("Roy", "Abhirup", "abhirup.roy"),
    ("Rozen", "Courtney", "Courtney.Rozen"),
    ("Saphir", "Ann", "Ann.Saphir"),
    ("Scarcella", "Mike", "Mike.Scarcella"),
    ("Scheyder", "Ernest", "Ernest.Scheyder"),
    ("Schlitz", "Heather", "Heather.Schlitz"),
    ("Seba", "Erwin", "Erwin.Seba"),
    ("Seetharaman", "Deepa", "deepa.seetharaman"),
    ("Shepardson", "David", "David.Shepardson"),
    ("Shirouzu", "Norihiko", "Norihiko.Shirouzu"),
    ("Singh", "Rajesh Kumar", "rajeshkumar.singh"),
    ("Somasekhar", "Arathy", "arathy.s"),
    ("Spector", "Mike", "Mike.Spector"),
    ("Steenhuysen", "Julie D.", "julie.steenhuysen"),
    ("Stempel", "Jonathan E.", "Jon.Stempel"),
    ("Stone", "Mike", "mike.stone"),
    ("Summerville", "Abigail", "Abigail.Summerville"),
    ("Teixeira", "Marcelo", "Marcelo.Teixeira"),
    ("Terhune", "Chad", "Chad.Terhune"),
    ("Tracy", "Matt", "Matt.Tracy"),
    ("Tsvetkova", "Maria", "maria.tsvetkova"),
    ("Valetkevitch", "Caroline", "Caroline.Valetkevitch"),
    ("Valle", "Sabrina", "Sabrina.Valle"),
    ("Vicens", "AJ", "A.J.Vicens"),
    ("Vinn", "Milana", "Milana.Vinn"),
    ("Volcovici", "Valerie", "valerie.volcovici"),
    ("Wang", "Echo", "E.Wang"),
    ("Wiessner", "Daniel", "Daniel.Wiessner"),
    ("Williams", "Curtis", "Curtis.Williams"),
    ("Wingrove", "Patrick", "Patrick.Wingrove"),
    ("Winter", "Jana", "Jana.Winter"),
    ("Wolfe", "Jan", "Jan.Wolfe"),
]

# Sort by last name
reporters.sort(key=lambda x: x[0])

# Create reporters dictionary
reporter_dict = {}

# Manager account
reporter_dict['admin'] = {
    'name': 'Admin',
    'is_manager': True,
    'password': generate_password_hash('admin123')
}

# Add reporters
for last_name, first_name, email_prefix in reporters:
    # Use email prefix (before @) as username
    username = email_prefix.lower()
    
    # Display name format: "Last, First"
    display_name = f"{last_name}, {first_name}"
    
    reporter_dict[username] = {
        'name': display_name,
        'is_manager': False,
        'password': generate_password_hash('password')
    }

# Save to data directory
data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)

output_file = os.path.join(data_dir, 'reporters.json')
with open(output_file, 'w') as f:
    json.dump(reporter_dict, f, indent=2)

print(f"✓ Created {len(reporters)} reporter accounts")
print(f"✓ Saved to: {output_file}")
print(f"\nManager login:")
print(f"  Username: admin")
print(f"  Password: admin123")
print(f"\nEmployee login (all reporters):")
print(f"  Username: [email prefix before @]")
print(f"  Password: password")
print(f"\nExample logins:")
print(f"  Username: ahmed.aboulenein")
print(f"  Username: andrew.chung")
print(f"  Username: luc.cohen")
print(f"\nFirst 5 reporters (sorted alphabetically by last name):")
for i, (last_name, first_name, email_prefix) in enumerate(reporters[:5], 1):
    print(f"  {i}. {last_name}, {first_name} (username: {email_prefix.lower()})")
print(f"  ...")
