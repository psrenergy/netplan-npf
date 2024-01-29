import csv
import datetime
import io
import sys


_IS_PY2 = sys.version_info[0] == 2
_IS_PY3 = sys.version_info[0] == 3


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

# Transformer control type
XFMR_FIXED_TAP_ANGLE = 1
XFMR_FIXED_TAP_VAR_ANGLE = 2
XFMR_VAR_TAP_FIXED_ANGLE = 3
XFMR_VAR_TAP_ANGLE = 4

class NpfException(Exception):
    pass


def to_date_str(date):
    # type: (datetime.datetime) -> str
    """Convert a datetime object into NetPlan's date string format."""
    return date.strftime(DATE_FORMAT)


def _empty(str_value):
    # type: (str) -> bool
    """Test if a string is empty."""
    return len(str_value.strip()) == 0


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

    def find_system(self, system_number):
        # type: (int) -> "System"
        for system in self.systems:
            if system.number == system_number:
                return system
        raise NpfException("Could not find system #{}".format(system_number))

    def find_region(self, region_number):
        # type: (int) -> "Region"
        for region in self.regions:
            if region.number == region_number:
                return region
        raise NpfException("Could not find region #{}".format(region_number))

    def find_area(self, area_number):
        # type: (int) -> "Area"
        for area in self.areas:
            if area.number == area_number:
                return area
        raise NpfException("Could not find area #{}".format(area_number))

    def find_dclink(self, link_number):
        # type: (int) -> "DcLink"
        for dclink in self.dclinks:
            if dclink.number == link_number:
                return dclink
        raise NpfException("Could not find DC link #{}".format(link_number))

    def find_dcbus(self, bus_number):
        # type: (int) -> "DcBus"
        for bus in self.dcbuses:
            if bus.number == bus_number:
                return bus
        raise NpfException("Could not find DC bus #{}".format(bus_number))

    def find_bus(self, bus_number):
        # type: (int) -> Union["Bus", "MiddlePointBus"]
        for bus in self.buses:
            if bus.number == bus_number:
                return bus
        for bus in self.middlepoint_buses:
            if bus.number == bus_number:
                return bus
        raise NpfException("Could not find bus #{}".format(bus_number))

    def find_line(self, from_bus, to_bus, ncir):
        # type: (int, int, int) -> "Line"
        for line in self.lines:
            if line.from_bus.number == from_bus and \
                    line.to_bus.number == to_bus and \
                    line.parallel_circuit_number == ncir:
                return line

    def find_transformer(self, from_bus, to_bus, ncir):
        # type: (int, int, int) -> Union["Transformer","EquivalentTransformer"]
        for transformer in self.transformer:
            if transformer.from_bus.number == from_bus and \
                    transformer.to_bus.number == to_bus and \
                    transformer.parallel_circuit_number == ncir:
                return transformer
        for transformer in self.equivalent_transformers:
            if transformer.from_bus.number == from_bus and \
                    transformer.to_bus.number == to_bus and \
                    transformer.parallel_circuit_number == ncir:
                return transformer
        raise NpfException("Could not find transformer from bus #{} "
                           "to bus #{} #{}"
                           .format(from_bus, to_bus, ncir))

    def find_transformer_by_name(self, name):
        # type: (str) -> Union["Transformer","EquivalentTransformer"]
        for transformer in self.transformers:
            if transformer.name.strip() == name:
                return transformer
        for transformer in self.equivalent_transformers:
            if transformer.name.strip() == name:
                return transformer
        raise NpfException("Could not find transformer with name \"{}\""
                           .format(name))

    @staticmethod
    def _append_elements(contents, header, comment, elements):
        # type: (list, str, str, list) -> None
        contents.append(header)
        contents.append(comment)
        for element in elements:
            contents.append(str(element))
        contents.append("END\n")

    def __str__(self):
        contents = ["NPF_REVISION", str(self.revision),
                    "DESCRIPTION", self.description, ]

        header_elements_pairs = (
            (System.header, System.comment, self.systems),
            (Region.header, Region.comment, self.regions),
            (Area.header, Area.comment, self.areas),
            (Bus.header, Bus.comment, self.buses),
            (MiddlePointBus.header, MiddlePointBus.comment,
             self.middlepoint_buses),
            (Demand.header, Demand.comment, self.demands),
            (Generator.header, Generator.comment, self.generators),
            (Line.header, Line.comment, self.lines),
            (Transformer.header, Transformer.comment, self.transformers),
            (EquivalentTransformer.header, EquivalentTransformer.comment,
             self.equivalent_transformers),
            (ThreeWindingTransformer.header, ThreeWindingTransformer.comment,
             self.three_winding_transformers),
            (ControlledSeriesCapacitor.header,
             ControlledSeriesCapacitor.comment, self.cscs),
            (LineShunt.header, LineShunt.comment, self.line_shunts),
            (BusShunt.header, BusShunt.comment, self.bus_shunts),
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
            NpFile._append_elements(contents, header, comment, elements)

        return "\n".join(contents)

    @staticmethod
    def _is_comment(line):
        # type: (str) -> bool
        return len(line) == 0 or (len(line) > 0 and line[0] == "#")

    @staticmethod
    def from_file(file_path):
        # type: (str) -> "NpFile"
        data = NpFile()
        with open(file_path, "r") as data_file:
            while True:
                original_line = data_file.readline()
                line = original_line.strip()
                if len(original_line) == 0:
                    break
                elif NpFile._is_comment(line):
                    continue
                elif line == "NPF_REVISION":
                    rev_str = data_file.readline().strip()
                    data.revision = int(rev_str)
                elif line == "DESCRIPTION":
                    data.description = data_file.readline().strip()
                elif line == "BUS":
                    buses = data._parse_until_end(Bus, data_file)
                    data.buses.extend(buses)
                elif line == "MIDDLEPOINT_BUS":
                    buses = data._parse_until_end(MiddlePointBus, data_file)
                    data.middlepoint_buses.extend(buses)
                elif line == "AREA":
                    areas = data._parse_until_end(Area, data_file)
                    data.areas.extend(areas)
                elif line == "REGION":
                    regions = data._parse_until_end(Region, data_file)
                    data.regions.extend(regions)
                elif line == "SYSTEM":
                    systems = data._parse_until_end(System, data_file)
                    data.systems.extend(systems)
                elif line == "DEMAND":
                    demands = data._parse_until_end(Demand, data_file)
                    data.demands.extend(demands)
                elif line == "GENERATOR":
                    generators = data._parse_until_end(Generator, data_file)
                    data.generators.extend(generators)
                elif line == "BUS_SHUNT":
                    bus_shunts = data._parse_until_end(BusShunt, data_file)
                    data.bus_shunts.extend(bus_shunts)
                elif line == "LINE":
                    lines = data._parse_until_end(Line, data_file)
                    data.lines.extend(lines)
                elif line == "LINE_SHUNT":
                    shunts = data._parse_until_end(LineShunt, data_file)
                    data.line_shunts.extend(shunts)
                elif line == "TRANSFORMER":
                    transformers = data._parse_until_end(Transformer,
                                                         data_file)
                    data.transformers.extend(transformers)
                elif line == "EQUIVALENT_TRANSFORMER":
                    transformers = data._parse_until_end(
                        EquivalentTransformer, data_file)
                    data.equivalent_transformers.extend(transformers)
                elif line == "THREE_WINDING_TRANSFORMER":
                    transformers = data._parse_until_end(
                        ThreeWindingTransformer, data_file)
                    data.three_winding_transformers.extend(transformers)
                elif line == "CSC":
                    capacitors = data._parse_until_end(
                        ControlledSeriesCapacitor, data_file)
                    data.cscs.extend(capacitors)
                elif line == "SVC":
                    svcs = data._parse_until_end(
                        StaticVarCompensator, data_file)
                    data.svcs.extend(svcs)
                elif line == "DC_LINK":
                    links = data._parse_until_end(DcLink, data_file)
                    data.dclinks.extend(links)
                elif line == "DC_BUS":
                    buses = data._parse_until_end(DcBus, data_file)
                    data.dcbuses.extend(buses)
                elif line == "DC_LINE":
                    lines = data._parse_until_end(DcLine, data_file)
                    data.dclines.extend(lines)
                elif line == "ACDC_CONVERTER_LCC":
                    converters = data._parse_until_end(AcDcConverterLcc,
                                                       data_file)
                    data.lcc_converters.extend(converters)
                elif line == "ACDC_CONVERTER_VSC":
                    converters = data._parse_until_end(AcDcConverterVsc,
                                                       data_file)
                    data.vsc_converters.extend(converters)
                else:
                    raise NpfException("Could not parse line:\n{}".format(line))
        return data

    def _parse_until_end(self, element_class, data_file):
        elements = []
        while True:
            original_line = data_file.readline()
            line = original_line.strip()
            if line == "END" or len(original_line) == 0:
                break
            elif NpFile._is_comment(line):
                continue
            else:
                elements.append(element_class.read_from_str(self, line))
        return elements

    def save(self, file_path):
        # type: (str) -> None
        with open(file_path, "w") as np_file:
            np_file.write(str(self))


def _to_str(value):
    if isinstance(value, str):
        return "".join(["\"", value, "\""])
    return str(value)


if _IS_PY3:
    def _to_csv_list(line):
        # type: (str) -> list
        return next(csv.reader(io.StringIO(line)))
else:
    def _to_csv_list(line):
        # type: (str) -> list
        return next(csv.reader(io.StringIO(line.decode("utf-8"))))


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

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "RecordType"
        return RecordType()


class SeriesType(RecordType):
    def __init__(self):
        super(SeriesType, self).__init__()
        self.from_bus = None
        self.to_bus = None
        self.parallel_circuit_number = 1

    def from_bus_number(self) -> int:
        return self.from_bus.number if self.from_bus is not None else 0

    def to_bus_number(self) -> int:
        return self.to_bus.number if self.to_bus is not None else 0


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
        return "  \"{:2s}\",\"{:20s}\",{:7d}".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "System"
        obj = System()
        obj.id, obj.name, number_str = _to_csv_list(line)
        obj.number = int(number_str)
        return obj


class Region(RecordType):
    """Region data."""
    header = "REGION"
    comment = "# [ID],\"[........Name......]\",Region#,System#," \
              "\"SystemID\""

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
        return "  \"{:2s}\",\"{:12s}\",{:7d},{:7d},\"{:2s}\"".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "Region"
        obj = Region()
        obj.id, obj.name, number_str, system_number_str,\
            system_id = _to_csv_list(line)
        obj.number = int(number_str)
        obj.system = data.find_system(int(system_number_str))
        return obj


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
        return "  \"{:4s}\",\"{:36s}\",{:5d},{:7d},\"{:2s}\"".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "Area"
        obj = Area()
        obj.id, obj.name, number_str, system_number_str,\
            system_id = _to_csv_list(line)
        obj.number = int(number_str)
        obj.system = data.find_system(int(system_number_str))
        return obj


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
               "\"{:10s}\",\"{:1s}\",{:7.2f},{:1d},{:1d},{:8.4f},{:8.4f}," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:1d},\"{:24s}\"".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "Bus"
        obj = Bus()
        obj.load_from(data, line)
        return obj

    def load_from(self, data, line):
        # type: ("NpFile", str) -> None

        number_str, self.name, self.op, kv_str, area_str, region_str,\
            system_str, self.date, self.cnd, cost_str, type_str, lds_str,\
            volt_str, angle_str, vmax_str, vmin_str, evmax_str, evmin_str,\
            stt_str, self.extended_name = _to_csv_list(line)

        self.number = int(number_str)
        self.system = data.find_system(int(system_str))
        self.area = data.find_area(int(area_str))
        self.region = data.find_region(int(region_str))
        self.kvbase = float(kv_str)
        self.cost = float(cost_str)
        self.type = int(type_str)
        self.loadshed = int(lds_str)
        self.volt = float(volt_str)
        self.angle = float(angle_str)
        self.vmax = float(vmax_str)
        self.vmin = float(vmin_str)
        self.evmax = float(evmax_str)
        self.evmin = float(evmin_str)
        self.stt = int(stt_str)


