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
data.description = "Case title"

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
area1.system = system
data.areas.append(area1)

area2 = psr.npf.Area()
area2.number = 2
area2.name = "Transmission Area"
area2.id = "ar02"
area2.system = system
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

# Three-winding transformer
# It's composed of three equivalent two-winding transformers and a
# middle point bus.
middle_bus = psr.npf.MiddlePointBus()
middle_bus.number = 8
middle_bus.name = "Midpoint"
middle_bus.kvbase = 1.0
middle_bus.system = system
middle_bus.area = area1
middle_bus.region = region
data.middlepoint_buses.append(middle_bus)

eqv_trf1 = psr.npf.EquivalentTransformer()
eqv_trf1.series_number = series_count
eqv_trf1.from_bus = bus1
eqv_trf1.to_bus = middle_bus
eqv_trf1.name = "eqvtr1"
data.equivalent_transformers.append(eqv_trf1)
series_count += 1

eqv_trf2 = psr.npf.EquivalentTransformer()
eqv_trf2.series_number = series_count
eqv_trf2.from_bus = bus2
eqv_trf2.to_bus = middle_bus
eqv_trf2.name = "eqvtr2"
data.equivalent_transformers.append(eqv_trf2)
series_count += 1

eqv_trf3 = psr.npf.EquivalentTransformer()
eqv_trf3.series_number = series_count
eqv_trf3.from_bus = bus3
eqv_trf3.to_bus = middle_bus
eqv_trf3.name = "eqvtr3"
data.equivalent_transformers.append(eqv_trf3)
series_count += 1

trf3 = psr.npf.ThreeWindingTransformer()
trf3.series_number = series_count
trf3.name = "TRF-GEN"
trf3.primary_transformer = eqv_trf1
trf3.secondary_transformer = eqv_trf2
trf3.tertiary_transformer = eqv_trf3
trf3.middlepoint_bus = middle_bus
data.three_winding_transformers.append(trf3)
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

# LCC DC Link components
lcc_link = psr.npf.DcLink()
lcc_link.number = 1
lcc_link.name = "LCC Link"
lcc_link.kvbase = 800.0
lcc_link.mwbase = 400.0
lcc_link.type = psr.npf.DcLink.TYPE_LCC
data.dclinks.append(lcc_link)

lcc_bus1 = psr.npf.DcBus()
lcc_bus1.number = 1
lcc_bus1.name = "DCB 1"
lcc_bus1.region = region
lcc_bus1.system = system
lcc_bus1.area = area2
lcc_bus1.dclink = lcc_link
data.dcbuses.append(lcc_bus1)

lcc_bus2 = copy.copy(lcc_bus1)
lcc_bus2.number = 2
lcc_bus2.name = "DCB 2"
data.dcbuses.append(lcc_bus2)

lcc_bus3 = copy.copy(lcc_bus1)
lcc_bus3.number = 3
lcc_bus3.name = "DCB 3N"
lcc_bus3.volt = 0.0
lcc_bus3.polarity = psr.npf.DcBus.POLARITY_NEUTRAL
data.dcbuses.append(lcc_bus3)

lcc_bus4 = copy.copy(lcc_bus3)
lcc_bus4.number = 4
lcc_bus4.name = "DCB 4N"
data.dcbuses.append(lcc_bus4)

lcc_line = psr.npf.DcLine()
lcc_line.number = 1
lcc_line.name = "DC Line 1-2"
lcc_line.from_bus = lcc_bus1
lcc_line.to_bus = lcc_bus2
lcc_line.r_ohm = 10.0
lcc_line.series_number = series_count
data.dclines.append(lcc_line)
series_count += 1

lcc_cnv_ret = psr.npf.AcDcConverterLcc()
lcc_cnv_ret.number = 1
lcc_cnv_ret.name = "LCC RET"
lcc_cnv_ret.ac_bus = bus3
lcc_cnv_ret.dc_bus = lcc_bus1
lcc_cnv_ret.neutral_bus = lcc_bus3
lcc_cnv_ret.type = psr.npf.AcDcConverterLcc.TYPE_RETIFIER
data.lcc_converters.append(lcc_cnv_ret)

lcc_cnv_inv = psr.npf.AcDcConverterLcc()
lcc_cnv_inv.number = 2
lcc_cnv_inv.name = "LCC INV"
lcc_cnv_inv.ac_bus = bus4
lcc_cnv_inv.dc_bus = lcc_bus2
lcc_cnv_inv.neutral_bus = lcc_bus4
lcc_cnv_inv.type = psr.npf.AcDcConverterLcc.TYPE_INVERTER
data.lcc_converters.append(lcc_cnv_inv)

# VSC DC Link components
vsc_link = psr.npf.DcLink()
vsc_link.number = 2
vsc_link.name = "VSC Link"
vsc_link.kvbase = 400.0
vsc_link.mwbase = 200.0
vsc_link.type = psr.npf.DcLink.TYPE_VSC
data.dclinks.append(vsc_link)

vsc_bus5 = psr.npf.DcBus()
vsc_bus5.number = 5
vsc_bus5.name = "DCB 5"
vsc_bus5.region = region
vsc_bus5.system = system
vsc_bus5.area = area2
vsc_bus5.dclink = vsc_link
data.dcbuses.append(vsc_bus5)

vsc_bus6 = copy.copy(vsc_bus5)
vsc_bus6.number = 6
vsc_bus6.name = "DCB 6"
data.dcbuses.append(vsc_bus6)

vsc_bus7 = copy.copy(vsc_bus5)
vsc_bus7.number = 7
vsc_bus7.name = "DCB 7N"
vsc_bus7.volt = 0.0
vsc_bus7.polarity = psr.npf.DcBus.POLARITY_NEUTRAL
data.dcbuses.append(vsc_bus7)

vsc_bus8 = copy.copy(vsc_bus5)
vsc_bus8.number = 8
vsc_bus8.name = "DCB 8N"
data.dcbuses.append(vsc_bus8)

vsc_line = psr.npf.DcLine()
vsc_line.number = 2
vsc_line.name = "DC Line 5-6"
vsc_line.from_bus = vsc_bus5
vsc_line.to_bus = vsc_bus6
vsc_line.r_ohm = 10.0
vsc_line.series_number = series_count
data.dclines.append(vsc_line)
series_count += 1

vsc_cnv_ret = psr.npf.AcDcConverterVsc()
vsc_cnv_ret.number = 3
vsc_cnv_ret.name = "VSC RET"
vsc_cnv_ret.ac_bus = bus3
vsc_cnv_ret.dc_bus = vsc_bus5
vsc_cnv_ret.neutral_bus = vsc_bus7
vsc_cnv_ret.ctr_bus = bus3
data.vsc_converters.append(vsc_cnv_ret)

vsc_cnv_inv = psr.npf.AcDcConverterVsc()
vsc_cnv_inv.number = 4
vsc_cnv_inv.name = "VSC INV"
vsc_cnv_inv.ac_bus = bus4
vsc_cnv_inv.dc_bus = vsc_bus6
vsc_cnv_inv.neutral_bus = vsc_bus8
vsc_cnv_inv.ctr_bus = bus4
data.vsc_converters.append(vsc_cnv_inv)


print(data)
