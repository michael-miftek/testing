import colorcet as cc
from colorcet.plotting import swatch, swatches
import holoviews as hv
hv.extension('matplotlib')

# swatch('fire')

# colorlist = ['%06X' % idx for idx in range(0x8000, 0xffff)]
colorlist = ['%06X' % idx for idx in range(0xff0000, 0xffff00, 0x000200)]
print(colorlist)
swatch(name='custom', cmap=colorlist)