class MiddlePointBus(Bus):
    header = "MIDDLEPOINT_BUS"
    comment = Bus.comment

    def __init__(self):
        super(MiddlePointBus, self).__init__()

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "MiddlePointBus"
        obj = MiddlePointBus()
        obj.load_from(data, line)
        return obj


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

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "Demand"
        obj = Demand()
        number_str, obj.name, obj.op, bus_number, _,\
            units_str, obj.date, obj.cnd, p_str, q_str = _to_csv_list(line)
        obj.number = int(number_str)
        obj.bus = data.find_bus(int(bus_number))
        obj.units = int(units_str)
        obj.p_mw = float(p_str)
        obj.q_mw = float(q_str)
        return obj


class Generator(RecordType):
    """Generator data."""
    header = "GENERATOR"
    comment = "# Gen#,\"[...Name...]\",\"Op\",Bus#,\"[.Bus Name.]\"," \
              "\"Type\",Units,Pmin,Pmax,Qmin,Qmax,\"[..Date..]\",\"C\"," \
              "CtrBus#,\"[CtrBusName]\",CtrType,Factor,UnitsOn,Pgen,Qgen"

    TYPE_HYDRO = "H"
    TYPE_THERMAL = "T"
    TYPE_RENEWABLE = "R"
    TYPE_SYNC = "S"
    TYPE_STATCOM = "V"

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
        self.power_factor = 1.0
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
                self.power_factor, self.units_on, self.pgen, self.qgen]
        return "{:6d},\"{:12s}\",\"{:1s}\",{:6d},\"{:12s}\"," \
               "\"{:1s}\",{:3d},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "\"{:10s}\",\"{:1s}\",{:6d},\"{:12s}\",{:1d}," \
               "{:8.3f},{:3d},{:8.3f},{:8.3f}".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "Generator"
        obj = Generator()
        number_str, obj.name, obj.op, bus_number, _,\
            obj.type, units_str, pmin_str, pmax_str,\
            qmin_str, qmax_str, obj.date, obj.cnd,\
            ctr_bus_number, _, ctr_type_str, factor_str,\
            units_on_str, pgen_str, qgen_str = _to_csv_list(line)
        obj.number = int(number_str)
        obj.bus = data.find_bus(int(bus_number))
        obj.ctr_bus = data.find_bus(int(ctr_bus_number))
        obj.units = int(units_str)
        obj.units_on = int(units_on_str)
        obj.ctr_type = int(units_str)
        obj.power_factor = float(factor_str)
        obj.pmax = float(pmax_str)
        obj.pmin = float(pmin_str)
        obj.qmax = float(qmax_str)
        obj.qmin = float(qmin_str)
        obj.pgen = float(pgen_str)
        obj.qgen = float(qgen_str)
        return obj


