import psr.npf
import copy


"""
Example network:

      1     3 AC Lines 4      5      6
 (G)--|-OO--|----------|--)|--|------|->
      2 |   |----------| 
 (G)--|-|   |          |->
            | DC Links |
       <-)|-|-[]----[]-|-|(->
            |-[]----[]-|
"""


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

bus2 = psr.npf.Bus()
bus2.number = 2
bus2.name = "Bus 2"
bus2.kvbase = 18.0
bus2.system = system
bus2.area = area1
bus2.region = region

bus3 = psr.npf.Bus()
bus3.number = 3
bus3.name = "Bus 3"
bus3.kvbase = 230.0
bus3.system = system
bus3.area = area2
bus3.region = region

bus4 = psr.npf.Bus()
bus4.number = 4
bus4.name = "Bus 4"
bus4.kvbase = 230.0
bus4.system = system
bus4.area = area2
bus4.region = region

bus5 = psr.npf.Bus()
bus5.number = 5
bus5.name = "Bus 5"
bus5.kvbase = 230.0
bus5.system = system
bus5.area = area2
bus5.region = region

bus6 = psr.npf.Bus()
bus6.number = 6
bus6.name = "Bus 6"
bus6.kvbase = 230.0
bus6.system = system
bus6.area = area2
bus6.region = region

data.buses.append(bus1)
data.buses.append(bus2)
data.buses.append(bus3)
data.buses.append(bus4)
data.buses.append(bus5)
data.buses.append(bus6)


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
line34_1.number = 1
line34_1.name = "TL34-1"
line34_1.r_pct = 0.02
line34_1.x_pct = 0.40
data.lines.append(line34_1)

line34_2 = copy.copy(line34_1)
line34_2.parallel_circuit_number = 2
line34_2.number = 2
line34_2.name = "TL34-2"
data.lines.append(line34_2)

line56 = psr.npf.Line()
line56.from_bus = bus5
line56.to_bus = bus6
line56.number = 3
line56.name = "TL56"
line56.r_pct = 0.03
line56.x_pct = 0.60
data.lines.append(line56)

# Line shunts
line56_shunt = psr.npf.LineShunt()
line56_shunt.number = 1
line56_shunt.name = "L56 shunt"
line56_shunt.circuit = line56
line56_shunt.terminal = psr.npf.LineShunt.TERMINAL_TO
line56_shunt.mvar = 60.0
data.line_shunts.append(line56_shunt)

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

# TODO: add missing components of the example.

print(data)
