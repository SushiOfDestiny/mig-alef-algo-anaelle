import numpy as np
import pandas as pd
import tech_eco_data


nHours = 8760
timeStep = 10
t = np.arange(1,nHours + 1)[::timeStep]
nHours = len(t)

zones = ['PACA']
scenar = 1

yearZero = 2020
yearFinal = 2040
yearStep = 10
yearList = [yr for yr in range(yearZero, yearFinal+yearStep, yearStep)] # +1 to include the final year
nYears = len(yearList)
areaList = ["Nice","Fos"]

scenario = {}
scenario['areaList'] = areaList
scenario['timeStep'] = timeStep 
scenario['lastTime'] = t[-1]

def demande_h_area(scenar, area, k):
    # un facteur pour différencier Nice de Fos
    # différent scénarios
    if scenar == 0 :
        demande_t_an = [100, 150, 175, 200]
    elif scenar == 1 :
        demande_t_an = [100, 296, 381, 571]
    elif scenar == 2 :
        demande_t_an = [100, 248, 239, 236] 
    elif scenar == 3 :
        demande_t_an = [100, 248, 239, 236] 

    if area == "Nice" :
        return (0.05 * 33.e3 / 8760) * demande_t_an[k] * np.ones(nHours)
    else :
        print( demande_t_an[k])
        return (33.e3 / 8760) * demande_t_an[k] * np.ones(nHours)


scenario['resourceDemand'] =  pd.concat(
    (
        pd.DataFrame(data = { 
          'AREA': area,
          'YEAR': year, 
          'TIMESTAMP': t, # We add the TIMESTAMP so that it can be used as an index later.
          'electricity': np.zeros(nHours),
          'hydrogen': demande_h_area(scenar, area, k), # Hourly constant but increasing demand
          'gas': np.zeros(nHours), 
         } 
        ) for k, year in enumerate(yearList)
    for area in areaList
    )
)
print(scenario['resourceDemand'])
'''
print(scenario['resourceDemand'].head())
print(scenario['resourceDemand'].tail())
'''
scenario['conversionTechs'] = [] 

