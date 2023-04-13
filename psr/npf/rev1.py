import datetime


# Default MVA/MW base.
MVABASE = 100.0

# Default kV base.
KVBASE = 1.0

# Default frequency (Hz) base.
HZBASE = 50

# Add operation.
OP_ADD = "A"
# Modify operation.
OP_MOD = "M"
# Remove operation.
OP_REM = "R"

# Registry condition.
CND_REGISTRY = "R"
# Planned condition.
CND_PLANNED = "P"

# Circuit metering end on "from" bus.
METERING_END_FROM = "F"
# Circuit metering end on "to" bus.
METERING_END_TO = "T"

# Default date
DEFAULT_DATE = "1900/01/01"

# now.strftime("%m/%d/%Y, %H:%M:%S")
DATE_FORMAT = "%Y/%m/%d"

# Status on value.
STATUS_ON = 1
# Status off value.
STATUS_OFF = 0

# Absolute maximum value of circuit flow.
FLOW_MAX = 9999.0


def to_date_str(date):
    # type: (datetime.datetime) -> str
    """Convert a datetime object into NetPlan's date string format."""
    return date.strftime(DATE_FORMAT)


class StarpointFile:
    header = "(BusF) (...Name...) (BusT) (...Name...)"

    def __init__(self):
        self.starpoints = []

    def __str__(self):
        contents = [StarpointFile.header, ]
        for starpoint in self.starpoints:
            contents.append("{:6d} {:12s} {:6d} {:12s}".format(
                starpoint.bus_from, starpoint.bus_from_name,
                starpoint.bus_to, starpoint.bus_to_name
            ))
        return "\n".join(contents)


class Starpoint:
    def __init__(self):
        self.bus_from = 0
        self.bus_from_name = ""
        self.bus_to = 0
        self.bus_to_name = ""


class NpFile:
    """Represents a study stage/block data."""
    def __init__(self):

        # File format revision number.
        self.revision = 1

        # Case title/description.
        self.description = ""
        self.buses = []
        # Buses that represents the fictitious middle point of
        #  three-winding transformers.
        self.middlepoint_buses = []
        self.areas = []
        self.regions = []
        self.systems = []
        self.demands = []
        self.generators = []
        self.bus_shunts = []
        self.lines = []
        self.line_shunts = []
        self.transformers = []
        self.equivalent_transformers = []
        self.three_winding_transformers = []
        # Controlled series capacitors.
        self.cscs = []
        # Static VAR compensators.
        self.svcs = []
        self.dclinks = []
        self.dcbuses = []
        self.dclines = []
        self.lcc_converters = []
        self.vsc_converters = []

    def _append_elements(self, contents, header, comment, elements):
        # type: (list, str, str, list) -> None
        contents.append(header)
        contents.append(comment)
        for element in elements:
            contents.append(str(element))
        contents.append("END\n")

    def __str__(self):
        contents = ["NPF_REVISION", str(self.revision),
                    "DESCRIPTION", self.title, ]

        header_elements_pairs = (
            (Bus.header, Bus.comment, self.buses),
            (MiddlePointBus.header, MiddlePointBus.comment,
             self.middlepoint_buses),
            (Area.header, Area.comment, self.areas),
            (Region.header, Region.comment, self.regions),
            (System.header, System.comment, self.systems),
            (Demand.header, Demand.comment, self.demands),
            (Generator.header, Generator.comment, self.generators),
            (BusShunt.header, BusShunt.comment, self.bus_shunts),
            (Line.header, Line.comment, self.lines),
            (LineShunt.header, LineShunt.comment, self.line_shunts),
            (Transformer.header, Transformer.comment, self.transformers),
            (EquivalentTransformer.header, EquivalentTransformer.comment,
             self.equivalent_transformers),
            (ThreeWindingTransformer.header, ThreeWindingTransformer.comment,
             self.three_winding_transformers),
            (ControlledSeriesCapacitor.header,
             ControlledSeriesCapacitor.comment, self.cscs),
            (StaticVarCompensator.header, StaticVarCompensator.comment,
             self.svcs),
            (DcLink.header, DcLink.comment, self.dclinks),
            (DcBus.header, DcBus.comment, self.dcbuses),
            (DcLine.header, DcLine.comment, self.dclines),
            (AcDcConverterLcc.header, AcDcConverterLcc.comment,
             self.lcc_converters),
            (AcDcConverterVsc.header, AcDcConverterVsc.comment,
             self.vsc_converters),
        )

        for header, comment, elements in header_elements_pairs:
            self._append_elements(contents, header, comment, elements)

        return "\n".join(contents)