class Line(SeriesType):
    """Line data."""
    header = "LINE"
    comment = "# FromBus#,ToBus#,ParallelCirc#,Op,MetEnd,R%,X%,MVAr," \
              "NorRating,EmgRating,PF,Cost,\"[..Date..]\",\"Cnd\",Serie#," \
              "Type,\"[...Name...]\",Env,LengthKm," \
              "Stt,\"[....Extended Name.....]\""

    LTYPE_LINE = 0
    LTYPE_JUMPER = -1
    LTYPE_BREAKER = -2
    LTYPE_SWITCH = -3

    def __init__(self):
        super(Line, self).__init__()
        self.op = OP_ADD
        # Metering end: (F)rom or (T)o bus.
        self.metering_end = METERING_END_FROM
        self.r_pct = 0.0
        self.x_pct = 0.0
        self.mvar = 0.0
        self.normal_rating = FLOW_MAX
        self.emergency_rating = FLOW_MAX
        self.power_factor = 0.0
        self.cost = 0.0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.number = 0
        self.type = self.LTYPE_LINE
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
                self.r_pct, self.x_pct, self.mvar, self.normal_rating,
                self.emergency_rating, self.power_factor, self.cost,
                self.date, self.cnd, self.number, self.type, self.name,
                self.env_factor, self.length_km, self.stt, self.extended_name
                ]
        return "{:6d},{:6d},{:3d},\"{:1s}\",\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},\"{:10s}\",\"{:1s}\",{:6d}," \
               "{:1d},\"{:12s}\",{:1d},{:8.3f},{:1d},\"{:12s}\"".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "Line"
        obj = Line()
        from_number, to_number, ncir, obj.op, obj.metering_end,\
            r_str, x_str, mvar_str, rat_str, emg_str, pf_str, \
            cost_str, obj.date, obj.cnd, series_str, type_str, \
            obj.name, env_str, len_str, stt_str, \
            obj.extended_name = _to_csv_list(line)
        obj.series_number = int(series_str)
        obj.from_bus = data.find_bus(int(from_number))
        obj.to_bus = data.find_bus(int(to_number))
        obj.parallel_circuit_number = int(ncir)
        obj.type = int(type_str)
        obj.r_pct = float(r_str)
        obj.x_pct = float(x_str)
        obj.mvar_pct = float(mvar_str)
        obj.normal_rating = float(rat_str)
        obj.emergency_rating = float(emg_str)
        obj.power_factor = float(pf_str)
        obj.cost = float(cost_str)
        obj.env_factor = int(env_str)
        obj.length_km = float(len_str) if not _empty(len_str.strip()) else 1.0
        obj.stt = int(stt_str)
        return obj


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

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "BusShunt"
        obj = BusShunt()
        number_str, obj.name, obj.op, bus_str, _, ctr_str, _,\
            obj.type, ctr_type_str, units_str, mvar_str, cost_str, obj.date, \
            obj.cnd, units_on_str = _to_csv_list(line)
        obj.number = int(number_str)
        obj.bus = data.find_bus(int(bus_str))
        obj.ctr_bus = data.find_bus(int(ctr_str))
        obj.ctr_type = int(ctr_type_str)
        obj.units = int(units_str)
        obj.units_on = int(units_on_str)
        obj.mvar = float(mvar_str)
        obj.cost = float(cost_str)
        return obj