for area in areaList: 
    for k, year in enumerate(yearList): 
        tech = "Offshore wind - floating"
        maxcap = 10000
        capex, opex, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(tech, hyp='ref', year=year) 
        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Electricity production',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex, 
                    'minCapacity': 0,'maxCapacity': maxcap, 
                    'EmissionCO2': 0, 'Conversion': {'electricity': 1, 'hydrogen':0},
                    'EnergyNbhourCap': 0, # used for hydroelectricity 
                    'capacityLim': 100e3, 'unitPower': 8} 
                }
             )
        )


        tech = "Onshore wind"
        maxcap = 10000
        capex, opex, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(tech, hyp='ref', year=year)
        if area == "Nice" :
            capex *= 1.5
        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Electricity production',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex, 
                    'minCapacity': 0,'maxCapacity': maxcap, 
                    'EmissionCO2': 0, 'Conversion': {'electricity': 1, 'hydrogen':0},
                    'EnergyNbhourCap': 0, # used for hydroelectricity 
                    'capacityLim': 100e3, 'unitPower': 3
                    }, 
                }
             )
        )

        tech = "Ground PV"
        maxcap = 10000
        capex, opex, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(tech, hyp='ref', year=year) 
        if area == "Nice" :
            capex *= 2
        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Electricity production',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex, 
                    'minCapacity': 0,'maxCapacity': maxcap, 
                    'EmissionCO2': 0, 'Conversion': {'electricity': 1, 'hydrogen':0},
                    'EnergyNbhourCap': 0, # used for hydroelectricity 
                    'capacityLim': 100e3, 'unitPower': 1
                    }, 
                }
             )
        )


        tech = "ElectrolysisM"

        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex, 
                    'minCapacity': 0,'maxCapacity': maxcap, 
                    'EmissionCO2': 0, 'Conversion': {'electricity': -1, 'hydrogen':0.69},
                    'EnergyNbhourCap': 0, # used for hydroelectricity 
                    'capacityLim': 100e3, 'unitPower': 1 
                    }, 
                }
             )
        )

        tech = "SMR"
        capex, opex, LifeSpan = 800e3, 40e3, 60
        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex, 
                    'minCapacity': 0,'maxCapacity': 100e3, 
                    'EmissionCO2': 0, 'Conversion': {'electricity': 0, 'hydrogen': 1, 'gas': -1.43},
                    'EnergyNbhourCap': 0, # used for hydroelectricity 
                    'capacityLim': 100e3, 'unitPower': 320
                    }, 
                }
             )
        )
        
        tech = "Existing SMR"
        capex, opex, LifeSpan = 0e3, 40e3, 30
        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex, 
                    'minCapacity': 1 if year == yearZero else 0,'maxCapacity': 1 if year == yearZero  else 0, 
                    'EmissionCO2': 0, 'Conversion': {'electricity': 0, 'hydrogen': 1, 'gas': -1.43},
                    'EnergyNbhourCap': 0, # used for hydroelectricity 
                    'capacityLim': 320 if year == yearZero else 0, 'unitPower': 320
                    }, 
                }
             )
        )

        tech = "SMR + CCS1"
        capex, opex, LifeSpan = 900e3, 45e3, 60
        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex, 
                    'minCapacity': 0,'maxCapacity': 100e3, 
                    'EmissionCO2': -169, 'Conversion': {'electricity': -0.17, 'hydrogen': 1, 'gas': -1.43},
                    'EnergyNbhourCap': 0, # used for hydroelectricity 
                    'capacityLim': 100e3, 'unitPower': 320
                    }, 
                }
             )
        )

        tech = "SMR + CCS2"
        capex, opex, LifeSpan = 1000e3, 50e3, 60
        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Hydrogen production',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 'operationCost': opex, 
                    'minCapacity': 0,'maxCapacity': 100e3, 
                    'EmissionCO2': -268, 'Conversion': {'electricity': -0.34, 'hydrogen': 1, 'gas': -1.43},
                    'EnergyNbhourCap': 0, # used for hydroelectricity 
                    'capacityLim': 100e3, 'unitPower': 320 
                    }, 
                }
             )
        )

        tech = "CCS1"
        capex, opex, LifeSpan = 100e3, 0e3, 60
        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Carbon capture',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 
                    'operationCost': opex, 'capacityLim': 100e3, 'unitPower': 320}, 
                }
             )
        )

        tech = "CCS2"
        capex, opex, LifeSpan = 100e3, 0e3, 60
        scenario['conversionTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'Category': 'Carbon capture',
                    'LifeSpan': LifeSpan, 'powerCost': 0, 'investCost': capex, 
                    'operationCost': opex, 'capacityLim': 100e3, 'unitPower': 320}, 
                }
             )
        )

scenario['conversionTechs'] =  pd.concat(scenario['conversionTechs'], axis=1) 

scenario['storageTechs'] = [] 
for area in areaList:
    for k, year in enumerate(yearList): 
        tech = "Battery"
        capex1, opex1, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(tech + ' - 1h', hyp='ref', year=year)
        capex4, opex4, LifeSpan = tech_eco_data.get_capex_new_tech_RTE(tech + ' - 4h', hyp='ref', year=year)
        capex_per_kWh = (capex4 - capex1) / 3
        capex_per_kW = capex1 - capex_per_kWh

        scenario['storageTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 'storageResource': 'electricity',  # ambiguïté du nom des paramètres ?
                    'storageLifeSpan': LifeSpan, 
                    'storagePowerCost': capex_per_kW, 
                    'storageEnergyCost': capex_per_kWh, 
                    'storageOperationCost': opex1, # TODO: according to RTE OPEX seems to vary with energy rather than power
                    'p_max': 5000, 
                    'c_max': 50000, 
                    'storageChargeFactors': {'electricity': 0.9200},
                    'storageDischargeFactors': {'electricity': 1.09},
                    'storageDissipation': 0.0085,  
                    }, 
                }
             )
        )

        tech = "Salt cavern"
        scenario['storageTechs'].append(
            pd.DataFrame(data={tech: 
                    {'AREA': area, 'YEAR': year, 
                   'storageResource': 'hydrogen', 
                   'storageLifeSpan': 40, 
                    'storagePowerCost': 0, 
                    'storageEnergyCost': 350e3, 
                    'storageOperationCost': 2e3, 
                    'p_max': 10000, 
                    'c_max': 100000, 
                    'storageChargeFactors': {'electricity': 0.0168, 'hydrogen': 1.0},
                    'storageDischargeFactors': {'hydrogen': 1.0},
                    'storageDissipation': 0,
                    }, 
                }
             )
        )

