# Dictionary of SDG indicators
indicators = {
    '1: No Poverty': [
        'SI.POV.DDAY',  # Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)
        'SI.POV.GINI',  # GINI index
        'SI.POV.GAPS',  # Poverty gap at $2.15 a day (2017 PPP) (%)
        'SI.DST.FRST.20',  # Income share held by lowest 20%
    ],
    '2: Zero Hunger': [
        'SN.ITK.DEFC.ZS',  # Prevalence of undernourishment (% of population)
        'SH.STA.STNT.ZS',  # Prevalence of stunting, height for age (% of children under 5)
        'AG.YLD.CREL.KG',  # Cereal yield (kg per hectare)
        'AG.LND.AGRI.ZS',  # Agricultural land (% of land area)
    ],
    '3: Good Health and Well-being': [
        'SH.DYN.MORT',  # Mortality rate, under-5 (per 1,000 live births)
        'SH.STA.MMRT',  # Maternal mortality ratio (modeled estimate, per 100,000 live births)
        'SH.XPD.CHEX.PC.CD',  # Current health expenditure per capita (current US$)
        'SP.DYN.LE00.IN',  # Life expectancy at birth, total (years)
    ],
    '4: Quality Education': [
        'SE.PRM.CMPT.ZS',  # Primary completion rate, total (% of relevant age group)
        'SE.SEC.ENRR',  # School enrollment, secondary (% gross)
        'SE.ADT.LITR.ZS',  # Literacy rate, adult total (% of people ages 15 and above)
        'SE.XPD.TOTL.GD.ZS',  # Government expenditure on education, total (% of GDP)
    ],
    '5: Gender Equality': [
        'SG.GEN.PARL.ZS',  # Proportion of seats held by women in national parliaments (%)
        'SL.TLF.CACT.FE.ZS',  # Labor force participation rate, female (% of female population ages 15+)
        'SE.ENR.PRIM.FM.ZS',  # School enrollment, primary (gross), gender parity index (GPI)
        'SG.VAW.REAS.ZS',  # Women who believe a husband is justified in beating his wife (any of five reasons) (%)
    ],
    '6: Clean Water and Sanitation': [
        'SH.H2O.SMDW.ZS',  # People using safely managed drinking water services (% of population)
        'SH.STA.SMSS.ZS',  # People using safely managed sanitation services (% of population)
        'ER.H2O.FWTL.ZS',  # Annual freshwater withdrawals, total (% of internal resources)
        'ER.H2O.FWST.ZS',  # Level of water stress: freshwater withdrawal as a proportion of available freshwater resources
    ],
    '7: Affordable and Clean Energy': [
        'EG.ELC.ACCS.ZS',  # Access to electricity (% of population)
        'EG.FEC.RNEW.ZS',  # Renewable energy consumption (% of total final energy consumption)
        'EG.USE.PCAP.KG.OE',  # Energy use (kg of oil equivalent per capita)
        'EG.ELC.LOSS.ZS',  # Electric power transmission and distribution losses (% of output)
    ],
    '8: Decent Work and Economic Growth': [
        'NY.GDP.PCAP.KD.ZG',  # GDP per capita growth (annual %)
        'SL.UEM.TOTL.ZS',  # Unemployment, total (% of total labor force)
        'SL.GDP.PCAP.EM.KD',  # GDP per person employed (constant 2017 PPP $)
        'SL.EMP.VULN.ZS',  # Vulnerable employment, total (% of total employment)
    ],
    '9: Industry, Innovation and Infrastructure': [
        'GB.XPD.RSDV.GD.ZS',  # Research and development expenditure (% of GDP)
        'NV.IND.MANF.ZS',  # Manufacturing, value added (% of GDP)
        'IT.NET.USER.ZS',  # Individuals using the Internet (% of population)
        'TX.VAL.TECH.MF.ZS',  # High-technology exports (% of manufactured exports)
    ],
    '10: Reduced Inequalities': [
        'SI.POV.GINI',  # GINI index
        'SI.DST.05TH.20',  # Income share held by highest 20%
        'SI.DST.FRST.20',  # Income share held by lowest 20%
        'BX.TRF.PWKR.DT.GD.ZS',  # Personal remittances, received (% of GDP)
    ],
    '11: Sustainable Cities and Communities': [
        'EN.URB.MCTY.TL.ZS',  # Population in urban agglomerations of more than 1 million (% of total population)
        'EN.POP.SLUM.UR.ZS',  # Population living in slums (% of urban population)
        'EN.ATM.PM25.MC.M3',  # PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)
        'VC.IHR.PSRC.P5',  # Intentional homicides (per 100,000 people)
    ],
    '12: Responsible Consumption and Production': [
        'EN.ATM.CO2E.PC',  # CO2 emissions (metric tons per capita)
        'AG.LND.AGRI.ZS',  # Agricultural land (% of land area)
        'ER.MRN.PTMR.ZS',  # Marine protected areas (% of territorial waters)
        'EP.PMP.DESL.CD',  # Pump price for diesel fuel (US$ per liter)
    ],
    '13: Climate Action': [
        'EN.ATM.CO2E.PC',  # CO2 emissions (metric tons per capita)
        'EG.USE.COMM.FO.ZS',  # Fossil fuel energy consumption (% of total)
        'AG.LND.FRST.ZS',  # Forest area (% of land area)
        'EN.CLC.MDAT.ZS',  # Droughts, floods, extreme temperatures (% of population, average 1990-2009)
    ],
    '14: Life Below Water': [
        'ER.MRN.PTMR.ZS',  # Marine protected areas (% of territorial waters)
        'ER.FSH.CAPT.MT',  # Capture fisheries production (metric tons)
        'EN.MAM.THRD.NO',  # Mammal species, threatened
        'ER.H2O.FWTL.ZS',  # Annual freshwater withdrawals, total (% of internal resources)
    ],
    '15: Life on Land': [
        'AG.LND.FRST.ZS',  # Forest area (% of land area)
        'ER.LND.PTLD.ZS',  # Terrestrial protected areas (% of total land area)
        'EN.MAM.THRD.NO',  # Mammal species, threatened
        'AG.LND.AGRI.ZS',  # Agricultural land (% of land area)
    ],
    '16: Peace, Justice and Strong Institutions': [
        'VC.IHR.PSRC.P5',  # Intentional homicides (per 100,000 people)
        'GE.EST',  # Government Effectiveness: Estimate
        'IC.FRM.BRIB.ZS',  # Bribery incidence (% of firms experiencing at least one bribe payment request)
        'SG.DMK.SRCR.FN.ZS',  # Women making their own informed decisions regarding sexual relations, contraceptive use and reproductive health care (% of women age 15-49)
    ],
    '17: Partnerships for the Goals': [
        'DT.ODA.ODAT.GN.ZS',  # Net ODA received (% of GNI)
        'BX.KLT.DINV.WD.GD.ZS',  # Foreign direct investment, net inflows (% of GDP)
        'IT.NET.USER.ZS',  # Individuals using the Internet (% of population)
        'GC.DOD.TOTL.GD.ZS',  # Central government debt, total (% of GDP)
    ]
}

# Function to get all indicator codes
def get_all_indicator_codes():
    return [code for theme_codes in indicators.values() for code in theme_codes]

# Function to get theme for a given indicator code
def get_theme_for_indicator(indicator_code):
    for theme, codes in indicators.items():
        if indicator_code in codes:
            return theme
    return None