def _to_str(value):
    if isinstance(value, str):
        return "".join(["\"", value, "\""])
    return str(value)


class RecordType(object):
    header = ""
    comment = ""

    def __init__(self):
        pass

    def __str__(self):
        values = []
        for var, value in vars(self).items():
            if var != "header" and var != "comment":
                # TODO: values that are string already should be escaped with
                #  quotes.
                values.append(_to_str(value))
        return ",".join(values)

    def __repr__(self):
        return self.__str__()


class System(RecordType):
    """System data."""
    header = "SYSTEM"
    comment = "# \"ID\",\"[.......Name.......]\",System#"

    def __init__(self):
        super(System, self).__init__()
        # Two-characters system unique identifier.
        self.id = ""
        # 12-characters system unique name.
        self.name = ""
        # Unique system number.
        self.number = 0

    def __str__(self):
        args = [self.id, self.name, self.number, ]
        return "  \"{:2s}\",\"{:20s}\",{:2d}".format(*args)


class Region(RecordType):
    """Region data."""
    header = "REGION"
    comment = "# \"[ID]\",\"[........Name......]\",Region#,System#,\"SystemID\""

    def __init__(self):
        super(Region, self).__init__()
        # Two-characters unique region identifier.
        self.id = ""
        # 12-characters unique region name.
        self.name = ""
        # Region unique number
        self.number = 0
        # System the region is part of.
        self.system = None

    def __str__(self):
        system_number = self.system.number if self.system is not None else 0
        system_id = self.system.id if self.system is not None else ""
        args = [self.id, self.name, self.number, system_number,
                system_id]
        return "  \"{:4s}\",\"{:12s}\",{:2d},{:2d},\"{:2s}\"".format(*args)


class Area(RecordType):
    """Area data."""
    header = "AREA"
    comment = \
        "# \"[ID]\",\"[.............Area Name............]\",Area#," \
        "System#,\"SystemID\""

    def __init__(self):
        super(Area, self).__init__()
        # 4-characters unique area identifier.
        self.id = ""
        # 36-characters unique area name.
        self.name = ""
        # Unique area number.
        self.number = 0
        # System the region is part of.
        self.system = None

    def __str__(self):
        system_number = self.system.number if self.system is not None else 0
        system_id = self.system.id if self.system is not None else ""
        args = [self.id, self.name, self.number, system_number,
                system_id]
        return "  \"{:4s}\",\"{:36s}\",{:4d},{:2d},\"{:2s}\"".format(*args)


class Bus(RecordType):
    """Bus data."""
    header = "BUS"
    comment = "# Bus#,\"[...Name...]\",\"Op\",[.kV.],Area#,Region#,System#," \
              "\"[..Date..]\",\"Cnd\",Cost,Type,LoadShed,Volt,Angle,Vmax," \
              "Vmin,EVmax,EVmin,Stt,\"[....Extended Name.....]\""

    def __init__(self):
        super(Bus, self).__init__()
        self.number = 0
        self.name = ""
        self.op = OP_ADD
        self.kvbase = 1.0
        self.area = None
        self.region = None
        self.system = None
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.cost = 0
        self.type = 0
        self.loadshed = 0
        self.volt = 1.0
        self.angle = 0.0
        self.vmax = 1.2
        self.vmin = 0.8
        self.evmax = 1.2
        self.evmin = 0.8
        self.stt = STATUS_ON
        self.extended_name = ""

    def __str__(self):
        system_number = self.system.number if self.system is not None else 0
        area_number = self.area.number if self.area is not None else 0
        region_number = self.region.number if self.region is not None else 0
        args = [self.number, self.name, self.op, self.kvbase, area_number,
                region_number, system_number, self.date, self.cnd,
                self.cost, self.type, self.loadshed, self.volt, self.angle,
                self.vmax, self.vmin, self.evmax, self.evmin, self.stt,
                self.extended_name]
        return "{:6d},\"{:12s}\",\"{:1s}\",{:8.2f},{:2d},{:2d},{:2d}," \
               "\"{:10s}\",\"{:1s}\",{:7.2f},{:1d},{:1d},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:1d},\"{:12s}\"".format(*args)


class MiddlePointBus(Bus):
    header = "MIDDLEPOINT_BUS"
    comment = Bus.comment

    def __init__(self):
        super(MiddlePointBus, self).__init__()