scenario['storageTechs'] =  pd.concat(scenario['storageTechs'], axis=1) 

scenario['transportTechs'] = []
for k, year in enumerate(yearList):
    ttech = 'Pipeline_S'
    p_max = 50000
    p_max_fonc = 100
    capex, opex, LifeSpan = 320,250,40
    scenario['transportTechs'].append(
        pd.DataFrame(data={ttech:
            {'YEAR' : year, 'transportResource': 'hydrogen',
            'transportLifeSpan':LifeSpan, 'transportPowerCost': 0, 'transportInvestCost': capex, 'transportOperationCost':opex,
            'transportMinPower':0, 'transportMaxPower': p_max,
            'transportEmissionCO2':0,
            'transportChargeFactors': {'hydrogen' : 0.01},
            'transportDischargeFactors': {'hydrogen' : 0.01},
            'transportDissipation':0.0,
            'transportMaxPowerFonc': p_max_fonc  # puissance maximale de fonctionnement du pipeline (=débit max), fixée
            }
        }
        )
    )

    ttech = 'Pipeline_M'
    p_max = 50000
    p_max_fonc = 1000
    capex, opex, LifeSpan = 290,225,40
    scenario['transportTechs'].append(
        pd.DataFrame(data={ttech:
            {'YEAR' : year, 'transportResource': 'hydrogen',
            'transportLifeSpan':LifeSpan, 'transportPowerCost': 0, 'transportInvestCost': capex, 'transportOperationCost':opex,
            'transportMinPower':0, 'transportMaxPower': p_max,
            'transportEmissionCO2':0,
            'transportChargeFactors': {'hydrogen' : 0.01},
            'transportDischargeFactors': {'hydrogen' : 0.01},
            'transportDissipation':0.0,
            'transportMaxPowerFonc': p_max_fonc  # puissance maximale de fonctionnement du pipeline (=débit max), fixée
            }
        }
        )
    )

    ttech = 'Pipeline_L'
    p_max = 50000
    p_max_fonc = 10000
    capex, opex, LifeSpan = 261,203,40
    scenario['transportTechs'].append(
        pd.DataFrame(data={ttech:
            {'YEAR' : year, 'transportResource': 'hydrogen',
            'transportLifeSpan':LifeSpan, 'transportPowerCost': 0, 'transportInvestCost': capex, 'transportOperationCost':opex,
            'transportMinPower':0, 'transportMaxPower': p_max,
            'transportEmissionCO2':0,
            'transportChargeFactors': {'hydrogen' : 0.01},
            'transportDischargeFactors': {'hydrogen' : 0.01},
            'transportDissipation':0.0,
            'transportMaxPowerFonc': p_max_fonc  # puissance maximale de fonctionnement du pipeline (=débit max), fixée
            }
        }
        )
    )


# ttech = truck transporting hydrogen
for k, year in enumerate(yearList):
    ttech = 'truckTransportingHydrogen'
    p_max = 500  # to change
    p_max_fonc = 0 # ttech n'est pas discrétisée
    capex, opex, LifeSpan = 290,0,10
    scenario['transportTechs'].append(
        pd.DataFrame(data={ttech:
            {'YEAR' : year, 'transportResource': 'hydrogen',
            'transportLifeSpan':LifeSpan, 'transportPowerCost': 0, 'transportInvestCost': capex, 'transportOperationCost':opex,
            'transportMinPower':0, 'transportMaxPower': p_max,
            'transportEmissionCO2':1/23,
            'transportChargeFactors': {'hydrogen' : 0.07},
            'transportDischargeFactors': {'hydrogen' : 0.01},
            'transportDissipation':0.0,
            'transportMaxPowerFonc': p_max_fonc
            }
        }  
        )
    )


# ttech = truck transporting electricity
#ttech = electric cable


scenario['transportTechs'] =  pd.concat(scenario['transportTechs'], axis=1) 

scenario['carbonTax'] = pd.DataFrame(data=np.linspace(0.0675,0.165, nYears),
    index=yearList, columns=('carbonTax',))

scenario['carbonGoals'] = pd.DataFrame(data=np.linspace(974e6, 205e6, nYears),
    index=yearList, columns=('carbonGoals',))

scenario['maxBiogasCap'] = pd.DataFrame(data=np.linspace(0, 310e6, nYears),
    index=yearList, columns=('maxBiogasCap',))

