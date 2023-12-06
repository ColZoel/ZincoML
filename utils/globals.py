import re

# ------------------------------------ NATURAL LANGUAGE PROCESSING VIA REGEX ------------------------------------------
# set list of common military branches and address pieces for matching
address_names = [" St", " ST", " Blvd", " blvd", " BLVD", " Av", " av", "AV", " rd", " Rd", "RD",
                 " rt", " Rt", "RT", " Route", " ROUTE", " route", " Apt", " APT", " SUITE", " STE ",
                 " Suite ", "Pk", " PK", " Dr", " Street", " STREET", "Ter", " TER", " Ln", " LN", " Lane",  " La ",
                 " Trl", " Trail", " Place", " Pl", " pl", " Crescent"]

special_chars_regex = re.compile(r'[.¥¢%?/>|@«!§#*^;—",_°\[®£\]»“:~©™}=\'‘’<\\]')
quotations = ["’’", '"']
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> REGEX COMPILATIONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
# –––––––> employer is all characters between end of occupation and start of address (below)
lastname_re = re.compile(r'(^”)|(^")|'
                         '(^Ma?[cC] ?[A-ZÑÉ][a-zñé]+)|'  # MC* or Mac*
                         '(^ ?[A-ZÑÉ][a-zñé]+)|'
                         '(^[A-ZÑÉ][a-zñé]+-[A-ZÑÉ][a-zñé]+)|'  # hyphenated
                         '(^O[\' ]{,2}[A-ZÑÉ][a-zñé]+)|'  # O' or D' or O’ or D’
                         '(^D[\' ]{,2}[A-ZÑÉ][a-zñé]+)|'
                         '^D[ea]l? [A-ZÑÉ][a-zñé]+|'  # De, Del or Dal 
                         '^Di [A-ZÑÉ][a-zñé]+|')  # Di

lastname2_re = re.compile(r'(^”|^"|'
                         '^Ma?[cC] ?[A-ZÑÉ][a-zñé]+|'  # MC* or Mac*
                         '^ ?[A-ZÑÉl][a-zñé]+|'
                         '^[A-ZÑÉ][a-zñé]+-[A-ZÑÉ][a-zñé]+|'  # hyphenated
                         '^O[\' ]{,2}[A-ZÑÉ][a-zñé]+|'  # O' or D' or O’ or D’
                         '^D[\' ]{,2}[A-ZÑÉ][a-zñé]+|'
                         '^D[ea]l? [A-ZÑÉ][a-zñé]+|'  # De, Del or Dal 
                         '^Di [A-ZÑÉ][a-zñé]+)')  # Di


firstname_re = re.compile(r'(?<= )([A-ZÑÉ][a-zéñ]*( Anne?)?) ([A-Z] )?|'  # Mary Ann
                          r'(?<= )([A-ZÑÉ][a-zñé]+-[A-ZÑÉ][a-zñé]+) ([A-Z] )?')

firstname2_re = re.compile(r'(?<=[a-zéñ] )('
                           r'[A-ZÑÉ][a-zéñ]* Anne? |'  # Mary Ann
                           r'[A-ZÑÉ][a-zéñ]* |'  # Mary
                           r'[A-ZÑÉ][a-zñé]+-[A-ZÑÉ][a-zñé]+ [A-Z]? )')

mid_initial_re = re.compile(r'(?<=[a-zñé])( [A-Z] )')

suffixes_re = re.compile(r'Jr|Mrs')  # for entires with Jr Mrs included
suffix2_re = re.compile(r'(Jr|Sr|Mrs)')  # for entries with suffixes

military_re = re.compile(r'(USAF|USMC|USN|USCG|USA)')  # entries with specified military branch
person2_re = re.compile(r'& (?P<person2>([A-Z][a-z]+){,2}) (?P<mid2>[A-Z]?)')  # person2 name

person2_re2 = re.compile(r'(?<=& )(?P<person2>([A-Z][a-z;]+){,2}) (?P<mid>[A-Z]?);?')  # person2 name

occupation_re = re.compile(r'(?P<occupation>(( [a-z]{3,}[- \n])+([a-z]{3,})*)|(?<=; )([a-z- \n]{3,})|'
                           r'\S*(log)?ist| '
                           r'emp | studt | retd | dir | [Mm]gr | pres | ctr | clk | eng | vp | admn | chem | wkr |'
                           r' nurse | clerical | teller | prof | asmblr | phys | splst | anlist | sis | bkpr '
                           r'| sls | drvr | lwyr | asst | supvr | atty | chairmn | tchr | slswn | slsmn | exe )+ ')


occupation_re2 = re.compile(r'(?<=[; ])(?P<occupation>([a-z- &\n]{3,})+)'
                            r'(?P<employer>( [A-Za-z&\\]+[ \n]?)*($|(?= [hr\d])))')


address_num_re = re.compile(r'((([hr]?[ISli]?[0-9]+\s)([0-9]*[A-Z]?[a-z]*\s?[0-9]*)+)(\s[A-Z][a-z]{,2})?)')
address_no_num_re = re.compile(r'( [hr][ISli]?(\s[A-Z]+[a-z]*)+)')

address_re2 = re.compile(r'(?<=[\n ][hr\d])([ISli]?[0-9]+[a-z]?( [A-Z][a-z]*)+[ \n]?)')

address_unit_re = re.compile(r'[sS]te [0-9]+[A-Z]?|[aA]pt [A-Z]|[aA]pt [0-9]+[A-Z]?')
address_unit_re2 = re.compile(r'(?<= )([sS]te [0-9]+[A-Z]?|[aA]pt [A-Z]|[aA]pt [0-9]+[A-Za-z]?)')

city_state_re = re.compile(r'(?P<city>(?: r[A-Zl][-\'A-Za-z ]+)+) (?P<state>( [a-zA-Z ]{2,3}))')  # non-local residents
other_loc_re = re.compile(r'( r[A-Zl][-\'A-Za-z ]+) ([A-Zl][-\'A-Za-z ]+)*|r\([A-Z][a-z]{2,}')

other_loc_re2 = re.compile(r'(?<= r)([A-Z][a-z]+[ \n]?[A-Z]{,2})')  # non-local residents

header_re = re.compile('([A-Z]+ to [A-Z]+)|^((r )?RESIDER\n{,2})$|^((h )?HOUSEHOLDER)\n{,2}$')

pagenum = re.compile(r'^[0-9]{1,4}\n{1,2}')

biz_re = re.compile(r'^(([A-Z][a-z]{2,}[ \n]){3,})|'
                     r'^([A-Z]{2,} )|'
                     r'^([A-Z][a-z]+ & )|'
                     r'^([A-Z][a-z]+ ){2,}\(')

phone_re = re.compile(r'(\d{3}-\d{4})')

homeowner_re = re.compile(r'([©@])')

municipal_re = re.compile(r'\((.{,3})\)')  # residents of municipalities

hr_re = re.compile(r'( [hr])(?=[0-9])')

parentheses_re = re.compile(r'(?<=\()([A-Za-z\d ]{3,})(?=\))')
