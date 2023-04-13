import psr.npf
import copy


"""
Example network:

      1     3 AC Lines 4 CSC  5      6
 (G)--|-OO--|----------|--)|--|------|->      SVC
      2 |   |----------|             |-OO-|-[-(|-]->
 (G)--|-|   |          |->                7
            | DC Links |
       <-)|-|-[]----[]-|-|(->
            |-[]----[]-|
"""

# Count the number of series network elements.
series_count = 1

data = psr.npf.NpFile()
data.revision = 1
data.title = "Case title"

# Create system, area and region.
system = psr.npf.System()
system.number = 1
system.name = "System"
system.id = "sy"
data.systems.append(system)

area1 = psr.npf.Area()
area1.number = 1
area1.name = "Generation Area"
area1.id = "ar01"
data.areas.append(area1)

area2 = psr.npf.Area()
area2.number = 2
area2.name = "Transmission Area"
area2.id = "ar02"
data.areas.append(area2)

region = psr.npf.Region()
region.number = 1
region.name = "Region"
region.id = "re01"
region.system = system
data.regions.append(region)

# Create/add buses
bus1 = psr.npf.Bus()
bus1.number = 1
bus1.name = "Bus 1"
bus1.kvbase = 18.0
bus1.system = system
bus1.area = area1
bus1.region = region
data.buses.append(bus1)

bus2 = psr.npf.Bus()
bus2.number = 2
bus2.name = "Bus 2"
bus2.kvbase = 18.0
bus2.system = system
bus2.area = area1
bus2.region = region
data.buses.append(bus2)

bus3 = psr.npf.Bus()
bus3.number = 3
bus3.name = "Bus 3"
bus3.kvbase = 230.0
bus3.system = system
bus3.area = area2
bus3.region = region
data.buses.append(bus3)

bus4 = psr.npf.Bus()
bus4.number = 4
bus4.name = "Bus 4"
bus4.kvbase = 230.0
bus4.system = system
bus4.area = area2
bus4.region = region
data.buses.append(bus4)

bus5 = psr.npf.Bus()
bus5.number = 5
bus5.name = "Bus 5"
bus5.kvbase = 230.0
bus5.system = system
bus5.area = area2
bus5.region = region
data.buses.append(bus5)

bus6 = psr.npf.Bus()
bus6.number = 6
bus6.name = "Bus 6"
bus6.kvbase = 230.0
bus6.system = system
bus6.area = area2
bus6.region = region
data.buses.append(bus6)

bus7 = psr.npf.Bus()
bus7.number = 7
bus7.name = "Bus 7"
bus7.kvbase = 13.8
bus7.system = system
bus7.area = area2
bus7.region = region
data.buses.append(bus7)


# Demands

demand1 = psr.npf.Demand()
demand1.number = 1
demand1.name = "Demand 1"
demand1.bus = bus4
demand1.p_mw = 150.0
demand1.q_mw = 35.0
data.demands.append(demand1)

demand2 = psr.npf.Demand()
demand2.number = 2
demand2.name = "Demand 2"
demand2.bus = bus6
demand2.p_mw = 300.0
demand2.q_mw = 100.0
data.demands.append(demand2)


# Generators
generator1 = psr.npf.Generator()
generator1.number = 1
generator1.name = "G01"
generator1.bus = bus1
generator1.ctr_bus = bus3
generator1.pmax = 200.0
generator1.qmin = -180.0
generator1.qmax = +200.0
generator1.type = psr.npf.Generator.TYPE_THERMAL
data.generators.append(generator1)

generator2 = copy.copy(generator1)
generator2.number = 2
generator2.name = "G02"
generator2.bus = bus2
data.generators.append(generator2)

# Lines
line34_1 = psr.npf.Line()
line34_1.from_bus = bus3
line34_1.to_bus = bus4
line34_1.number = series_count
line34_1.name = "TL34-1"
line34_1.r_pct = 0.02
line34_1.x_pct = 0.40
data.lines.append(line34_1)
series_count += 1

line34_2 = copy.copy(line34_1)
line34_2.parallel_circuit_number = 2
line34_2.number = series_count
line34_2.name = "TL34-2"
data.lines.append(line34_2)
series_count += 1

line56 = psr.npf.Line()
line56.from_bus = bus5
line56.to_bus = bus6
line56.number = series_count
line56.name = "TL56"
line56.r_pct = 0.03
line56.x_pct = 0.60
data.lines.append(line56)
series_count += 1

# Line shunts
line56_shunt = psr.npf.LineShunt()
line56_shunt.number = 1
line56_shunt.name = "L56 shunt"
line56_shunt.circuit = line56
line56_shunt.terminal = psr.npf.LineShunt.TERMINAL_TO
line56_shunt.mvar = 60.0
data.line_shunts.append(line56_shunt)

# Two-winding transformer
trf67 = psr.npf.Transformer()
trf67.from_bus = bus6
trf67.to_bus = bus7
trf67.series_number = series_count
trf67.name = "TR67-SVC"
data.transformers.append(trf67)
series_count += 1


# Controlled Series Capacitor
csc = psr.npf.ControlledSeriesCapacitor()
csc.number = 1
csc.name = "CSC 4-5"
csc.from_bus = bus4
csc.to_bus = bus5
csc.xmin_pct = -20.0
csc.xmax_pct = -5.0
csc.nominal_rating = 300.0
csc.emergency_rating = 300.0
csc.series_number = series_count
data.cscs.append(csc)
series_count += 1

# Bus shunts
bshunt3 = psr.npf.BusShunt()
bshunt3.number = 1
bshunt3.name = "B03-cap"
bshunt3.bus = bus3
bshunt3.mvar = 50.0
bshunt3.type = psr.npf.BusShunt.CAPACITOR
bshunt3.ctr_bus = bus3
data.bus_shunts.append(bshunt3)

bshunt4 = copy.copy(bshunt3)
bshunt4.number = 2
bshunt4.name = "B04-cap"
bshunt4.bus = bus4
bshunt4.ctr_bus = bus4
data.bus_shunts.append(bshunt4)

# Static VAR compensator
svc = psr.npf.StaticVarCompensator()
svc.number = 1
svc.name = "SVC B07"
svc.bus = bus7
svc.ctr_bus = bus6
svc.droop = 5.0
svc.qmin = -20.0
svc.qmax = +20.0
data.svcs.append(svc)

# TODO: add missing components of the example.


print(data)