class Demand(RecordType):
    """Demand per bus (load) data."""
    header = "DEMAND"
    comment = "# Demand#,\"[...Name...]\",\"Op\",Bus#,\"[.Bus Name.]\"," \
              "Units,\"[..Date..]\",\"Cnd\",P_MW,Q_MW"

    def __init__(self):
        super(Demand, self).__init__()
        self.number = 0
        self.name = ""
        self.op = OP_ADD
        self.bus = None
        self.units = 1
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.p_mw = 0.0
        self.q_mw = 0.0

    def __str__(self):
        bus_number = self.bus.number if self.bus is not None else 0
        bus_name = self.bus.name if self.bus is not None else ""
        args = [self.number, self.name, self.op,
                bus_number, bus_name, self.units, self.date,
                self.cnd, self.p_mw, self.q_mw]
        return "  {:7d},\"{:12s}\",\"{:1s}\",{:5d},\"{:12s}\",{:5d}," \
               "\"{:10s}\",\"{:1s}\",{:8.3f},{:8.3f}".format(*args)


class Generator(RecordType):
    """Generator data."""
    header = "GENERATOR"
    comment = "# Gen#,\"[...Name...]\",\"Op\",Bus#,\"[.Bus Name.]\",\"Type\"," \
              "Units,Pmin,Pmax,Qmin,Qmax,\"[..Date..]\",\"C\"," \
              "CtrBus#,\"[CtrBusName]\",CtrType,Factor,UnitsOn,Pgen,Qgen"

    TYPE_HYDRO = "H"
    TYPE_THERMAL = "T"
    TYPE_RENEWABLE = "R"

    def __init__(self):
        super(Generator, self).__init__()
        self.number = 0
        self.name = ""
        self.op = OP_ADD
        self.bus = None
        # Generator type: (H)ydro, (T)hermal, (R)enewable.
        self.type = Generator.TYPE_THERMAL
        self.units = 1
        self.pmin = 0
        self.pmax = 0
        self.qmin = 0
        self.qmax = 0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.ctr_bus = None
        self.ctr_type = 0
        self.factor = 0.0
        self.units_on = 1
        self.pgen = 0.0
        self.qgen = 0.0

    def __str__(self):
        bus_number = self.bus.number if self.bus is not None else 0
        bus_name = self.bus.name if self.bus is not None else ""
        ctr_bus_number = self.ctr_bus.number if self.ctr_bus is not None else 0
        ctr_bus_name = self.ctr_bus.name if self.ctr_bus is not None else ""
        args = [self.number, self.name, self.op, bus_number, bus_name,
                self.type, self.units, self.pmin, self.pmax,
                self.qmin, self.qmax, self.date, self.cnd,
                ctr_bus_number, ctr_bus_name, self.ctr_type,
                self.factor, self.units_on, self.pgen, self.qgen]
        return "{:6d},\"{:12s}\",\"{:1s}\",{:6d},\"{:12s}\"," \
               "\"{:1s}\",{:3d},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "\"{:10s}\",\"{:1s}\",{:6d},\"{:12s}\",{:1d}," \
               "{:8.3f},{:3d},{:8.3f},{:8.3f}".format(*args)


class Line(RecordType):
    """Line data."""
    header = "LINE"
    comment = "# FromBus#,ToBus#,ParallelCirc#,Op,MetEnd,R%,X%,MVAr," \
              "NomRating,EmgRating,PF,Cost,\"[..Date..]\",\"Cnd\",Serie#," \
              "Type,\"[...Name...]\",Env,LengthKm," \
              "Stt,\"[....Extended Name.....]\""

    def __init__(self):
        super(Line, self).__init__()
        self.from_bus = None
        self.to_bus = None
        self.parallel_circuit_number = 1
        self.op = OP_ADD
        # Metering end: (F)rom or (T)o bus.
        self.metering_end = METERING_END_FROM
        self.r_pct = 0.0
        self.x_pct = 0.0
        self.mvar = 0.0
        self.nominal_rating = FLOW_MAX
        self.emergency_rating = FLOW_MAX
        self.power_factor = 0.0
        self.cost = 0.0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.number = 0
        # circuit type
        # TODO: create enumeration for different types.
        self.type = 0
        self.name = ""
        # environment factor (0/1)
        self.env_factor = 0
        self.length_km = 0
        self.stt = STATUS_ON
        self.extended_name = ""

    def __str__(self):
        from_bus_number = self.from_bus.number \
            if self.from_bus is not None else 0
        to_bus_number = self.to_bus.number if self.to_bus is not None else 0
        args = [from_bus_number, to_bus_number,
                self.parallel_circuit_number, self.op, self.metering_end,
                self.r_pct, self.x_pct, self.mvar, self.nominal_rating,
                self.emergency_rating, self.power_factor, self.cost,
                self.date, self.cnd, self.number, self.type, self.name,
                self.env_factor, self.length_km, self.stt, self.extended_name
                ]
        return "{:6d},{:6d},{:3d},\"{:1s}\",\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},\"{:10s}\",\"{:1s}\",{:6d}," \
               "{:1d},\"{:12s}\",{:1d},{:8.3f},{:1d},\"{:12s}\"".format(*args)