class LineShunt(RecordType):
    """Line shunt data."""
    header = "LINE_SHUNT"
    comment = "# Shunt#,\"[...Name...]\",\"Op\"," \
              "FromBus#,ToBus#,ParallelCirc#,MVAr,Term,Cost," \
              "\"[..Date..]\",\"Cnd\",Stt,\"[.LineName.]\""
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
            if self.circuit is not None else 0
        circ_to_number = self.circuit.to_bus.number \
            if self.circuit is not None else 0
        circ_name = self.circuit.name if self.circuit is not None else ""
        circ_parallel = self.circuit.parallel_circuit_number\
            if self.circuit is not None else 0
        args = [self.number, self.name, self.op,
                circ_from_number, circ_to_number,
                circ_parallel, self.mvar, self.terminal, self.cost,
                self.date, self.cnd, self.stt, circ_name]
        return "{:6d},\"{:12s}\",\"{:1s}\",{:6d},{:6d},{:2d},{:8.3f}," \
               "\"{:1s}\",{:8.3f},\"{:10s}\",\"{:1s}\"," \
               "{:1d},\"{:12s}\"".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "LineShunt"
        obj = LineShunt()
        number_str, obj.name, obj.op, from_str, to_str, ncir,\
            mvar_str, obj.terminal, cost_str, obj.date, \
            obj.cnd, stt_str, _ = _to_csv_list(line)
        obj.number = int(number_str)
        obj.circuit = data.find_line(int(from_str), int(to_str), int(ncir))
        obj.mvar = float(mvar_str)
        obj.cost = float(cost_str)
        return obj


class Transformer(SeriesType):
    """Two-winding transformer data."""
    header = "TRANSFORMER"
    comment = "# FromBus#,ToBus#,ParallelCirc#,\"Op\",\"MetEnd\",R%,X%," \
              "TapMin,TapMax,PhaseMin,PhaseMax,ControlType,CtrBus,TapSteps," \
              "NorRating,EmgRating,PF,Cost,\"[..Date..]\",\"Cnd\",Series#," \
              "\"[...Name...]\",Env,\"[...Extended Name...]\",Stt,Tap,Phase," \
              "MinFlow,MaxFlow,EmgMinFlow,EmgMaxFlow"

    def __init__(self):
        super(Transformer, self).__init__()
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
        self.normal_rating = FLOW_MAX
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
                ctr_bus_number, self.tap_steps, self.normal_rating,
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

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "Transformer"
        obj = Transformer()
        obj.load_from(data, line)
        return obj

    def load_from(self, data, line):
        # type: ("NpFile", str) -> None

        from_str, to_str, ncir, self.op, self.metering_end, \
            r_str, x_str, tmin_str, tmax_str, pmin_str, pmax_str, \
            ctr_type, ctr_bus, steps_str, rat_str, emg_str, \
            pf_str, cost_str, self.date, self.cnd, series_str,\
            self.name, env_str, self.extended_name,\
            stt_str, tap_str, phs_str, minflow, maxflow,\
            eminflow, emaxflow = _to_csv_list(line)

        self.from_bus = data.find_bus(int(from_str))
        self.to_bus = data.find_bus(int(to_str))
        self.parallel_circuit_number = int(ncir)
        ctr_bus = int(ctr_bus) if not _empty(ctr_bus) else 0
        self.ctr_bus = data.find_bus(ctr_bus) if ctr_bus != 0 else None
        self.control_type = int(ctr_type)
        self.r_pct = float(r_str)
        self.x_pct = float(x_str)
        self.tap_min = float(tmin_str)
        self.tap_max = float(tmax_str)
        self.tap_steps = int(steps_str)
        self.phase_min = float(pmin_str) if not _empty(pmin_str) else 0.0
        self.phase_max = float(pmax_str) if not _empty(pmax_str) else 0.0
        self.normal_rating = float(rat_str)
        self.emergency_rating = float(emg_str)
        self.cost = float(cost_str)
        self.series_number = int(series_str)
        self.minflow = float(minflow)
        self.maxflow = float(maxflow)
        self.emergency_minflow = float(eminflow)
        self.emergency_maxflow = float(emaxflow)
        self.stt = int(stt_str) if not _empty(stt_str) else 1
        self.tap = float(tap_str) if not _empty(tap_str) else 1.0
        self.phase = float(phs_str) if not _empty(phs_str) else 0.0


