import psr.npf

data = psr.npf.NpFile()
data.revision = 1
data.titu = "Case title"
data.buses.append(psr.npf.Bus())
data.buses.append(psr.npf.Bus())
data.middlepoint_buses.append(psr.npf.Bus())
data.areas.append(psr.npf.Area())
data.regions.append(psr.npf.Region())
data.systems.append(psr.npf.System())
data.demands.append(psr.npf.Demand())
data.generators.append(psr.npf.Generator())
data.bus_shunts.append(psr.npf.BusShunt())
data.lines.append(psr.npf.Line())
data.line_shunts.append(psr.npf.LineShunt())
data.transformers.append(psr.npf.Transformer())
data.equivalent_transformers.append(psr.npf.Transformer())
data.equivalent_transformers.append(psr.npf.Transformer())
data.equivalent_transformers.append(psr.npf.Transformer())
data.three_winding_transformers.append(psr.npf.ThreeWindingTransformer())
data.cscs.append(psr.npf.ControlledSeriesCapacitor())
data.svcs.append(psr.npf.StaticVarCompensator())

print(data)
