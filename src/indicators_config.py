# Dictionary of SDG indicators
indicators = {
    'SDG 1: No Poverty': [
        'SI.POV.NAHC',  # Poverty headcount ratio at national poverty lines (% of population)
        'SI.POV.DDAY',  # Poverty headcount ratio at $2.15 a day (2017 PPP) (% of population)
        'SI.POV.GINI',  # GINI index
        'SI.DST.05TH.20'  # Income share held by highest 20%
    ],
    'SDG 2: Zero Hunger': [
        'SN.ITK.DEFC.ZS',  # Prevalence of undernourishment (% of population)
        'AG.YLD.CREL.KG',  # Cereal yield (kg per hectare)
        'AG.LND.AGRI.ZS',  # Agricultural land (% of land area)
        'AG.PRD.FOOD.XD'  # Food production index (2014-2016 = 100)
    ],
    'SDG 3: Good Health and Well-being': [
        'SH.DYN.MORT',  # Mortality rate, under-5 (per 1,000 live births)
        'SH.STA.MMRT',  # Maternal mortality ratio (modeled estimate, per 100,000 live births)
        'SH.HIV.INCD.ZS',  # Incidence of HIV (% of uninfected population ages 15-49)
        'SH.IMM.MEAS',  # Immunization, measles (% of children ages 12-23 months)
        'SH.XPD.CHEX.PC.CD',  # Current health expenditure per capita (current US$)
        'SP.DYN.LE00.IN'  # Life expectancy at birth, total (years)
    ],
    'SDG 4: Quality Education': [
        'SE.PRM.ENRR',  # School enrollment, primary (% gross)
        'SE.SEC.ENRR',  # School enrollment, secondary (% gross)
        'SE.ADT.LITR.ZS',  # Literacy rate, adult total (% of people ages 15 and above)
        'SE.XPD.TOTL.GD.ZS',  # Government expenditure on education, total (% of GDP)
        'SE.TER.ENRR'  # School enrollment, tertiary (% gross)
    ],
    'SDG 5: Gender Equality': [
        'SG.GEN.PARL.ZS',  # Proportion of seats held by women in national parliaments (%)
        'SL.TLF.CACT.FE.ZS',  # Labor force participation rate, female (% of female population ages 15+)
        'SE.ENR.PRIM.FM.ZS',  # School enrollment, primary (gross), gender parity index (GPI)
        'SG.VAW.REAS.ZS'  # Women who believe a husband is justified in beating his wife (any of five reasons) (%)
    ],
    'SDG 6: Clean Water and Sanitation': [
        'SH.H2O.SMDW.ZS',  # People using safely managed drinking water services (% of population)
        'SH.STA.SMSS.ZS',  # People using safely managed sanitation services (% of population)
        'ER.H2O.FWTL.ZS',  # Annual freshwater withdrawals, total (% of internal resources)
        'EE.BOD.TOTL.KG'  # Organic water pollutant (BOD) emissions (kg per day)
    ],
    'SDG 7: Affordable and Clean Energy': [
        'EG.ELC.ACCS.ZS',  # Access to electricity (% of population)
        'EG.USE.ELEC.KH.PC',  # Electric power consumption (kWh per capita)
        'EG.USE.PCAP.KG.OE',  # Energy use (kg of oil equivalent per capita)
        'EG.FEC.RNEW.ZS'  # Renewable energy consumption (% of total final energy consumption)
    ],
    'SDG 8: Decent Work and Economic Growth': [
        'NY.GDP.MKTP.KD.ZG',  # GDP growth (annual %)
        'NY.GDP.PCAP.CD',  # GDP per capita (current US$)
        'SL.EMP.VULN.ZS',  # Vulnerable employment, total (% of total employment)
        'SL.UEM.TOTL.ZS',  # Unemployment, total (% of total labor force)
        'SL.TLF.CACT.ZS',  # Labor force participation rate, total (% of total population ages 15+)
        'SL.EMP.TOTL.SP.ZS'  # Employment to population ratio, 15+, total (%)
    ],
    'SDG 9: Industry, Innovation and Infrastructure': [
        'IT.NET.USER.ZS',  # Individuals using the Internet (% of population)
        'IT.CEL.SETS.P2',  # Mobile cellular subscriptions (per 100 people)
        'GB.XPD.RSDV.GD.ZS',  # Research and development expenditure (% of GDP)
        'IP.PAT.RESD'  # Patent applications, residents
    ],
    'SDG 10: Reduced Inequalities': [
        'SI.POV.GINI',  # GINI index
        'SI.DST.05TH.20',  # Income share held by highest 20%
        'BX.KLT.DINV.WD.GD.ZS'  # Foreign direct investment, net inflows (% of GDP)
    ],
    'SDG 11: Sustainable Cities and Communities': [
        'SP.URB.TOTL.IN.ZS',  # Urban population (% of total population)
        'EN.ATM.PM25.MC.M3',  # PM2.5 air pollution, mean annual exposure (micrograms per cubic meter)
    ],
    'SDG 12: Responsible Consumption and Production': [
        'AG.PRD.FOOD.XD',  # Food production index (2014-2016 = 100)
        'EG.USE.PCAP.KG.OE',  # Energy use (kg of oil equivalent per capita)
    ],
    'SDG 13: Climate Action': [
        'EN.ATM.CO2E.PC',  # CO2 emissions (metric tons per capita)
        'AG.LND.FRST.ZS',  # Forest area (% of land area)
        'EG.ELC.RNEW.ZS',  # Renewable electricity output (% of total electricity output)
    ],
    'SDG 14: Life Below Water': [
        'ER.PTD.TOTL.ZS',  # Terrestrial and marine protected areas (% of total territorial area)
        'EE.BOD.TOTL.KG'  # Organic water pollutant (BOD) emissions (kg per day)
    ],
    'SDG 15: Life on Land': [
        'AG.LND.FRST.ZS',  # Forest area (% of land area)
        'ER.PTD.TOTL.ZS',  # Terrestrial and marine protected areas (% of total territorial area)
    ],
    'SDG 16: Peace, Justice and Strong Institutions': [
        'IC.BUS.EASE.XQ',  # Ease of doing business score (0 = lowest performance to 100 = best performance)
        'IQ.CPA.PROT.XQ',  # CPIA property rights and rule-based governance rating (1=low to 6=high)
        'GE.EST',  # Government Effectiveness: Estimate
        'RQ.EST'  # Regulatory Quality: Estimate
    ],
    'SDG 17: Partnerships for the Goals': [
        'DT.DOD.DECT.CD',  # External debt stocks, total (current US$)
        'GC.DOD.TOTL.GD.ZS',  # Central government debt, total (% of GDP)
        'NE.TRD.GNFS.ZS',  # Trade (% of GDP)
        'BX.KLT.DINV.WD.GD.ZS'  # Foreign direct investment, net inflows (% of GDP)
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