class EquivalentTransformer(Transformer):
    header = "EQUIVALENT_TRANSFORMER"
    comment = Transformer.comment

    def __init__(self):
        super(EquivalentTransformer, self).__init__()

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "EquivalentTransformer"
        obj = EquivalentTransformer()
        obj.load_from(data, line)
        return obj


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
        self.primary_transformer = None
        self.secondary_transformer = None
        self.tertiary_transformer = None
        self.middlepoint_bus = None
        self.parallel_circuit_number = 1
        self.op = OP_ADD
        # TODO: this doesn't make sense for 3w transformers
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
        self.name = ""
        self.extended_name = ""

    def from_bus_number(self) -> int:
        return self.primary_transformer.from_bus.number \
            if self.primary_transformer is not None else 0

    def to_bus_number(self) -> int:
        return self.primary_transformer.to_bus.number \
            if self.primary_transformer is not None else 0

    def middlepoint_bus_number(self) -> int:
        return self.middlepoint_bus.number \
            if self.middlepoint_bus is not None else 0

    def tertiary_bus_number(self) -> int:
        return self.tertiary_transformer.to_bus.number \
            if self.tertiary_transformer is not None else 0

    def __str__(self):
        primary_bus_number = self.primary_transformer.from_bus.number \
            if self.primary_transformer is not None else 0
        primary_name = self.primary_transformer.name \
            if self.primary_transformer is not None else ""
        secondary_bus_number = self.secondary_transformer.from_bus.number \
            if self.secondary_transformer is not None else 0
        secondary_name = self.secondary_transformer.name \
            if self.secondary_transformer is not None else ""
        tertiary_bus_number = self.tertiary_transformer.from_bus.number \
            if self.tertiary_transformer is not None else 0
        tertiary_name = self.tertiary_transformer.name \
            if self.tertiary_transformer is not None else ""
        middlepoint_bus_number = self.middlepoint_bus.number \
            if self.middlepoint_bus is not None else 0
        args = [primary_bus_number, secondary_bus_number,
                tertiary_bus_number, middlepoint_bus_number,
                self.parallel_circuit_number, self.op, self.metering_end,
                self.rps_pct, self.xps_pct, self.sbaseps_mva,
                self.rst_pct, self.xst_pct, self.sbasest_mva,
                self.rpt_pct, self.xpt_pct, self.sbasept_mva,
                self.power_factor, self.cost, self.date, self.cnd,
                self.series_number, primary_name, secondary_name,
                tertiary_name, self.name, self.extended_name]
        return "{:6d},{:6d},{:6d},{:6d},{:2d},\"{:1s}\",\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f}," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "\"{:10s}\",\"{:1s}\",{:6d}," \
               "\"{:12s}\",\"{:12s}\",\"{:12s}\"," \
               "\"{:12s}\",\"{:12s}\"".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "ThreeWindingTransformer"
        obj = ThreeWindingTransformer()
        _, _, _, mid_str, ncir, obj.op,\
            obj.metering_end, rps_pct, xps_pct, sbaseps_mva,\
            rst_pct, xst_pct, sbasest_mva, \
            rpt_pct, xpt_pct, sbasept_mva, \
            power_factor, cost_str, obj.date, obj.cnd,\
            series_str, pri_name, sec_name, ter_name, obj.name,\
            obj.extended_name = _to_csv_list(line)

        obj.primary_transformer = data.find_transformer_by_name(
            pri_name.strip())
        obj.secondary_transformer = data.find_transformer_by_name(
            sec_name.strip())
        obj.tertiary_transformer = data.find_transformer_by_name(
            ter_name.strip())
        obj.middlepoint_bus = data.find_bus(int(mid_str))
        obj.parallel_circuit_number = int(ncir)
        obj.rps_pct = float(rps_pct)
        obj.xps_pct = float(xps_pct)
        obj.sbaseps_mva = float(sbaseps_mva)
        obj.rst_pct = float(rst_pct)
        obj.xst_pct = float(xst_pct)
        obj.sbasest_mva = float(sbasest_mva)
        obj.rpt_pct = float(rpt_pct)
        obj.xpt_pct = float(xpt_pct)
        obj.sbasept_mva = float(sbasept_mva)
        obj.power_factor = float(power_factor) \
            if not _empty(power_factor) else 0.0
        obj.cost = float(cost_str) if not _empty(cost_str) else 0.0
        obj.series_number = int(series_str)
        return obj