class BusShunt(RecordType):
    """Bus shunt data."""
    header = "BUS_SHUNT"
    comment = "# Shunt#,\"[...Name...]\",\"Op\",Bus#,\"[.Bus Name.]\"," \
              "CtrBus#,\"[.Ctr Name.]\",\"T\",CtrType,Units,MVAr,Cost," \
              "\"[..Date..]\",\"Cnd\",UnitsOn"

    REACTOR = "R"
    CAPACITOR = "C"

    def __init__(self):
        super(BusShunt, self).__init__()
        self.number = 0
        self.name = ""
        self.op = OP_ADD
        self.bus = None
        self.ctr_bus = None
        self.type = BusShunt.REACTOR
        # TODO: create enumeration for control types.
        self.ctr_type = 0
        self.units = 1
        self.mvar = 0.0
        self.cost = 0.0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.units_on = 1

    def __str__(self):
        bus_number = self.bus.number if self.bus is not None else 0
        bus_name = self.bus.name if self.bus is not None else ""
        ctr_bus_number = self.ctr_bus.number if self.ctr_bus is not None else 0
        ctr_bus_name = self.ctr_bus.name if self.ctr_bus is not None else ""
        args = [self.number, self.name, self.op,
                bus_number, bus_name,
                ctr_bus_number, ctr_bus_name,
                self.type, self.ctr_type, self.units, self.mvar, self.cost,
                self.date, self.cnd, self.units_on,
                ]
        return "{:6d},\"{:12s}\",\"{:1s}\",{:6d},\"{:12s}\"," \
               "{:6d},\"{:12s}\",\"{:1s}\",{:1d},{:3d},{:8.3f}," \
               "{:8.3f},\"{:10s}\",\"{:1s}\",{:1d}".format(*args)


class LineShunt(RecordType):
    """Line shunt data."""
    header = "LINE_SHUNT"
    comment = "# Shunt#,\"[...Name...]\",\"Op\"," \
              "FromBus#,ToBus#,ParallelCirc#,MVAr,Term,Cost," \
              "\"[..Date..]\",\"Cnd\",Stt,Series#"
    TERMINAL_FROM = "F"
    TERMINAL_TO = "T"

    def __init__(self):
        super(LineShunt, self).__init__()
        self.number = 0
        self.name = ""
        self.op = OP_ADD
        self.circuit = None
        self.mvar = 0.0
        # Connection terminal: (F)rom bus or (T)o bus.
        self.terminal = LineShunt.TERMINAL_FROM
        # Cost per unit in k$.
        self.cost = 0.0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.stt = STATUS_ON

    def __str__(self):
        circ_from_number = self.circuit.from_bus.number \
            if self.circuit is not None else ""
        circ_to_number = self.circuit.to_bus.number \
            if self.circuit is not None else 0
        circ_number = self.circuit.number if self.circuit is not None else 0
        circ_parallel = self.circuit.parallel_circuit_number\
            if self.circuit is not None else 0
        args = [self.number, self.name, self.op,
                circ_from_number, circ_to_number,
                circ_parallel, self.mvar, self.terminal, self.cost,
                self.date, self.cnd, self.stt, circ_number]
        return "{:6d},\"{:12s}\",\"{:1s}\",{:6d},{:6d},{:2d},{:8.3f}," \
               "\"{:1s}\",{:8.3f},\"{:10s}\",\"{:1s}\"," \
               "{:1d},{:3d}".format(*args)


