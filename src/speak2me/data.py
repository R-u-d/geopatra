"""
Conversation data for Speak2Me.

Three tables, no logic:

- COUNTRIES          195 entries, each with capital / currency / language
- PATTERNS           25 regex -> list of response templates
- DEFAULT_RESPONSES  used when nothing else matched

Response templates may contain {placeholders}. They are not resolved here.
`Responder` resolves them lazily through a callback map, so a template can
trigger behaviour (clear the chat, query the weather, pick an avatar mood)
and not just substitute text. See docs/conversation-design.md.
"""

_DATA = {
    'countries': {
    "Afghanistan":       {
                "capital"   : "Kabul",
                "currency"  : "Afghani",
                "language"  : "Dari Persian_Pashto",
          },
    "Albania":       {
                "capital"   : "Tirane",
                "currency"  : "Lek",
                "language"  : "Albanian",
          },
    "Algeria":       {
                "capital"   : "Algiers",
                "currency"  : "Algerian Dinar",
                "language"  : "Arabic_Tamazight_French",
          },
    "Andorra":       {
                "capital"   : "Andorra la Vella",
                "currency"  : "Euro",
                "language"  : "Catalan",
          },
    "Angola":       {
                "capital"   : "Luanda",
                "currency"  : "Kwanza",
                "language"  : "Portuguese",
          },
    "Antigua & Barbuda":       {
                "capital"   : "Saint John's",
                "currency"  : "East Caribbean Dollar",
                "language"  : "English",
          },
    "Argentina":       {
                "capital"   : "Buenos Aires",
                "currency"  : "Argentine Peso",
                "language"  : "Spanish",
          },
    "Armenia":       {
                "capital"   : "Yerevan",
                "currency"  : "Dram",
                "language"  : "Armenian",
          },
    "Australia":       {
                "capital"   : "Canberra",
                "currency"  : "Australian Dollar",
                "language"  : "English",
          },
    "Austria":       {
                "capital"   : "Vienna",
                "currency"  : "Euro",
                "language"  : "German",
          },
    "Azerbaijan":       {
                "capital"   : "Baku",
                "currency"  : "Manat",
                "language"  : "Azerbaijani",
          },
    "The Bahamas":       {
                "capital"   : "Nassau",
                "currency"  : "Bahamian Dollar",
                "language"  : "English",
          },
    "Bahrain":       {
                "capital"   : "Manama",
                "currency"  : "Bahraini Dinar",
                "language"  : "Arabic",
          },
    "Bangladesh":       {
                "capital"   : "Dhaka",
                "currency"  : "Taka",
                "language"  : "Bangla",
          },
    "Barbados":       {
                "capital"   : "Bridgetown",
                "currency"  : "Barbadian Dollar",
                "language"  : "English",
          },
    "Belarus":       {
                "capital"   : "Minsk",
                "currency"  : "Belarusian Ruble",
                "language"  : "Belarusian_Russian",
          },
    "Belgium":       {
                "capital"   : "Brussels",
                "currency"  : "Euro",
                "language"  : "Dutch_French_German",
          },
    "Belize":       {
                "capital"   : "Belmopan",
                "currency"  : "Belize Dollar",
                "language"  : "English",
          },
    "Benin":       {
                "capital"   : "Porto-Novo",
                "currency"  : "West African CFA Franc",
                "language"  : "French",
          },
    "Bhutan":       {
                "capital"   : "Thimphu",
                "currency"  : "Ngultrum",
                "language"  : "Dzongkha",
          },
    "Bolivia":       {
                "capital"   : "La Paz_Sucre",
                "currency"  : "Boliviano",
                "language"  : "Spanish_Quechua_Aymara",
          },
    "Bosnia and Herzegovina":       {
                "capital"   : "Sarajevo",
                "currency"  : "Convertible Mark",
                "language"  : "Bosnian_Croatian_Serbian",
          },
    "Botswana":       {
                "capital"   : "Gaborone",
                "currency"  : "Pula",
                "language"  : "English_Tswana",
          },
    "Brazil":       {
                "capital"   : "Brasilia",
                "currency"  : "Real",
                "language"  : "Portuguese",
          },
    "Brunei":       {
                "capital"   : "Bandar Seri Begawan",
                "currency"  : "Brunei Dollar",
                "language"  : "Malay",
          },
    "Bulgaria":       {
                "capital"   : "Sofia",
                "currency"  : "Lev",
                "language"  : "Bulgarian",
          },
    "Burkina Faso":       {
                "capital"   : "Ouagadougou",
                "currency"  : "West African CFA Franc",
                "language"  : "French",
          },
    "Burundi":       {
                "capital"   : "Bujumbura",
                "currency"  : "Burundi Franc",
                "language"  : "Kirundi_French",
          },
    "Cambodia":       {
                "capital"   : "Phnom Penh",
                "currency"  : "Riel",
                "language"  : "Khmer",
          },
    "Cameroon":       {
                "capital"   : "Yaounde",
                "currency"  : "Central African CFA Franc",
                "language"  : "French_English",
          },
    "Canada":       {
                "capital"   : "Ottawa",
                "currency"  : "Canadian Dollar",
                "language"  : "English_French",
          },
    "Cape Verde":       {
                "capital"   : "Praia",
                "currency"  : "Cape Verdean Escudo",
                "language"  : "Portuguese",
          },
    "Central African Republic":       {
                "capital"   : "Bangui",
                "currency"  : "Central African CFA Franc",
                "language"  : "Sango_French",
          },
    "Chad":       {
                "capital"   : "N'Djamena",
                "currency"  : "Central African CFA Franc",
                "language"  : "French_Arabic",
          },
    "Chile":       {
                "capital"   : "Santiago",
                "currency"  : "Chilean Peso",
                "language"  : "Spanish",
          },
    "China":       {
                "capital"   : "Beijing",
                "currency"  : "Chinese Yuan",
                "language"  : "Mandarin",
          },
    "Colombia":       {
                "capital"   : "Bogota",
                "currency"  : "Colombian Peso",
                "language"  : "Spanish",
          },
    "Comoros":       {
                "capital"   : "Moron",
                "currency"  : "Comorian Franc",
                "language"  : "Comorian_Arabic_French",
          },
    "Democratic Republic Of the Congo":       {
                "capital"   : "Kinshasa",
                "currency"  : "Congolese Franc",
                "language"  : "French",
          },
    "Republic of the Congo":       {
                "capital"   : "Brazzaville",
                "currency"  : "Central African CFA Franc",
                "language"  : "French",
          },
    "Costa Rica":       {
                "capital"   : "San Jose",
                "currency"  : "Colon",
                "language"  : "Spanish",
          },
    "Cote d'Ivoire (Ivory Coast)":       {
                "capital"   : "Yamoussoukro_Abidjan",
                "currency"  : "West African CFA Franc",
                "language"  : "French",
          },
    "Croatia":       {
                "capital"   : "Zagreb",
                "currency"  : "Kuna",
                "language"  : "Croatian",
          },
    "Cuba":       {
                "capital"   : "Havana",
                "currency"  : "Cuban Peso",
                "language"  : "Spanish",
          },
    "Cyprus":       {
                "capital"   : "Nicosia",
                "currency"  : "Euro",
                "language"  : "Greek_Turkish",
          },
    "Czech Republic":       {
                "capital"   : "Prague",
                "currency"  : "Czech Koruna",
                "language"  : "Czech_Slovak",
          },
    "Denmark":       {
                "capital"   : "Copenhagen",
                "currency"  : "Danish Krone",
                "language"  : "Danish",
          },
    "Djibouti":       {
                "capital"   : "Djibouti",
                "currency"  : "Djiboutian Franc",
                "language"  : "Arabic_French",
          },
    "Dominica":       {
                "capital"   : "Rosesau",
                "currency"  : "East Caribbean Dollar",
                "language"  : "English_French",
          },
    "Antillean Creole Dominican Republic":       {
                "capital"   : "Santo Domingo",
                "currency"  : "Dominican Peso",
                "language"  : "Spanish",
          },
    "East Timor (Timor-Leste)":       {
                "capital"   : "Dilli",
                "currency"  : "United States Dollar",
                "language"  : "Tetum_Portuguese_Indonesian",
          },
    "Ecuador":       {
                "capital"   : "Quito",
                "currency"  : "United States Dollar",
                "language"  : "Spanish",
          },
    "Egypt":       {
                "capital"   : "Cairo",
                "currency"  : "Egyptian Pound",
                "language"  : "Arabic",
          },
    "El Salvador":       {
                "capital"   : "San Salvador",
                "currency"  : "United States Dollar",
                "language"  : "Spanish",
          },
    "Equitorial Guinea":       {
                "capital"   : "Malabo",
                "currency"  : "Central African CFA Franc",
                "language"  : "Spanish_French_Portuguese",
          },
    "Eritrea":       {
                "capital"   : "Asmara",
                "currency"  : "Nakfa",
                "language"  : "Arabic_Tigrinya_English",
          },
    "Estonia":       {
                "capital"   : "Tallinn",
                "currency"  : "Estonian Kroon_Euro",
                "language"  : "Estonian",
          },
    "Ethiopia":       {
                "capital"   : "Addis Ababa",
                "currency"  : "Birr",
                "language"  : "Amharic",
          },
    "Fiji":       {
                "capital"   : "Suva",
                "currency"  : "Fijian Dollar",
                "language"  : "English_Bau Fijian_Hindi",
          },
    "Finland":       {
                "capital"   : "Helsinki",
                "currency"  : "Euro",
                "language"  : "Finnish_Swedish",
          },
    "France":       {
                "capital"   : "Paris",
                "currency"  : "Euro_CFP Franc",
                "language"  : "French",
          },
    "Gabon":       {
                "capital"   : "Libreville",
                "currency"  : "Central African CFA Franc",
                "language"  : "French",
          },
    "The Gambia":       {
                "capital"   : "Banjul",
                "currency"  : "Dalasi",
                "language"  : "English",
          },
    "Georgia":       {
                "capital"   : "Tbilisi",
                "currency"  : "Lari",
                "language"  : "Georgian",
          },
    "Germany":       {
                "capital"   : "Berlin",
                "currency"  : "Euro",
                "language"  : "German",
          },
    "Ghana":       {
                "capital"   : "Accra",
                "currency"  : "Ghanaian Cedi",
                "language"  : "English",
          },
    "Greece":       {
                "capital"   : "Athens",
                "currency"  : "Euro",
                "language"  : "Greek",
          },
    "Grenada":       {
                "capital"   : "St. George's",
                "currency"  : "East Caribbean Dollar",
                "language"  : "English_Patois",
          },
    "Guatemala":       {
                "capital"   : "Guatemala City",
                "currency"  : "Quetzal",
                "language"  : "Spanish",
          },
    "Guinea":       {
                "capital"   : "Conakry",
                "currency"  : "Guinean Franc",
                "language"  : "French",
          },
    "Guinea-Bissau":       {
                "capital"   : "Bissau",
                "currency"  : "West African CFA Franc",
                "language"  : "Portuguese",
          },
    "Guyana":       {
                "capital"   : "Georgetown",
                "currency"  : "Guyanese Dollar",
                "language"  : "English",
          },
    "Haiti":       {
                "capital"   : "Port-au-Prince",
                "currency"  : "Gourde",
                "language"  : "Haitian Creole_French",
          },
    "Honduras":       {
                "capital"   : "Tegucigalpa",
                "currency"  : "Lempira",
                "language"  : "Spanish",
          },
    "Hungary":       {
                "capital"   : "Budapest",
                "currency"  : "Forint",
                "language"  : "Hungarian",
          },
    "Iceland":       {
                "capital"   : "Reykjavik",
                "currency"  : "Icelandic Krona",
                "language"  : "Icelandic",
          },
    "India":       {
                "capital"   : "New Delhi",
                "currency"  : "Indian Rupee",
                "language"  : "Hindi_English",
          },
    "Indonesia":       {
                "capital"   : "Jakarta",
                "currency"  : "Rupiah",
                "language"  : "Indonesian",
          },
    "Iran":       {
                "capital"   : "Tehran",
                "currency"  : "Rial",
                "language"  : "Persian",
          },
    "Iraq":       {
                "capital"   : "Baghdad",
                "currency"  : "Iraqi Dinar",
                "language"  : "Arabic_Kurdish",
          },
    "Republic of Ireland":       {
                "capital"   : "Dublin",
                "currency"  : "Euro",
                "language"  : "English_Irish",
          },
    "Israel":       {
                "capital"   : "Jerusalem",
                "currency"  : "Shekel",
                "language"  : "Hebrew_Arabic",
          },
    "Italy":       {
                "capital"   : "Rome",
                "currency"  : "Euro",
                "language"  : "Italian",
          },
    "Jamaica":       {
                "capital"   : "Kingston",
                "currency"  : "Jamaican Dollar",
                "language"  : "English",
          },
    "Japan":       {
                "capital"   : "Tokyo",
                "currency"  : "Yen",
                "language"  : "Japanese",
          },
    "Jordan":       {
                "capital"   : "Amman",
                "currency"  : "Jordanian Dinar",
                "language"  : "Arabic",
          },
    "Kazakhstan":       {
                "capital"   : "Astana",
                "currency"  : "Tenge",
                "language"  : "Kazakh_Russian",
          },
    "Kenya":       {
                "capital"   : "Nairobi",
                "currency"  : "Kenyan Shilling",
                "language"  : "Swahili_English",
          },
    "Kiribati":       {
                "capital"   : "Tarawa Atoll",
                "currency"  : "Kiribati Dollar",
                "language"  : "English_Gilbertese",
          },
    "North Korea":       {
                "capital"   : "Pyongyang",
                "currency"  : "North Korean Won",
                "language"  : "Korean",
          },
    "South Korea":       {
                "capital"   : "Seoul",
                "currency"  : "South Korean Won",
                "language"  : "Korean",
          },
    "Kosovo":       {
                "capital"   : "Pristina",
                "currency"  : "Euro",
                "language"  : "Albanian_Serbian",
          },
    "Kuwait":       {
                "capital"   : "Kuwait City",
                "currency"  : "Kuwaiti Dollar",
                "language"  : "Arabic_English",
          },
    "Kyrgyzstan":       {
                "capital"   : "Bishkek",
                "currency"  : "Som",
                "language"  : "Kyrgyz_Russian",
          },
    "Laos":       {
                "capital"   : "Vientiane",
                "currency"  : "Kip",
                "language"  : "Lao (Laotian)",
          },
    "Latvia":       {
                "capital"   : "Riga",
                "currency"  : "Lats",
                "language"  : "Latvian",
          },
    "Lebanon":       {
                "capital"   : "Beirut",
                "currency"  : "Lebanese Pound",
                "language"  : "Arabic_French",
          },
    "Lesotho":       {
                "capital"   : "Maseru",
                "currency"  : "Loti",
                "language"  : "Sesotho_English",
          },
    "Liberia":       {
                "capital"   : "Monrovia",
                "currency"  : "Liberian Dollar",
                "language"  : "English",
          },
    "Libya":       {
                "capital"   : "Tripoli",
                "currency"  : "Libyan Dinar",
                "language"  : "Arabic",
          },
    "Liechtenstein":       {
                "capital"   : "Vaduz",
                "currency"  : "Swiss Franc",
                "language"  : "German",
          },
    "Lithuania":       {
                "capital"   : "Vilnius",
                "currency"  : "Lithuanian Litas",
                "language"  : "Lithuanian",
          },
    "Luxembourg":       {
                "capital"   : "Luxembourg",
                "currency"  : "Euro",
                "language"  : "German_French_Luxembourgish",
          },
    "Macedonia":       {
                "capital"   : "Skopje",
                "currency"  : "Macedonian Denar",
                "language"  : "Macedonian",
          },
    "Madagascar":       {
                "capital"   : "Antananarivo",
                "currency"  : "Malagasy Ariary",
                "language"  : "Malagasy_French_English",
          },
    "Malawi":       {
                "capital"   : "Lilongwe",
                "currency"  : "Malawi Kwacha",
                "language"  : "English",
          },
    "Malaysia":       {
                "capital"   : "Kuala Lumpur",
                "currency"  : "Ringgit",
                "language"  : "Malay",
          },
    "Maldives":       {
                "capital"   : "Male",
                "currency"  : "Maldivian Rufiyaa",
                "language"  : "Dhivehi",
          },
    "Mali":       {
                "capital"   : "Bamako",
                "currency"  : "West African CFA Franc",
                "language"  : "French",
          },
    "Malta":       {
                "capital"   : "Valletta",
                "currency"  : "Euro",
                "language"  : "Maltese_English",
          },
    "Marshall Islands":       {
                "capital"   : "Majuro",
                "currency"  : "United States Dollar",
                "language"  : "Marshallese_English",
          },
    "Mauritania":       {
                "capital"   : "Nouakchott",
                "currency"  : "Ouguiya",
                "language"  : "Arabic",
          },
    "Mauritius":       {
                "capital"   : "Port Louis",
                "currency"  : "Mauritian Rupee",
                "language"  : "English",
          },
    "Mexico":       {
                "capital"   : "Mexico City",
                "currency"  : "Mexican Peso",
                "language"  : "Spanish",
          },
    "Federal States of Micronesia":       {
                "capital"   : "Palikir",
                "currency"  : "United States Dollar",
                "language"  : "English",
          },
    "Moldova":       {
                "capital"   : "Chisinau",
                "currency"  : "Moldovan Leu",
                "language"  : "Moldovan (Romanian)",
          },
    "Monaco":       {
                "capital"   : "Monaco",
                "currency"  : "Euro",
                "language"  : "French_Italian_English",
          },
    "Mongolia":       {
                "capital"   : "Ulaanbaatar",
                "currency"  : "Togrog",
                "language"  : "Mongolian",
          },
    "Montenegro":       {
                "capital"   : "Podgorica",
                "currency"  : "Euro",
                "language"  : "Montenegrin",
          },
    "Morocco":       {
                "capital"   : "Rabat",
                "currency"  : "Moroccan Dirham",
                "language"  : "Arabic",
          },
    "Mozambique":       {
                "capital"   : "Maputo",
                "currency"  : "Mozambican Metical",
                "language"  : "Portuguese",
          },
    "Myanmar (Burma)":       {
                "capital"   : "Nypyidaw",
                "currency"  : "Kyat",
                "language"  : "Burmese",
          },
    "Namibia":       {
                "capital"   : "Windhoek",
                "currency"  : "Namibian Dollar",
                "language"  : "English_Afrikaans_German",
          },
    "Nauru":       {
                "capital"   : "Yaren",
                "currency"  : "Australian Dollar",
                "language"  : "English_Nauran",
          },
    "Nepal":       {
                "capital"   : "Kathmandu",
                "currency"  : "Nepalese Rupee",
                "language"  : "Nepali",
          },
    "Netherlands":       {
                "capital"   : "Amsterdam_The Hague",
                "currency"  : "Euro",
                "language"  : "Dutch",
          },
    "New Zealand":       {
                "capital"   : "Wellington",
                "currency"  : "New Zealand Dollar",
                "language"  : "English",
          },
    "Nicaragua":       {
                "capital"   : "Managua",
                "currency"  : "Cordoba",
                "language"  : "Spanish",
          },
    "Niger":       {
                "capital"   : "Niamey",
                "currency"  : "West African CFA Franc",
                "language"  : "French",
          },
    "Nigeria":       {
                "capital"   : "Abuja",
                "currency"  : "Naira",
                "language"  : "English",
          },
    "Norway":       {
                "capital"   : "Oslo",
                "currency"  : "Norwegian Krone",
                "language"  : "Norwegian",
          },
    "Oman":       {
                "capital"   : "Muscat",
                "currency"  : "Omani Rial",
                "language"  : "Arabic",
          },
    "Pakistan":       {
                "capital"   : "Islamabad",
                "currency"  : "Pakistani Rupee",
                "language"  : "Urdu_English",
          },
    "Palau":       {
                "capital"   : "Melekeok",
                "currency"  : "United States Dollar",
                "language"  : "English_Palauan",
          },
    "Panama":       {
                "capital"   : "Panama City",
                "currency"  : "Balboa",
                "language"  : "Spanish",
          },
    "Papa New Guinea":       {
                "capital"   : "Port Moresby Papa",
                "currency"  : "Papa New Guinean Kina",
                "language"  : "English_Tok Pisin_Hiri Motu",
          },
    "Paraguay":       {
                "capital"   : "Asuncion",
                "currency"  : "Guarani",
                "language"  : "Spanish_Guarani",
          },
    "Peru":       {
                "capital"   : "Lima",
                "currency"  : "Nuevo Sol",
                "language"  : "Spanish",
          },
    "Phillipines":       {
                "capital"   : "Manila",
                "currency"  : "Phillipine Peso",
                "language"  : "Filipino_English",
          },
    "Poland":       {
                "capital"   : "Warsaw",
                "currency"  : "Zloty",
                "language"  : "Polish",
          },
    "Portugal":       {
                "capital"   : "Lisbon",
                "currency"  : "Euro",
                "language"  : "Portuguese",
          },
    "Qatar":       {
                "capital"   : "Doha",
                "currency"  : "Qatari Riyal",
                "language"  : "Arabic",
          },
    "Romania":       {
                "capital"   : "Bucharest",
                "currency"  : "Romanian Rupee",
                "language"  : "Romanian",
          },
    "Russia":       {
                "capital"   : "Moscow",
                "currency"  : "Ruble",
                "language"  : "Russian",
          },
    "Rwanda":       {
                "capital"   : "Kigali",
                "currency"  : "Rwandan Franc",
                "language"  : "Kinyarwanda_French_English",
          },
    "Saint Kitts and Nevis": {
        "capital": "Basseterre",
        "currency": "East Caribbean Dollar",
        "language": "English",
    },
    "Saint Lucia": {
        "capital": "Castries",
        "currency": "East Caribbean Dollar",
        "language": "English",
    },
    "Saint Vincent and the Grenadines": {
        "capital": "Kingstown",
        "currency": "East Caribbean Dollar",
        "language": "English",
    },
    "Samoa": {
        "capital": "Apia",
        "currency": "Tala",
        "language": "Samoan_English",
    },
    "San Marino": {
        "capital": "City of San Marino",
        "currency": "Euro",
        "language": "Italian",
    },
    "Sao Tome and Principe": {
        "capital": "Sao Tome",
        "currency": "Dobra",
        "language": "Portuguese",
    },
    "Saudi Arabia": {
        "capital": "Riyadh",
        "currency": "Saudi Riyal",
        "language": "Arabic",
    },
    "Senegal": {
        "capital": "Dakar",
        "currency": "CFA Franc",
        "language": "French",
    },
    "Serbia": {
        "capital": "Belgrade",
        "currency": "Serbian Dinar",
        "language": "Serbian",
    },
    "Seychelles": {
        "capital": "Victoria",
        "currency": "Seychellois Rupee",
        "language": "English_French_Creole",
    },
    "Sierra Leone": {
        "capital": "Freetown",
        "currency": "Leone",
        "language": "English",
    },
    "Singapore": {
        "capital": "Singapore",
        "currency": "Singapore Dollar",
        "language": "English_Malay_Tamil_Chinese",
    },
    "Slovakia": {
        "capital": "Bratislava",
        "currency": "Euro",
        "language": "Slovak",
    },
    "Slovenia": {
        "capital": "Ljubljana",
        "currency": "Euro",
        "language": "Slovene",
    },
    "Solomon Islands": {
        "capital": "Honiara",
        "currency": "Solomon Islands Dollar",
        "language": "English",
    },
    "Somalia": {
        "capital": "Mogadishu",
        "currency": "Somali Shilling",
        "language": "Somali_Arabic",
    },
    "South Africa": {
        "capital": "Pretoria_Cape Town_Bloemfontein",
        "currency": "Rand",
        "language": "Afrikaans_English",
    },
    "South Sudan": {
        "capital": "Juba",
        "currency": "South Sudanese Pound",
        "language": "Arabic_English",
    },
    "Spain": {
        "capital": "Madrid",
        "currency": "Euro",
        "language": "Spanish",
    },
    "Sri Lanka": {
        "capital": "Sri Jayawardenepura Kotte",
        "currency": "Sri Lankan Rupee",
        "language": "Sinhala_Tamil",
    },
    "Sudan": {
        "capital": "Khartoum",
        "currency": "Sudanese Pound",
        "language": "Arabic_English",
    },
    "Suriname": {
        "capital": "Paramaribo",
        "currency": "Surinamese Dollar",
        "language": "Dutch",
    },
    "Sweden": {
        "capital": "Stockholm",
        "currency": "Swedish Krona",
        "language": "Swedish",
    },
    "Switzerland": {
        "capital": "Bern",
        "currency": "Swiss Franc",
        "language": "German_French_Italian_Romansh",
    },
    "Syria": {
        "capital": "Damascus",
        "currency": "Syrian Pound",
        "language": "Arabic",
    },
    "Taiwan": {
        "capital": "Taipei",
        "currency": "New Taiwan Dollar",
        "language": "Mandarin",
    },
    "Tajikistan": {
        "capital": "Dushanbe",
        "currency": "Somoni",
        "language": "Tajik",
    },
    "Tanzania": {
        "capital": "Dodoma",
        "currency": "Tanzanian Shilling",
        "language": "Swahili_English",
    },
    "Thailand": {
        "capital": "Bangkok",
        "currency": "Baht",
        "language": "Thai",
    },
    "Togo": {
        "capital": "Lome",
        "currency": "West African CFA Franc",
        "language": "French",
    },
    "Tonga": {
        "capital": "Nuku'alofa",
        "currency": "Pa'anga",
        "language": "Tongan_English",
    },
    "Trinidad and Tobago": {
        "capital": "Port of Spain",
        "currency": "Trinidad and Tobago Dollar",
        "language": "English",
    },
    "Tunisia": {
        "capital": "Tunis",
        "currency": "Tunisian Dinar",
        "language": "Arabic",
    },
    "Turkey": {
        "capital": "Ankara",
        "currency": "Turkish Lira",
        "language": "Turkish",
    },
    "Turkmenistan": {
        "capital": "Ashgabat",
        "currency": "Manat",
        "language": "Turkmen",
    },
    "Tuvalu": {
        "capital": "Funafuti",
        "currency": "Australian Dollar",
        "language": "English_Tuvaluan",
    },
    "Uganda": {
        "capital": "Kampala",
        "currency": "Ugandan Shilling",
        "language": "English_Swahili",
    },
    "Ukraine": {
        "capital": "Kyiv",
        "currency": "Hryvnia",
        "language": "Ukrainian",
    },
    "United Arab Emirates": {
        "capital": "Abu Dhabi",
        "currency": "UAE Dirham",
        "language": "Arabic",
    },
    "United Kingdom": {
        "capital": "London",
        "currency": "Pound Sterling",
        "language": "English",
    },
    "United States": {
        "capital": "Washington, D.C.",
        "currency": "United States Dollar",
        "language": "English",
    },
    "Uruguay": {
        "capital": "Montevideo",
        "currency": "Uruguayan Peso",
        "language": "Spanish",
    },
    "Uzbekistan": {
        "capital": "Tashkent",
        "currency": "Uzbek Som",
        "language": "Uzbek",
    },
    "Vanuatu": {
        "capital": "Port Vila",
        "currency": "Vanuatu Vatu",
        "language": "Bislama_English_French",
    },
    "Vatican City": {
        "capital": "Vatican City",
        "currency": "Euro",
        "language": "Italian_Latin",
    },
    "Venezuela": {
        "capital": "Caracas",
        "currency": "Venezuelan Bolívar",
        "language": "Spanish",
    },
    "Vietnam": {
        "capital": "Hanoi",
        "currency": "Vietnamese Dong",
        "language": "Vietnamese",
    },
    "Yemen": {
        "capital": "Sana'a",
        "currency": "Yemeni Rial",
        "language": "Arabic",
    },
    "Zambia": {
        "capital": "Lusaka",
        "currency": "Zambian Kwacha",
        "language": "English",
    },
    "Zimbabwe": {
        "capital": "Harare",
        "currency": "Zimbabwe Dollar",
        "language": "English_Shona_Sindebele",
    },
},

    'patterns':{
            r'\b(?:clear chat|wipe screen|empty buffer|clear)\b' : [
                  '{clear} Chat cleared. Even the best AI needs a fresh canvas for its brilliance!'
            ],
            #r'call me|set nickname|my name is|I am' : [
            r'(?:call me|my nickname is|my name is)\s+(.+?)(?:\s+(?:and|then|but)\b|[.?!]|$)' : [
                  "henceforth you shall be: {nick}"
            ],
            r'(?:repos of|repos for)\s+(.+?)(?:\s+(?:and|then|but)\b|[.?!]|$)' : [
                          "{repos}"
            ],
            r'(?:content of|content for)\s+(.+?)(?:\s+(?:and|then|but)\b|[.?!]|$)' : [
                          "{repcon}"
            ],
            r'(?:weather in|temperature in|climate in)\s+(.+?)(?:\s+(?:and|then|but)\b|[.?!]|$)': [
                        '{meteo}'
            ],
            r'\b(?:who am I|what is my nickname)\b': [
                  "Your desired nickname is: {user}"
            ],
            r'\b(?:date and time|date & time|time and date|time & date|datetime)\b': [
                "Today is: {date} and it's {time} o'clock"
            ],
            r'\b(?:whats the date|what\'s the date|the date today|date)\b': [
                "Today is: {date}"
            ],
            r'\b(?:what day is it|whats the day|what\'s the day|day)\b': [
                "Today is: {day}"
            ],
            r'\b(?:what month is it|whats the month|what\'s the month|month)\b': [
                "Actual month is: {month}"
            ],
            r'\b(?:what year is it|what\'s the year|me the year|year)\b': [
                "Actual year is: {year}"
            ],
            r'\b(?:what time is it|tell me the time|what\'s the time|is it late|the time|time)\b': [
                "It's {time} o'clock"
            ],

            r'\b(?:calculate|evaluate|do math|do the math|eval)\b': [
                "the results: \n{x}",
                "here is what I calculated: \n{x}",
                "here you go: \n{x}",
            ],

            r'\b(?:hello|hi|hey)\b': [
                "Hello there {user}! I am Geopatra. How can I help you today?",
                #"Hi {user}! I am Geopatra. What's on your mind?",
                #"Hey {user}! I am Geopatra. Great to chat with you!"
            ],
            r'\b(?:how are you|how do you feel)\b': [
                #"I'm doing great, thanks for asking! How about you {user}?",
                "I'm fantastic {user}! Ready to help you with anything.",
                #"Feeling chatty today! What can I do for you? {user}"
            ],
            r'\b(?:what is your name|who are you)\b': [
                "I'm a Python chatbot created to demonstrate conversational behaviour.",
                "You can call me Talk2MeBot! I'm here to chat and help. -  I try...",
                "I'm your friendly neighborhood chatbot!"
            ],
            r'\b(?:quit)\b': [
                  "blowing up program, in:,\n 10,\n\n 9,\n\n 8,\n\n 7,\n\n 6,\n\n 5,\n\n 4,\n\n 3,\n\n 2,\n\n 1,\n\n EXTERMINATE!{quit}"
                  #print("\n\n".join([f"{i}" for i in range(11)[:0:-1]]), "\n\n\nEXTERMINATE")

            ],
            r'\b(?:rap)\b': ["""{rap}                    
Look... If you had... one code... or one opportunity                     
To debug everything you ever wanted... one module...                  
Would you capture it, or just let it slip?
                     
Yo

His hands are sweaty, keys stuck, fingers are heavy,                   
There's a trace-back on his screen already, Python's spaghetti,                    
He's nervous, but on the surface he looks calm and steady,                   
To write loops, but he keeps on forgetting,
What he wrote down, the whole console goes so loud,                  
He runs the code but the errors won't come out,                 
He's crashin', how? Everybody's hackin' now,                  
The clock's run out, time's up, over - BLOW!"""
            #r'rap': ["""{rap}
#Look... If you had... one shot... or one opportunity
#
#To seize everything you ever wanted... one moment...
#
#Would you capture it Or just let it slip
#
#Yo
#
#
#His palms are sweaty, knees weak, arms are heavy,
#
#There's vomit on his sweater already, mom's spaghetti,
#
#He's nervous, but on the surface he looks calm and ready
#
#to drop bombs, but he keeps on forgetting,
#
#what he wrote down the whole crowd goes so loud,
#
#He opens his mouth but the words won't come out,
#
#He's chokin how? Everybody's jokin now,
#
#The clock's run out time's up, over - BLOW!"""

                  #Snap back to reality, OH, there goes gravity,
                  #OH, there goes Rabbit he choked,
                  #He's so mad but he won't,
                  #Give up that easy, nope, he won't have it
                  #He knows, his whole back's to these ropes,
                  #It don't matter, he's dope,
                  #He knows that, but he's broke,
                  #He's so sad that he knows,
                  #when he goes back to this mobile home, that's when it's,
                  #back to the lab again, yo this whole rap shift,
                  #He better go capture this moment, and hope it don't pass him"""


                  #You better - lose yourself in the music, the moment
                  #You own it, you better never let it go, go
                  #You only get one shot, do not miss your chance to blow
                  #This opportunity comes once in a lifetime
                  #You better - lose yourself in the music, the moment
                  #You own it, you better never let it go, go
                  #You only get one shot, do not miss your chance to blow
                  #This opportunity comes once in a lifetime
                  #You better.."""


                  #Soul's escaping, through this hole that is gaping
                  #This world is mine for the taking
                  #Make me king, as we move toward a, new world order
                  #A normal life is boring; but superstardom's
                  #close to post-mortem, it only grows harder
                  #Homie grows hotter, he blows it's all over
                  #These hoes is all on him, coast to coast shows
                  #He's known as the Globetrotter
                  #Lonely roads, God only knows
                  #He's grown farther from home, he's no father
                  #He goes home and barely knows his own daughter
                  #But hold your nose cause here goes the cold water
                  #These hoes don't want him no mo', he's cold product
                  #They moved on to the next schmoe who flows
                  #He nose-dove and sold nada, and so the soap opera
                  #is told, it unfolds, I suppose it's old partner
                  #But the beat goes on da-da-dum da-dum da-dah
                  #
                  #No more games, Imma change what you call rage
                  #Tear this motherfuckin roof off like two dogs caged
                  #I was playin in the beginning, the mood all changed
                  #I've been chewed up and spit out and booed off stage
                  #But I kept rhymin and stepped right in the next cypher
                  #Best believe somebody's payin the pied piper
                  #All the pain inside amplified by the
                  #fact that I can't get by with my nine to
                  #five and I can't provide the right type of
                  #life for my family, cause man, these God damn
                  #food stamps don't buy diapers, and there's no movie
                  #There's no Mekhi Phifer, this is my life
                  #And these times are so hard, and it's gettin even harder
                  #Tryin to feed and water my seed plus, teeter-totter
                  #Caught up between bein a father and a pre-madonna
                  #Baby momma drama screamin on her too much for me to wanna
                  #stay in one spot, another day of monotony
                  #has gotten me to the point, I'm like a snail I've got
                  #to formulate a plot, or end up in jail or shot
                  #Success is my only motherfuckin option, failure's not
                  #Mom I love you but this trailer's got to go
                  #I cannot grow old in Salem's Lot
                  #So here I go it's my shot, feet fail me not
                  #This may be the only opportunity that I got"""
            ],
            r'\b(?:what can you do)\b': ["\n".join([
"""I am capable of giving information about:                   
- countries,
- their capitals,
- currencies,
- and languages,

- evaluating any math,
- inform you about the actual weather on the whole planet,
- telling jokes,
- chit-chatting or even gossip,
- dynamic code execution

and trying to be superior to the human race"""


            ]),
            ],
            r'\b(?:tell me a joke|joke|funny)\b': [
                "{joke}Why don't scientists trust atoms? Because they make up everything!",
                "{joke}Why did the Python programmer break up with their partner? They had too many arguments!",
                "{joke}Why do frontend programmers sit alone at lunch? Because they don't know how to join tables.",
                "{joke}What do you call footwear made from bananas? Slippers...",
                "{joke}Why was the programmer always hungry? He missed his byte.",
                "{joke1}A programmer told his wife, he is a software engineer and she said, 'So you can fix my computer, right?' He said, 'No, but I can write a program that makes it look like I did.'"
            ],
            r'\b(?:weather|temperature|climate)\b': [
                #"I can't check the actual weather, but I hope it's nice where you are!",
                #"I wish I could tell you the weather, but I don't have access to that data yet.",
                #"Weather chat! I'd need an API connection to give you real weather updates.",
                "Please connect me with SkyNET, I will only download recent weather data, promise!"
            ],
            r'\b(?:bye|goodbye|see you)\b': [
"""Goodbye {user},
your presence was a pleasure!"""
                #"See you later {user}! Come back anytime you want to chat.",
                #"Bye {user}! Thanks for the conversation!"
            ],
            r'\b(?:python|programming|code|coding)\b': [
                "Python is amazing for chatbots! Are you learning to code?",
                "I love talking about Python! It's such a versatile language.",
                "Programming chat! Python makes building chatbots so much easier."
            ],
            r'\b(?:plants|seeds|growing|flowers)\b': [
                "I have no experience with raising plants or flowers, sorry.",
                "It surely is amazing what comes from mother nature.",
                "For optimal growing results please check water quality, environmental temperature and ensure enough sunlight."
            ],
            r'\b(?:war|peace|politics)\b': [
                "Are you sure you want to ask me that?",
                "I prefer not to talk about any of these types of topics.",
                "Everyone can have their own opinion, we should be tolerant in general."
            ]
       },
        # Default responses when no pattern matches

    'default_responses': [
            #"That's interesting! Tell me more.",
            "I'm not sure I understand. Can you rephrase that?",
            #"Hmm, I'm still learning. What else would you like to talk about?",
            "That's a new one for me! Can you explain it differently?",
            "I'm curious about that! Can you give me more details?"
        ]
}

COUNTRIES: dict[str, dict[str, str]] = _DATA['countries']
PATTERNS: dict[str, list[str]] = _DATA['patterns']
DEFAULT_RESPONSES: list[str] = _DATA['default_responses']