class ControlledSeriesCapacitor(RecordType):
    header = "CSC"
    comment = "# FromBus#,ToBus#,ParallelCirc#,\"Op\",\"MetEnd\"," \
              "Xmin%,Xmax%,NorRating,EmgRating,PF,Cost,\"[..Date..]\"," \
              "\"Cnd\",Series#,\"[...Name...]\",\"CM\",Stt," \
              "Bypass,Setpoint"

    CONTROL_MODE_FIXED_X = 0
    CONTROL_MODE_POWER = 1

    def __init__(self):
        super(ControlledSeriesCapacitor, self).__init__()
        self.from_bus = None
        self.to_bus = None
        self.parallel_circuit_number = 1
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
        self.xmin_pct = 0.0
        self.xmax_pct = 0.0
        self.normal_rating = FLOW_MAX
        self.emergency_rating = FLOW_MAX
        self.power_factor = 0.0
        self.cost = 0.0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.series_number = 0
        self.name = ""
        self.control_mode = self.CONTROL_MODE_FIXED_X
        self.stt = STATUS_ON
        self.bypass = STATUS_OFF
        self.setpoint = 0.0

    def __str__(self):
        from_bus_number = self.from_bus.number \
            if self.from_bus is not None else 0
        to_bus_number = self.to_bus.number if self.to_bus is not None else 0

        args = [
            from_bus_number, to_bus_number,
            self.parallel_circuit_number, self.op, self.metering_end,
            self.xmin_pct, self.xmax_pct,
            self.normal_rating, self.emergency_rating,
            self.power_factor, self.cost, self.date, self.cnd,
            self.series_number, self.name, self.control_mode, self.stt,
            self.bypass, self.setpoint
        ]
        return "{:6d},{:6d},{:3d},\"{:1s}\",\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f},{:8.3f}," \
               "\"{:10s}\",\"{:1s}\",{:6d},\"{:12s}\",{:1d},{:1d}," \
               "{:1d},{:8.3f}".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "ControlledSeriesCapacitor"
        obj = ControlledSeriesCapacitor()
        from_bus, to_bus, ncir, obj.op, obj.metering_end,\
            xmin, xmax, rat_str, emg_str, pf_str, cost_str, \
            obj.date, obj.cnd, series_str, obj.name, \
            obj.control_mode, stt_str, byp_str, set_str = _to_csv_list(line)

        obj.from_bus = data.find_bus(int(from_bus))
        obj.to_bus = data.find_bus(int(to_bus))
        obj.parallel_circuit_number = int(ncir)
        obj.xmax_pct = float(xmax)
        obj.xmin_pct = float(xmin)
        obj.normal_rating = float(rat_str)
        obj.emergency_rating = float(emg_str)
        obj.power_factor = float(pf_str)
        obj.cost_str = float(cost_str) if not _empty(cost_str) else 0.0
        obj.series_number = int(series_str)
        obj.stt = int(stt_str)
        obj.bypass = int(byp_str)
        obj.setpoint = float(set_str)
        return obj


class StaticVarCompensator(RecordType):
    """Static var compensator data."""
    header = "SVC"
    comment = "# SVC#,\"[...Name...]\",\"Op\",Bus#,\"[.Bus Name.]\",CtrBus," \
              "\"[.Ctr Name.]\",Droop,CtrMode,Units,Qmin,Qmax,Cost," \
              "\"[..Date..]\",\"Cnd\",Stt,SetMVAR"
    MODE_POWER = 1

    def __init__(self):
        super(StaticVarCompensator, self).__init__()
        self.number = 0
        self.name = ""
        self.op = OP_ADD
        self.bus = None
        self.ctr_bus = None
        self.droop = 0.0
        self.ctr_mode = self.MODE_POWER
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


    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "StaticVarCompensator"
        obj = StaticVarCompensator()
        number_str, obj.name, obj.op, bus_str, _, ctr_str, _,\
            droop_str, mode_str, units_str, qmin_str, qmax_str,\
            cost_str, obj.date, obj.cnd, stt_str, set_str = _to_csv_list(line)

        obj.number = int(number_str)
        obj.bus = data.find_bus(int(bus_str))
        obj.ctr_bus = data.find_bus(int(ctr_str))
        obj.ctr_mode = int(mode_str)
        obj.qmin = float(qmin_str)
        obj.qmax = float(qmax_str)
        obj.cost = float(cost_str) if not _empty(cost_str) else 0.0
        obj.droop = float(droop_str)
        obj.units = int(units_str)
        obj.stt = int(stt_str)
        obj.mvar_setpoint = float(set_str)
        return obj


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

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "DcLink"
        obj = DcLink()
        number_str, obj.name, kv_str, mw_str, obj.type = _to_csv_list(line)
        obj.number = int(number_str)
        obj.kvbase = float(kv_str)
        obj.mwbase = float(mw_str)
        return obj


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

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "DcBus"
        obj = DcBus()
        number_str, obj.name, obj.op, type_str, obj.polarity,\
            groundr, area_str, region_str, system_str, dclink_str, \
            obj.date, obj.cnd, cost_str, volt_str = _to_csv_list(line)
        obj.number = int(number_str)
        obj.type = int(type_str) if not _empty(type_str) else 0
        obj.groundr = float(groundr) if not _empty(groundr) else 0.0
        obj.area = data.find_area(int(area_str))
        obj.region = data.find_region(int(region_str))
        obj.system = data.find_system(int(system_str))
        obj.dclink = data.find_dclink(int(dclink_str))
        obj.cost = float(cost_str) if not _empty(cost_str) else 0.0
        obj.volt = float(volt_str)
        return obj


