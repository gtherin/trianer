__version__ = "2.7.3"

from .analysis.vetruve import *

from .core.athlete import Athlete
from .core.triathlon import *
from .core.variable import *
from .core.variables import variables

from .nutrition.fueling import *

from .race.gpx import *
from .race.weather import *
from .race.race import Race
from .race.races import available_races