class Transformer(RecordType):
    """Two-winding transformer data."""
    header = "TRANSFORMER"
    comment = "# FromBus#,ToBus#,ParallelCirc#,\"Op\",\"MetEnd\",R%,X%," \
              "TapMin,TapMax,PhaseMin,PhaseMax,ControlType,CtrBus,TapSteps," \
              "NomRating,EmgRating,PF,Cost,\"[..Date..]\",\"Cnd\",Series#," \
              "\"[...Name...]\",Env,\"[...Extended Name...]\",Stt,Tap,Phase," \
              "MinFlow,MaxFlow,EmgMinFlow,EmgMaxFlow"

    def __init__(self):
        super(Transformer, self).__init__()
        self.from_bus = None
        self.to_bus = None
        self.parallel_circuit_number = 1
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
        self.r_pct = 0
        self.x_pct = 0
        self.tap_min = 0.8
        self.tap_max = 1.2
        self.phase_min = 0.0
        self.phase_max = 0.0
        self.control_type = 0
        self.ctr_bus = None
        self.tap_steps = 20
        self.nominal_rating = FLOW_MAX
        self.emergency_rating = FLOW_MAX
        self.power_factor = 0
        self.cost = 0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.series_number = 0
        self.name = ""
        self.env = 0
        self.extended_name = ""
        self.stt = STATUS_ON
        self.tap = 1.0
        self.phase = 0.0
        self.minflow = -FLOW_MAX
        self.maxflow = +FLOW_MAX
        self.emergency_minflow = -FLOW_MAX
        self.emergency_maxflow = +FLOW_MAX

    def __str__(self):
        from_bus_number = self.from_bus.number \
            if self.from_bus is not None else 0
        to_bus_number = self.to_bus.number \
            if self.to_bus is not None else 0
        ctr_bus_number = self.ctr_bus.number \
            if self.ctr_bus is not None else 0
        args = [from_bus_number, to_bus_number,
                self.parallel_circuit_number, self.op, self.metering_end,
                self.r_pct, self.x_pct, self.tap_min, self.tap_max,
                self.phase_min, self.phase_max, self.control_type,
                ctr_bus_number, self.tap_steps, self.nominal_rating,
                self.emergency_rating, self.power_factor, self.cost,
                self.date, self.cnd, self.series_number, self.name, self.env,
                self.extended_name, self.stt, self.tap, self.phase,
                self.minflow, self.maxflow, self.emergency_minflow,
                self.emergency_maxflow, ]
        return "{:6d},{:6d},{:3d},\"{:1s}\",\"{:1s}\",{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:1d},{:6d},{:3d}," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},\"{:10s}\",\"{:1s}\"," \
               "{:6d},\"{:12s}\",{:1d},\"{:12s}\",{:1d}," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f}".format(*args)


class EquivalentTransformer(Transformer):
    header = "EQUIVALENT_TRANSFORMER"
    comment = Transformer.comment

    def __init__(self):
        super(EquivalentTransformer, self).__init__()


class ThreeWindingTransformer(RecordType):
    """Three-winding transformer data."""
    header = "THREE_WINDING_TRANSFORMER"
    comment = "# PrimaryBus#,SecondaryBus#,TertiaryBus#,MiddlePointBus#," \
              "ParallelCirc#,\"Op\",\"MetEnd\",RPS%,XPS%,SbPS," \
              "RST%,XST%,SbST,RPT%,XPT%,SbPT,PF,Cost,\"[..Date..]\",\"Cnd\"," \
              "Series#,\"PriEqvTrfName\",\"SecEqvTrfName\"," \
              "\"TerEqvTrfname\",\"[...Name...]\",\"[...Extended Name...]\""

    def __init__(self):
        super(ThreeWindingTransformer, self).__init__()
        self.primary_bus_number = 0
        self.secondary_bus_number = 0
        self.tertiary_bus_number = 0
        self.middlepoint_bus_number = 0
        self.parallel_circuit_number = 0
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
        self.rps_pct = 0
        self.xps_pct = 0
        self.sbaseps_mva = 0
        self.rst_pct = 0
        self.xst_pct = 0
        self.sbasest_mva = 0
        self.rpt_pct = 0
        self.xpt_pct = 0
        self.sbasept_mva = 0
        self.power_factor = 0
        self.cost = 0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.series_number = 0
        self.pritrf_name = ""
        self.sectrf_name = ""
        self.tertrf_name = ""
        self.name = ""
        self.extended_name = ""

    def __str__(self):
        args = [self.primary_bus_number, self.secondary_bus_number,
                self.tertiary_bus_number, self.middlepoint_bus_number,
                self.parallel_circuit_number, self.op, self.metering_end,
                self.rps_pct, self.xps_pct, self.sbaseps_mva,
                self.rst_pct, self.xps_pct, self.sbaseps_mva,
                self.rpt_pct, self.xpt_pct, self.sbasept_mva,
                self.power_factor, self.cost, self.date, self.cnd,
                self.series_number, self.pritrf_name, self.sectrf_name,
                self.tertrf_name, self.name, self.extended_name]
        return "{:6d},{:6d},{:6d},{:6d},{:2d},\"{:1s}\",\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "\"{:10s}\",\"{:1s}\",{:6d}," \
               "\"{:12s}\",\"{:12s}\",\"{:12s}\"," \
               "\"{:12s}\",\"{:12s}\",".format(*args)