scenario['gridConnection'] = pd.read_csv("Data/Raw/CalendrierHPHC_TIME.csv", sep=',', decimal='.', skiprows=0,
                                comment="#").set_index(["TIMESTAMP"]).loc[t]

scenario['economicParameters'] = pd.DataFrame({
    'discountRate':[0.04], 
    'financeRate': [0.04]
    }
)

scenario['distances'] = pd.DataFrame(
    data=[0,200,200,0],
    index=[("Fos", "Fos"),("Fos", "Nice"),("Nice", "Fos"),("Nice", "Nice")],
    columns=["distances"]
    )



df_res_ref = pd.read_csv('./Data/Raw/set2020-2050_horaire_TIMExRESxYEAR.csv', 
    sep=',', decimal='.', skiprows=0,comment="#").set_index(["YEAR", "TIMESTAMP",'RESOURCES'])

scenario['resourceImportPrices'] = pd.concat(
    (
        pd.DataFrame(data={
            'AREA': area,
            'YEAR': year, 
            'TIMESTAMP': t, 
            'electricity': df_res_ref.loc[(year, slice(None), 'electricity'),'importCost'].values[::timeStep],
            'natural gas': 2 * df_res_ref.loc[(year, slice(None), 'gazNat'),'importCost'].values[::timeStep],
            'biogas': 150 * np.ones(nHours),
            'hydrogen': 60/33 * 1000 * np.ones(nHours),
        }) for k, year in enumerate(yearList[1:])
    for area in areaList
    )
)

scenario['resourceImportCO2eq'] = pd.concat(
    (
        pd.DataFrame(data={
            'AREA': area,
            'YEAR': year, 
            'TIMESTAMP': t, 
            'electricity': df_res_ref.loc[(year, slice(None), 'electricity'),'emission'].values[::timeStep],
            'gas': max(0, 0.03 * (1 - (year - yearZero)/(2050 - yearZero))) * 29 / 13.1 + 203.5  * (1 - tech_eco_data.get_biogas_share_in_network_RTE(year)), # Taking 100 yr GWP of methane and 3% losses due to upstream leaks. Losses drop to zero in 2050. 
            'natural gas': max(0, 0.03 * (1 - (year - yearZero)/(2050 - yearZero))) * 29 / 13.1 + 203.5  * (1 - tech_eco_data.get_biogas_share_in_network_RTE(year)), # Taking 100 yr GWP of methane and 3% losses due to upstream leaks. Losses drop to zero in 2050. 
            'biogas': max(0, 0.03 * (1 - (year - yearZero)/(2050 - yearZero))) * 29 / 13.1,
            'hydrogen': max(0, 0.05  - .03 * (year - yearZero)/(2050 - yearZero)) * 11 / 33, # Taking 100 yr GWP of H2 and 5% losses due to upstream leaks. Leaks fall to 2% in 2050 See: https://www.energypolicy.columbia.edu/research/commentary/hydrogen-leakage-potential-risk-hydrogen-economy
        }) for k, year in enumerate(yearList[1:])
    for area in areaList
    )
)

scenario['convTechList'] = ["Offshore wind - floating", "Onshore wind", "Ground PV", "ElectrolysisS","ElectrolysisM","ElectrolysisL"]
ctechs = scenario['convTechList']
availabilityFactor = pd.read_csv('Data/Raw/availabilityFactor2020-2050_PACA_TIMExTECHxYEAR - renamed.csv',
                                 sep=',', decimal='.', skiprows=0).set_index(["YEAR", "TIMESTAMP", "TECHNOLOGIES"]).loc[(slice(None), t, slice(None))]
itechs = availabilityFactor.index.isin(ctechs, level=2)
scenario['availability'] = availabilityFactor.loc[(slice(None), slice(None), itechs)]

# availability pour transport ?


scenario["yearList"] = yearList 
scenario["areaList"] = areaList
scenario["transitionFactors"] =pd.DataFrame(
    {'TECHNO1':['Existing SMR', 'Existing SMR', 'SMR', 'SMR', 'SMR + CCS1'],
    'TECHNO2':['SMR + CCS1','SMR + CCS2', 'SMR + CCS1','SMR + CCS2','SMR + CCS2'],
    'TransFactor': 1}).set_index(['TECHNO1','TECHNO2'])