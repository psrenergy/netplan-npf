

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

        # Case title.
        self.title = ""
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

    def _append_elements(self, contents, header, comment, elements):
        # type: (list, str, str, list) -> None
        contents.append(header)
        contents.append(comment)
        for element in elements:
            contents.append(str(element))
        contents.append("END")

    def __str__(self):
        contents = ["NPF_REVISION", str(self.revision),
                    "TITLE", self.title, ]

        header_elements_pairs = (
            (Bus.header, Bus.comment, self.buses),
            (Bus.header, Bus.comment, self.middlepoint_buses),
            (Area.header, Area.comment, self.areas),
            (Region.header, Region.comment, self.regions),
            (System.header, System.comment, self.systems),
            (Demand.header, Demand.comment, self.demands),
            (Generator.header, Generator.comment, self.generators),
            (BusShunt.header, BusShunt.comment, self.bus_shunts),
            (Line.header, Line.comment, self.lines),
            (Line.header, Line.comment, self.lines),
            (LineShunt.header, LineShunt.comment, self.line_shunts),
            (Transformer.header, Transformer.comment, self.transformers),
            (Transformer.header, Transformer.comment, self.equivalent_transformers),
            (ThreeWindingTransformer.header, ThreeWindingTransformer.comment, self.three_winding_transformers),
            (ThreeWindingTransformer.header, ThreeWindingTransformer.comment, self.three_winding_transformers),
            (ControlledSeriesCapacitor.header, ControlledSeriesCapacitor.comment, self.cscs),
            (StaticVarCompensator.header, StaticVarCompensator.comment, self.svcs),
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
    comment = "('S','(........Name......)',S,(Ns)"

    def __init__(self):
        super(System, self).__init__()
        # Two-characters system unique identifier.
        self.id = ""
        # 12-characters system unique name.
        self.name = ""
        # Unique system number.
        self.number = 0


class Region(RecordType):
    """Region data."""
    header = "REGION"
    comment = "('R','(........Name......)',(Nr),(Ns),'Is'"

    def __init__(self):
        super(Region, self).__init__()
        # Two-characters unique region identifier.
        self.id = ""
        # 12-characters unique region name.
        self.name = ""
        #
        self.nr = 0
        self.ns = 0
        self.icode = ""


class Area(RecordType):
    """Area data."""
    header = "AREA"
    comment = "('Ar)','(.............Area Name............)',(Na),(Ns),'Is'"

    def __init__(self):
        super(Area, self).__init__()
        # Two-characters unique area identifier.
        self.id = ""
        # 12-characters unique area name.
        self.name = ""
        # Unique area number.
        self.number = 0
        self.system_number = 0
        self.iscode = ""


class Bus(RecordType):
    """Bus data."""
    header = "BUS"
    comment = "(Bus.),'(...Name...)','O',(.kV.),(Ar),(Rg),(Si),'(..Date..)','C',(.Cost.),TB,CC,(Volt),(Angl),(Vmax),(Vmin),(Emax),(Emin),S,'(.........Name24.......)'"

    def __init__(self):
        super(Bus, self).__init__()
        self.bus = 0
        self.name = ""
        self.o = ""
        self.kv = 0
        self.area = 0
        self.region = 0
        self.system = 0
        self.date = ""
        self.c = ""
        self.cost = 0
        self.tb = 0
        self.cc = 0
        self.volt = 0
        self.angl = 0
        self.vmax = 0
        self.vmin = 0
        self.emax = 0
        self.emin = 0
        self.s = 0
        self.name24 = ""


class Demand(RecordType):
    """Demand per bus (load) data."""
    header = "DEMAND"
    comment = "(Ndm),'(...DNam...)','O',(Bus.),'(...Bnam...)',(Nu),'(..Date..)','C',(Nd),(Nc),(PdemP),(QdemP)"

    def __init__(self):
        super(Demand, self).__init__()
        self.ndm = 0
        self.dnam = ""
        self.o = 0
        self.bus = 0
        self.bnam = ""
        self.nu = 0
        self.date = ""
        self.c = ""
        self.nd = 0
        self.nc = 0
        self.pdemp = 0
        self.qdemp = 0


class Generator(RecordType):
    """Generator data."""
    header = "GENERATOR"
    comment = "(Ng),'(..Name12..)','(...GNam...)','O',(Bus.),'(...Name...)','T',Nu,(Pmin),(Pmax),(Qmin),(Qmax),(PrbF),'(..Date..)','C',(Ktr.),'(.Ktr_Name.)',(TC),(Factor),Uc,(Pgen),(Qgen)"

    def __init__(self):
        super(Generator, self).__init__()
        self.ng = 0
        self.name12 = ""
        self.gnam = ""
        self.o = ""
        self.bus = 0
        self.name = ""
        self.t = 0
        self.nu = 0
        self.pmin = 0
        self.pmax = 0
        self.qmin = 0
        self.qmax = 0
        self.prbf = 0
        self.date = 0
        self.c = ""
        self.ktr = 0
        self.ktr_name = ""
        self.tc = 0
        self.factor = 0
        self.uc = 0
        self.pgen = 0
        self.qgen = 0


class Line(RecordType):
    """Line data."""
    header = "LINE"
    comment = "(Bfr.),(Bto.),Nc,'O','W',(.R%.),(.X%.),(MVAr),(.Rn.),(.Re.),(.Fp.),(.Cost.),'(..Date..)','C',(KeyC),TC,'(..Name12..)',( EF,(..Km..),S,'(................Name40................)'"

    def __init__(self):
        super(Line, self).__init__()
        self.bfr = 0
        self.bto = 0
        self.nc = 0
        self.o = ""
        self.w = ""
        self.r = 0
        self.x = 0
        self.mvar = 0
        self.rn = 0
        self.re = 0
        self.fp = 0
        self.cost = 0
        self.date = ""
        self.c = 0
        self.keyc = 0
        self.tc = 0
        self.name12 = ""
        self.ef = 0
        self.km = 0
        self.s = ""
        self.name40 = ""


class BusShunt(RecordType):
    """Bus shunt data."""
    header = "BUS_SHUNT"
    comment = "(Ns),'(...Name...)','O',(Bus.),'(.Bus_Name.)',(Ktr.),'(.Ktr_Name.)','T',(CT),(Nu),(MVAr),(K$/Uni),'(..Date..)','C',(Uc)"

    def __init__(self):
        super(BusShunt, self).__init__()
        self.ns = 0
        self.name = 0
        self.o = 0
        self.bus = 0
        self.bus_name = 0
        self.ktr = 0
        self.ktr_name = 0
        self.t = 0
        self.ct = 0
        self.nu = 0
        self.mvar = 0
        self.kcost_uni = 0
        self.date = 0
        self.c = 0
        self.uc = 0


class LineShunt(RecordType):
    """Line shunt data."""
    header = "LINE_SHUNT"
    comment = "(Ns),'(...SNam...)','O',(Bfr.),(BTo.),Nc,(MVAr),'B',(K$/Uni),'(..Date..)','C',S,'(...LKey...)'"

    def __init__(self):
        super(LineShunt, self).__init__()
        self.ns = 0
        self.snam = ""
        self.o = ""
        self.bfr = 0
        self.bto = 0
        self.nc = 0
        self.mvar = 0
        self.b = ""
        self.kcost_uni = 0
        self.date = ""
        self.c = ""
        self.s = 0
        self.lkey = ""


class Transformer(RecordType):
    """Two-winding transformer data."""
    header = "TRANSFORMER"
    comment = "(Bfr.),(Bto.),Nc,'O','W',(.R%.),(.X%.),(Tmn),(Tmx),(Phn),(Phx),TC,(BCn.),Nt,(.Rn.),(.Re.),(.Fp.),(.Cost.),'(..Date..)','C',(KeyC),'(...Name...)',( EF,'(................Name40................)',S,(Tap),(Phs),(Fmin),(Fmax),(FEmn),(FEmx)"

    def __init__(self):
        super(Transformer, self).__init__()
        self.bfr = 0
        self.bto = 0
        self.nc = 0
        self.o = ""
        self.w = ""
        self.r = 0
        self.x = 0
        self.tmn = 0
        self.tmx = 0
        self.phn = 0
        self.phx = 0
        self.tc = 0
        self.bcn = 0
        self.nt = 0
        self.rn = 0
        self.re = 0
        self.fp = 0
        self.cost = 0
        self.date = ""
        self.c = ""
        self.keyc = 0
        self.name = ""
        self.ef = 0
        self.name40 = ""
        self.s = 0
        self.tap = 0
        self.phs = 0
        self.fmin = 0
        self.fmax = 0
        self.femn = 0
        self.femx = 0


class ThreeWindingTransformer(RecordType):
    """Three-winding transformer data."""
    header = "THREE_WINDING_TRANSFORMER"
    comment = "(BPr.),(BSe.),(BTe.),(Fic.),'Nc','O',W,(RPS%),(XPS%),(SbPS),(RST%),(XST%),(SbST),(RPT%),(XPT%),(SbPT),(.Fp.),(.Cost.),'(..Date..)','C',(KeyC),'(..PrName..)','(..SeName..)','(..TeName..)','(..Name12..)','(................Name40......-->)"

    def __init__(self):
        super(ThreeWindingTransformer, self).__init__()
        self.bpr = 0
        self.bse = 0
        self.bte = 0
        self.fic = 0
        self.nc = 0
        self.o = ""
        self.w = ""
        self.rps = 0
        self.xps = 0
        self.sbps = 0
        self.rst = 0
        self.xst = 0
        self.sbst = 0
        self.rpt = 0
        self.xpt = 0
        self.sbpt = 0
        self.fp = 0
        self.cost = 0
        self.date = ""
        self.c = ""
        self.keyc = 0
        self.prname = ""
        self.sename = ""
        self.tename = ""
        self.name12 = ""
        self.name40 = ""


class ControlledSeriesCapacitor(RecordType):
    header = "CSC"
    comment = "(Bfr.),(Bto.),Nc,'O','W',(XMn%),(XMx%),Nt,(.Rn.),(.Re.),(.Fp.),(.Cost.),'(..Date..)','C',(KeyC),'(..Name12..)','CM','M',(VTMN),(VTMX),(LINX),(SET.),S,B,(.MW.)"

    def __init__(self):
        super(ControlledSeriesCapacitor, self).__init__()
        self.bfr = 0
        self.bto = 0
        self.nc = 0
        self.o = ""
        self.w = ""
        self.xmn = 0
        self.xmx = 0
        self.nt = 0
        self.rn = 0
        self.re = 0
        self.fp = 0
        self.cost = 0
        self.date = ""
        self.c = ""
        self.keyc = 0
        self.name12 = ""
        self.cm = ""
        self.m = ""
        self.vtmn = 0
        self.vtmx = 0
        self.linx = 0
        self.set = 0
        self.s = 0
        self.b = 0
        self.mw = 0


class StaticVarCompensator(RecordType):
    """Static var compensator data."""
    header = "DSVC"
    comment = "(Nc),'(...CNam...)','O',(.Bus),'(.Bus Name.)',(.Ktr),'(.Ktr Name.)',(CLin),CM,(Nu),(Qmin),(Qmax),(k$/Uni),'(..Date..)','C',S,(MVAR)"

    def __init__(self):
        super(StaticVarCompensator, self).__init__()
        self.nc = 0
        self.cnam = ""
        self.o = ""
        self.bus = 0
        self.bus_name = ""
        self.ktr = 0
        self.ktr_name = ""
        self.clin = 0
        self.cm = 0
        self.nu = 0
        self.qmin = 0
        self.qmax = 0
        self.kcost_uni = 0
        self.date = ""
        self.c = 0
        self.s = 0
        self.mvar = 0