class ControlledSeriesCapacitor(RecordType):
    header = "CSC"
    comment = "# FromBus#,ToBus#,ParallelCirc#,\"Op\",\"MetEnd\",Xmin%,Xmax%," \
              "NomRating,EmgRating,PF,Cost,\"[..Date..]\",\"Cnd\"," \
              "Series#,\"[...Name...]\",\"CM\",\"M\",Stt,Bypass,Setpoint"

    def __init__(self):
        super(ControlledSeriesCapacitor, self).__init__()
        self.from_bus = None
        self.to_bus = None
        self.parallel_circuit_number = 1
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
        self.xmin_pct = 0.0
        self.xmax_pct = 0.0
        self.nominal_rating = FLOW_MAX
        self.emergency_rating = FLOW_MAX
        self.power_factor = 0.0
        self.cost = 0.0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.series_number = 0
        self.name = ""
        self.control_mode = ""
        self.stt = STATUS_ON
        self.bypass = STATUS_OFF
        self.setpoint = 0.0

    def __str__(self):
        from_bus_number = self.from_bus.number if self.from_bus is not None else 0
        to_bus_number = self.to_bus.number if self.to_bus is not None else 0

        args = [
            from_bus_number, to_bus_number,
            self.parallel_circuit_number, self.op, self.metering_end,
            self.xmin_pct, self.xmax_pct,
            self.nominal_rating, self.emergency_rating,
            self.power_factor, self.cost, self.date, self.cnd,
            self.series_number, self.name, self.control_mode, self.stt,
            self.bypass, self.setpoint
        ]
        return "{:6d},{:6d},{:3d},\"{:1s}\",\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "\"{:10s}\",\"{:1s}\",{:6d},\"{:12s}\",\"{:1s}\",{:1d}," \
               "{:1d},{:8.3f}".format(*args)


class StaticVarCompensator(RecordType):
    """Static var compensator data."""
    header = "SVC"
    comment = "# SVC#,\"[...Name...]\",\"Op\",Bus#,\"[.Bus Name.]\",CtrBus," \
              "\"[.Ctr Name.]\",Droop,CtrMode,Units,Qmin,Qmax,Cost," \
              "\"[..Date..]\",\"Cnd\",Stt,SetMVAR"

    def __init__(self):
        super(StaticVarCompensator, self).__init__()
        self.number = 0
        self.name = ""
        self.op = OP_ADD
        self.bus = None
        self.ctr_bus = None
        self.droop = 0.0
        self.ctr_mode = 0
        self.units = 1
        self.qmin = 0
        self.qmax = 0
        self.cost = 0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.stt = STATUS_ON
        self.mvar_setpoint = 0

    def __str__(self):
        bus_number = self.bus.number if self.bus is not None else 0
        bus_name = self.bus.name if self.bus is not None else ""
        ctr_bus_number = self.ctr_bus.number if self.ctr_bus is not None else 0
        ctr_bus_name = self.ctr_bus.name if self.ctr_bus is not None else ""
        args = [self.number, self.name, self.op, bus_number,
                bus_name, ctr_bus_number, ctr_bus_name,
                self.droop, self.ctr_mode, self.units, self.qmin, self.qmax,
                self.cost, self.date, self.cnd, self.stt, self.mvar_setpoint]
        return "{:6d},\"{:12s}\",\"{:1s}\",{:6d},\"{:12s}\"," \
               "{:6d},\"{:12s}\",{:8.3f},{:3d},{:3d},{:8.3f},{:8.3f}," \
               "{:8.2f},\"{:10s}\",\"{:1s}\",{:1d},{:8.3f}".format(*args)


class DcLink(RecordType):
    header = "DC_LINK"
    comment = "# Link#,\"[...Name...]\",kVbase,MWbase,\"Type\""

    TYPE_LCC = "LCC"
    TYPE_VSC = "VSC"

    def __init__(self):
        super(DcLink, self).__init__()
        self.number = 0
        self.name = ""
        self.kvbase = KVBASE
        self.mwbase = MVABASE
        self.type = DcLink.TYPE_LCC

    def __str__(self):
        args = [self.number, self.name,
                self.kvbase, self.mwbase, self.type]
        return "{:4d},\"{:12s}\",{:8.3f},{:8.3f},\"{:3s}\"".format(*args)


