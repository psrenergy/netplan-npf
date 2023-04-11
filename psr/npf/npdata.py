

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

        """Case title."""
        self.titu = ""

        self.dbar = []
        self.dbae = []
        self.dare = []
        self.dreg = []
        self.down = []
        self.dsis = []
        self.ddem = []
        self.dger = []
        self.dbsh = []
        self.dlin = []
        self.dshl = []
        self.dtrf = []
        self.dt3e = []
        self.dtr3 = []
        self.dcsc = []
        self.dsvc = []

    def _append_elements(self, contents, header, elements):
        contents.append(header)
        for element in elements:
            contents.append(element)
        contents.append("9999999")

    def __str__(self):
        contents = ["TITU", self.titu, "DBAR"]

        header_elements_pairs = (
            (Dbar.header, self.dbar),
            (Dbar.header, self.dbae),
            (Dare.header, self.dare),
            (Dreg.header, self.dreg),
            (Down.header, self.down),
            (Dsis.header, self.dsis),
            (Ddem.header, self.ddem),
            (Dger.header, self.dger),
            (Dbsh.header, self.dbsh),
            (Dlin.header, self.dlin),
            (Dlin.header, self.dlin),
            (Dshl.header, self.dshl),
            (Dtrf.header, self.dtrf),
            (Dtrf.header, self.dt3e),
            (Dtr3.header, self.dtr3),
            (Dtr3.header, self.dtr3),
            (Dcsc.header, self.dcsc),
            (Dsvc.header, self.dsvc),
        )

        for header, elements in header_elements_pairs:
            self._append_elements(contents, header, elements)

        return "\n".join(contents)


class Dsis:
    """System data."""
    header = "('S','(........Name......)',S,(Ns)"

    def __init__(self):
        self.id = ""
        self.name = ""
        self.ns = 0


class Down:
    """Owner data."""
    header = "('O','(........Name......)',(No),(Ns),'Is'"

    def __init__(self):
        self.id = ""
        self.name = ""
        self.no = 0
        self.ns = 0
        self.iscode = 0


class Dreg:
    """Region data."""
    header = "('R','(........Name......)',(Nr),(Ns),'Is'"

    def __init__(self):
        self.id = ""
        self.name = ""
        self.nr = 0
        self.ns = 0
        self.icode = ""


class Dare:
    """Area data."""
    header = "('Ar)','(...............Anam...............)',(Na),(Ns),'Is',(Exchg),(ExMin),(ExMax)"

    def __init__(self):
        self.id = ""
        self.name = ""
        self.na = 0
        self.ns = 0
        self.iscode = ""
        self.exchg = 0.0
        self.exmin = 0.0
        self.exmax = 0.0


class Dbar:
    """Bus data."""
    header = "(Bus.),'(...Name...)','O',(.kV.),(Ar),(Rg),(Si),'(..Date..)','C',(.Cost.),TB,CC,(Volt),(Angl),(Vmax),(Vmin),(Emax),(Emin),S,(Ow),'(.........Name24.......)'"

    def __init__(self):
        self.bus = 0
        self.name = ""
        self.o = ""
        self.kv = 0
        self.ar = 0
        self.rg = 0
        self.si = 0
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
        self.ow = 0
        self.name24 = ""


class Ddem:
    """Demand per bus (load) data."""
    header = "(Ndm),'(...DNam...)','O',(Bus.),'(...Bnam...)',(Nu),'(..Date..)','C',(Nd),(Nc),(PdemP),(QdemP),(PdemI),(QdemI),(PdemZ),(QdemZ)"

    def __init__(self):
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
        self.pdemi = 0
        self.qdemi = 0
        self.pdemz = 0
        self.qdemz = 0


class Dger:
    """Generator data."""
    header = "(Ng),'(..Name12..)','(...GNam...)','O',(Bus.),'(...Name...)','T',Nu,(Pmin),(Pmax),(Qmin),(Qmax),(PrbF),'(..Date..)','C',(Ktr.),'(.Ktr_Name.)',(TC),(Factor),Uc,(Pgen),(Qgen)"

    def __init__(self):
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


class Dlin:
    """Line data."""
    header = "(Bfr.),(Bto.),Nc,'O','W',(.R%.),(.X%.),(MVAr),(.Rn.),(.Re.),(.Fp.),(.Cost.),'(..Date..)','C',(KeyC),TC,'(..Name12..)',( EF,(..Km..),S,'(................Name40................)'"

    def __init__(self):
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


class Dbsh:
    """Bus shunt data."""
    header = "(Ns),'(...Name...)','O',(Bus.),'(.Bus_Name.)',(Ktr.),'(.Ktr_Name.)','T',(CT),(Nu),(MVAr),(K$/Uni),'(..Date..)','C',(Uc)"

    def __init__(self):
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


class Dshl:
    """Line shunt data."""
    header = "(Ns),'(...SNam...)','O',(Bfr.),(BTo.),Nc,(MVAr),'B',(K$/Uni),'(..Date..)','C',S,'(...LKey...)'"

    def __init__(self):
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


class Dtrf:
    """Two-winding transformer data."""
    header = "(Bfr.),(Bto.),Nc,'O','W',(.R%.),(.X%.),(Tmn),(Tmx),(Phn),(Phx),TC,(BCn.),Nt,(.Rn.),(.Re.),(.Fp.),(.Cost.),'(..Date..)','C',(KeyC),'(...Name...)',( EF,'(................Name40................)',S,(Tap),(Phs),(Fmin),(Fmax),(FEmn),(FEmx)"

    def __init__(self):
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


class Dtr3:
    """Three-winding transformer data."""
    header = "(BPr.),(BSe.),(BTe.),(Fic.),'Nc','O',W,(RPS%),(XPS%),(SbPS),(RST%),(XST%),(SbST),(RPT%),(XPT%),(SbPT),(.Fp.),(.Cost.),'(..Date..)','C',(KeyC),'(..PrName..)','(..SeName..)','(..TeName..)','(..Name12..)','(................Name40......-->)"

    def __init__(self):
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


class Dcsc:
    header = "(Bfr.),(Bto.),Nc,'O','W',(XMn%),(XMx%),Nt,(.Rn.),(.Re.),(.Fp.),(.Cost.),'(..Date..)','C',(KeyC),'(..Name12..)','CM','M',(VTMN),(VTMX),(LINX),(SET.),S,B,(.MW.)"

    def __init__(self):
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


class Dsvc:
    """Static var compensator data."""
    header = "(Nc),'(...CNam...)','O',(.Bus),'(.Bus Name.)',(.Ktr),'(.Ktr Name.)',(CLin),CM,(Nu),(Qmin),(Qmax),(k$/Uni),'(..Date..)','C',S,(MVAR)"

    def __init__(self):
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