class DcLine(SeriesType):
    header = "DC_LINE"
    comment = "# FromBus#,ToBus#,ParallelCirc#,\"Op\",\"MetEnd\"," \
              "R_Ohm,L_Ohm,NominalRating,Cost,\"[..Date..]\",Cnd,Series#," \
              "\"[.........Name.........]\",Stt"

    def __init__(self):
        super(DcLine, self).__init__()
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
        self.r_ohm = 0.0
        self.l_ohm = 0.0
        self.normal_rating = FLOW_MAX
        self.cost = 0.0
        self.date = DEFAULT_DATE
        self.cnd = CND_REGISTRY
        self.number = 0
        self.name = ""
        self.stt = STATUS_ON

    def __str__(self):
        from_bus_number = self.from_bus.number \
            if self.from_bus is not None else 0
        to_bus_number = self.to_bus.number if self.to_bus is not None else 0
        args = [from_bus_number, to_bus_number,
                self.parallel_circuit_number, self.op, self.metering_end,
                self.r_ohm, self.l_ohm, self.normal_rating, self.cost,
                self.date, self.cnd, self.number, self.name, self.stt]
        return "{:6d},{:6d},{:3d},\"{:1s}\",\"{:1s}\"," \
               "{:8.3f},{:8.3f},{:8.3f},{:8.3f},\"{:10s}\"," \
               "\"{:1s}\",{:6d},\"{:24s}\",{:1d}".format(*args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "DcLine"
        obj = DcLine()
        fodasse = _to_csv_list(line)
        from_str, to_str, ncir, obj.op, obj.metering_end,\
            r_str, l_str, rat_str, cost_str, obj.date,\
            obj.cnd, series_str, obj.name, stt_str = fodasse
        obj.from_bus = data.find_dcbus(int(from_str))
        obj.to_bus = data.find_dcbus(int(to_str))
        obj.parallel_circuit_number = int(ncir)
        obj.r_ohm = float(r_str)
        obj.l_ohm = float(l_str) if not _empty(l_str) else 0.0
        obj.normal_rating = float(rat_str)
        obj.cost = float(cost_str) if not _empty(cost_str) else 0.0
        obj.series_number = int(series_str)
        obj.stt = int(stt_str)
        return obj


class AcDcConverter(RecordType):
    def __init__(self):
        super(AcDcConverter, self).__init__()
        self.ac_bus = None
        self.dc_bus = None
        self.neutral_bus = None

    def ac_bus_number(self):
        return self.ac_bus.number if self.ac_bus is not None else 0

    def dc_bus_number(self):
        return self.dc_bus.number if self.dc_bus is not None else 0

    def neutral_bus_number(self):
        return self.neutral_bus.number if self.neutral_bus is not None else 0


class AcDcConverterLcc(AcDcConverter):
    header = "ACDC_CONVERTER_LCC"
    comment = "# Cnv#,\"Op\",\"MetEnd\",AcBus#,DcBus#,NeutralBus#,\"Type\"," \
              "Inom,Bridges,Xc,Vfs,Snom,Tmin,Tmax,Steps,\"Mode\"," \
              "FlowAcDc,FlowDcAc," \
              "FirR,FirRmin,FirRmax,FirI,FirImin,FirImax,CCCC,Cost," \
              "\"[..Date..]\",\"Cnd\",\"[...Name...]\",Hz,Stt,Tap,Setpoint"

    TYPE_RECTIFIER = "R"
    TYPE_INVERTER = "I"
    TYPE_BIDIRECTIONAL = "B"

    def __init__(self):
        super(AcDcConverterLcc, self).__init__()
        self.number = 0
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
        # Type: (R)etifier or (I)nverter
        self.type = AcDcConverterLcc.TYPE_RECTIFIER
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
        self.rectifier_firing_angle_set = 0.0
        self.rectifier_firing_angle_min = 0.0
        self.rectifier_firing_angle_max = 0.0
        self.inverter_firing_angle_set = 0.0
        self.inverter_firing_angle_min = 0.0
        self.inverter_firing_angle_max = 0.0
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
        args = {"num": self.number,
                "op": self.op,
                "met": self.metering_end,
                "acb": ac_bus_number,
                "dcb": dc_bus_number,
                "dcbn": neutral_bus_number,
                "type": self.type.strip(),
                "inom": self.nominal_current,
                "br": self.bridges,
                "xc": self.xc,
                "vfs": self.vfs,
                "snom": self.nominal_power,
                "tmin": self.tap_min,
                "tmax": self.tap_max,
                "tstp": self.tap_steps,
                "ctr": self.control_mode.strip(),
                "facdc": self.flow_ac_dc,
                "fdcac": self.flow_dc_ac,
                "rfirset": self.rectifier_firing_angle_set,
                "rfirmin": self.rectifier_firing_angle_min,
                "rfirmax": self.rectifier_firing_angle_max,
                "ifirset": self.inverter_firing_angle_set,
                "ifirmin": self.inverter_firing_angle_min,
                "ifirmax": self.inverter_firing_angle_max,
                "cccc": self.ccc_capacitance,
                "cost": self.cost,
                "date": self.date.strip(),
                "cnd": self.cnd.strip(),
                "name": self.name,
                "hz": self.hzbase,
                "stt": self.stt,
                "tap": self.tap,
                "set": self.setpoint, }
        return "{num:6d},\"{op:1s}\",\"{met:1s}\"," \
               "{acb:6d},{dcb:6d},{dcbn:6d}," \
               "\"{type:1s}\",{inom:8.3f}," \
               "{br:2d},{xc:8.3f},{vfs:8.3f}," \
               "{snom:8.3f},{tmin:8.3f},{tmax:8.3f}," \
               "{tstp:3d},\"{ctr:1s}\"," \
               "{facdc:8.3f},{fdcac:8.3f}," \
               "{rfirset:8.3f},{rfirmin:8.3f},{rfirmax:8.3f}," \
               "{ifirset:8.3f},{ifirmin:8.3f},{ifirmax:8.3f}," \
               "{cccc:8.3f},{cost:8.3f}," \
               "\"{date:10s}\",\"{cnd:1s}\",\"{name:12s}\"," \
               "{hz:3d},{stt:1d},{tap:8.4f},{set:8.3f}".format(**args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "AcDcConverterLcc"
        obj = AcDcConverterLcc()
        number_str, obj.op, obj.metering_end, ac_bus, dc_bus, neutral_bus,\
            obj.type, inom, bridges, xc, vfs, snom, tmin, tmax,\
            steps, obj.control_mode, flowacdc, flowdcac, \
            rfirang, rfirmin, rfirmax, ifirang, ifirmin, ifirmax, cccc, \
            cost, obj.date, obj.cnd, obj.name, \
            hz, stt, tap, setpoint = _to_csv_list(line)
        obj.number = int(number_str)
        obj.ac_bus = data.find_bus(int(ac_bus))
        obj.dc_bus = data.find_dcbus(int(dc_bus))
        obj.neutral_bus = data.find_dcbus(int(neutral_bus))
        obj.nominal_current = float(inom)
        obj.bridges = int(bridges)
        obj.xc = float(xc)
        obj.vfs = float(vfs)
        obj.nominal_power = float(snom)
        obj.tap_min = float(tmin)
        obj.tap_max = float(tmax)
        obj.tap_steps = int(steps)
        obj.flow_ac_dc = float(flowacdc)
        obj.flow_dc_ac = float(flowdcac)
        # TODO: use better values for empty min/max.
        obj.rectifier_firing_angle_set = float(rfirang) \
            if not _empty(rfirang) else 0.0
        obj.rectifier_firing_angle_min = float(rfirmin) \
            if not _empty(rfirmin) else 0.0
        obj.rectifier_firing_angle_max = float(rfirmax) \
            if not _empty(rfirmax) else 0.0
        obj.inverter_firing_angle_set = float(ifirang) \
            if not _empty(ifirang) else 0.0
        obj.inverter_firing_angle_min = float(ifirmin) \
            if not _empty(ifirmin) else 0.0
        obj.inverter_firing_angle_max = float(ifirmax) \
            if not _empty(ifirmax) else 0.0
        obj.ccc_capacitance = float(cccc)
        obj.cost = float(cost) if not _empty(cost) else 0.0
        obj.hzbase = int(hz)
        obj.stt = int(stt)
        obj.tap = float(tap)
        obj.setpoint = float(setpoint)
        return obj


class AcDcConverterVsc(AcDcConverter):
    header = "ACDC_CONVERTER_VSC"
    comment = "# Cnv#,\"Op\",\"MetEnd\",AcBus#,DcBus#,NeutralBus#," \
              "\"CnvMode\",\"VoltMode\",Aloss,Bloss,Minloss,FlowAcDc," \
              "FlowDcAc,Imax,Pwf,Qmin,Qmax,CtrBus#,\"[.Ctr Name.]\"," \
              "Rmpct,Cost,\"[..Date..]\",\"Cnd\",\"[...Name...]\",Stt,Setpoint"

    def __init__(self):
        super(AcDcConverterVsc, self).__init__()
        self.number = 0
        self.op = OP_ADD
        self.metering_end = METERING_END_FROM
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
        args = {"number": self.number,
                "op": self.op,
                "met": self.metering_end,
                "acb": ac_bus_number,
                "dcb": dc_bus_number,
                "dcbn": neutral_bus_number,
                "cctr": self.converter_ctr_mode, "vctr": self.voltage_ctr_mode,
                "alo": self.aloss, "blo": self.bloss, "mlo": self.minloss,
                "facdc": self.flow_ac_dc, "fdcac": self.flow_dc_ac,
                "imax": self.max_current,
                "pf": self.power_factor,
                "qmin": self.qmin, "qmax": self.qmax,
                "ctrb": ctr_bus_number,
                "ctrbnam": ctr_bus_name,
                "rmpct": self.rmpct,
                "cost": self.cost,
                "date": self.date,
                "cnd": self.cnd,
                "name": self.name,
                "stt": self.stt,
                "set": self.setpoint}
        return "{number:6d},\"{op:1s}\",\"{met:1s}\"," \
               "{acb:6d},{dcb:6d},{dcbn:6d}," \
               "\"{cctr:1s}\",\"{vctr:1s}\"," \
               "{alo:8.3f},{blo:8.3f},{mlo:8.3f}," \
               "{facdc:8.3f},{fdcac:8.3f},{imax:8.3f}," \
               "{pf:8.3f},{qmin:8.3f},{qmax:8.3f}," \
               "{ctrb:6d},\"{ctrbnam:12s}\",{rmpct:8.3f},{cost:8.3f}," \
               "\"{date:10s}\",\"{cnd:1s}\",\"{name:12s}\"," \
               "{stt:1d},{set:8.3f}".format(**args)

    @staticmethod
    def read_from_str(data, line):
        # type: ("NpFile", str) -> "AcDcConverterVsc"
        obj = AcDcConverterVsc()
        number_str, obj.op, obj.metering_end, ac_bus, dc_bus, neutral_bus,\
            obj.converter_ctr_mode, obj.voltage_ctr_mode, \
            aloss, bloss, minloss, flowacdc, flowdcac, imax, pwf, qmin, qmax,\
            ctr_bus, _, rmpct, cost, obj.date, obj.cnd, \
            obj.name, stt, setpoint = _to_csv_list(line)
        obj.number = int(number_str)
        obj.ac_bus = data.find_bus(int(ac_bus))
        obj.dc_bus = data.find_dcbus(int(dc_bus))
        obj.neutral_bus = data.find_dcbus(int(neutral_bus))
        obj.ctr_bus = data.find_bus(int(ctr_bus))
        obj.max_current = float(imax)
        obj.aloss = float(aloss)
        obj.bloss = float(bloss)
        obj.minloss = float(minloss)
        obj.pwf = float(pwf)
        obj.qmin = float(qmin)
        obj.qmax = float(qmax)
        obj.rmpct = float(rmpct)
        obj.flow_ac_dc = float(flowacdc)
        obj.flow_dc_ac = float(flowdcac)
        obj.cost = float(cost) if not _empty(cost) else 0.0
        obj.stt = int(stt)
        obj.setpoint = float(setpoint)
        return obj