class DcBus(RecordType):
    header = "DC_BUS"
    comment = "# Bus#,\"[...Name...]\",\"Op\",Type,Polarity,GroundR," \
              "Area#,Region#,System#,DcLink#," \
              "\"[..Date..]\",\"Cnd\",Cost,Volt"

    POLARITY_POSITIVE = "+"
    POLARITY_NEGATIVE = "-"
    POLARITY_NEUTRAL = "0"

    def __init__(self):
        super(DcBus, self).__init__()
        self.number = 0
        self.name = ""
        self.op = OP_ADD
        self.type = 0
        self.polarity = DcBus.POLARITY_POSITIVE
        self.groundr = 0.0
        self.area = None
        self.region = None
        self.system = None
        self.dclink = None
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.cost = 0.0
        self.volt = 1.0

    def __str__(self):
        area_number = self.area.number if self.area is not None else 0
        region_number = self.region.number if self.region is not None else 0
        system_number = self.system.number if self.system is not None else 0
        dclink_number = self.dclink.number if self.dclink is not None else 0
        args = [self.number, self.name, self.op,
                self.type, self.polarity, self.groundr,
                area_number, region_number, system_number,
                dclink_number, self.date, self.cnd, self.cost, self.volt]
        return "{:6d},\"{:12s}\",\"{:1s}\",{:1d},\"{:1s}\"," \
               "{:8.3f},{:4d},{:4d},{:4d},{:4d},\"{:10s}\"," \
               "\"{:1s}\",{:8.3f},{:8.3f}".format(*args)


class DcLine(RecordType):
    header = "DC_LINE"
    comment = "# FromBus#,ToBus#,ParallelCirc#,\"Op\",\"MetEnd\",R_Ohm,L_Ohm," \
              "NominalRating,Cost,Date,Cnd,Series#," \
              "\"[.........Name.........]\",Stt"

    def __init__(self):
        super(DcLine, self).__init__()
        self.from_bus = None
        self.to_bus = None
        self.parallel_circuit_number = 1
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
        self.r_ohm = 0.0
        self.l_ohm = 0.0
        self.nominal_rating = FLOW_MAX
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.series_number = 0
        self.name = ""
        self.stt = STATUS_ON

    def __str__(self):
        from_bus_number = self.from_bus.number if self.from_bus is not None else 0
        to_bus_number = self.to_bus.number if self.to_bus is not None else 0
        args = [from_bus_number, to_bus_number,
                self.parallel_circuit_number, self.op, self.metering_end,
                self.r_ohm, self.l_ohm, self.nominal_rating, self.date,
                self.cnd, self.series_number, self.name, self.stt]
        return "{:6d},{:6d},{:3d},\"{:1s}\",\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f},\"{:10s}\"," \
               "\"{:1s}\",{:6d},\"{:24s}\",{:1d}".format(*args)


class AcDcConverterLcc(RecordType):
    header = "ACDC_CONVERTER_LCC"
    comment = "# Cnv#,\"Op\",\"MetEnd\",AcBus#,DcBus#,NeutralBus#,\"Type\"," \
              "Inom,Bridges,Xc,Vfs,Snom,Tmin,Tmax,Steps,Mode," \
              "FlowAcDc,FlowDcAc," \
              "FirR,FirRmin,FirRmax,FirI,FirImin,FirImax,CCCC,Cost," \
              "\"[..Date..]\",\"Cnd\",\"[...Name...]\",Hz,Stt,Tap,Setpoint"

    TYPE_RETIFIER = "R"
    TYPE_INVERTER = "I"
    TYPE_BIDIRECTIONAL = "B"

    def __init__(self):
        super(AcDcConverterLcc, self).__init__()
        self.number = 0
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
        self.ac_bus = None
        self.dc_bus = None
        self.neutral_bus = None
        # Type: (R)etifier or (I)nverter
        self.type = AcDcConverterLcc.TYPE_RETIFIER
        self.nominal_current = 0.0
        self.bridges = 2
        self.xc = 0.0
        self.vfs = 0.0
        self.nominal_power = 0.0
        self.tap_min = 0.8
        self.tap_max = 1.2
        self.tap_steps = 100
        self.control_mode = "P"
        self.flow_ac_dc = FLOW_MAX
        self.flow_dc_ac = FLOW_MAX
        self.firing_angle_retifier_set = 0.0
        self.firing_angle_retifier_min = 0.0
        self.firing_angle_retifier_max = 0.0
        self.firing_angle_inverter_set = 0.0
        self.firing_angle_inverter_min = 0.0
        self.firing_angle_inverter_max = 0.0
        self.ccc_capacitance = 0.0
        self.cost = 0.0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.name = ""
        self.hzbase = HZBASE
        self.stt = STATUS_ON
        self.tap = 1.0
        self.setpoint = 0.0

    def __str__(self):
        ac_bus_number = self.ac_bus.number if self.ac_bus is not None else 0
        dc_bus_number = self.dc_bus.number if self.dc_bus is not None else 0
        neutral_bus_number = self.neutral_bus.number \
            if self.neutral_bus is not None else 0
        args = [self.number, self.op, self.metering_end,
                ac_bus_number, dc_bus_number, neutral_bus_number,
                self.type, self.nominal_current, self.bridges, self.xc,
                self.vfs, self.nominal_power,
                self.tap_min, self.tap_max, self.tap_steps,
                self.control_mode, self.flow_ac_dc, self.flow_dc_ac,
                self.firing_angle_retifier_set, self.firing_angle_retifier_min,
                self.firing_angle_retifier_max, self.firing_angle_inverter_set,
                self.firing_angle_inverter_min, self.firing_angle_inverter_max,
                self.ccc_capacitance, self.cost, self.date, self.cnd,
                self.name, self.hzbase, self.stt, self.tap, self.setpoint, ]
        return "{:6d},\"{:1s}\",\"{:1s}\",{:6d},{:6d},{:6d}," \
               "\"{:1s}\",{:8.3f},{:2d},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "\"{:10s}\",\"{:1s}\",\"{:12s}\"," \
               "{:3d},{:8.3f},{:8.3f}".format(*args)


class AcDcConverterVsc(RecordType):
    header = "ACDC_CONVERTER_VSC"
    comment = "# Cnv#,\"Op\",\"MetEnd\",AcBus#,DcBus#,NeutralBus#,\"CnvMode\"," \
              "\"VoltMode\",Aloss,Bloss,Minloss,FlowAcDc,FlowDcAc,Imax,Pwf," \
              "Qmin,Qmax,CtrBus#,\"[.Ctr Name.]\",Rmpct,Cost,\"[..Date..]\"," \
              "\"Cnd\",\"[...Name...]\",Stt,Setpoint"

    def __init__(self):
        super(AcDcConverterVsc, self).__init__()
        self.number = 0
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
        self.ac_bus = None
        self.dc_bus = None
        self.neutral_bus = None
        self.type = ""
        self.nominal_current = 0.0
        self.converter_ctr_mode = ""
        self.voltage_ctr_mode = ""
        self.aloss = 0.0
        self.bloss = 0.0
        self.minloss = 0.0
        self.flow_ac_dc = 0.0
        self.flow_dc_ac = 0.0
        self.max_current = 0.0
        self.power_factor = 0.0
        self.qmin = 0.0
        self.qmax = 0.0
        self.ctr_bus = None
        self.rmpct = 0.0
        self.cost = 0.0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.name = ""
        self.stt = STATUS_ON
        self.setpoint = 0.0

    def __str__(self):
        ac_bus_number = self.ac_bus.number if self.ac_bus is not None else 0
        dc_bus_number = self.dc_bus.number if self.dc_bus is not None else 0
        neutral_bus_number = self.neutral_bus.number \
            if self.neutral_bus is not None else 0
        ctr_bus_number = self.ctr_bus.number if self.ctr_bus is not None else 0
        ctr_bus_name = self.ctr_bus.name if self.ctr_bus is not None else ""
        args = [self.number, self.op, self.metering_end,
                ac_bus_number, dc_bus_number, neutral_bus_number, self.type,
                self.nominal_current,
                self.converter_ctr_mode, self.voltage_ctr_mode,
                self.aloss, self.bloss, self.minloss,
                self.flow_ac_dc, self.flow_dc_ac, self.max_current,
                self.power_factor, self.qmin, self.qmax,
                ctr_bus_number, ctr_bus_name,
                self.rmpct,
                self.cost, self.date, self.cnd, self.name, self.stt,
                self.setpoint]
        return "{:6d},\"{:1s}\",\"{:1s}\",{:6d},{:6d},{:6d}," \
               "\"{:1s}\",{:8.3f},\"{:1s}\",\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f}," \
               "{:6d},\"{:12s}\",{:8.3f},{:8.3f}," \
               "\"{:10s}\",\"{:1s}\",\"{:12s}\"," \
               "{:1d},{:8.3f}".format(*args)
