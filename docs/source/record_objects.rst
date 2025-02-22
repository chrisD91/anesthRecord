import mode : use the record_objects
--------------------------------------

the recorded data and associated methods are loaded in "wave classes".

four classes are builded to store and display the data and manipulate them, two for slowWaves ('trends'), two for fastWaves:

  - MonitorTrend
  - MonitorWave
  - TaphTrend
  - TelevetWave

loading is possible from an ipython terminal:

   .. code-block:: python

      # after import anesplot.recordmain as rec
      mtrends = rec.MonitorTrend()
      mwaves = rec.MonitorWave()
      ttrends = rec.TaphTrend()
      telwaves = rec.TelevetWave()  <- this has to be improved quite a lot

      # or import the object directly:
      from anesplot.slow_waves import MonitorTrend, TaphTrend
      from anesplot.fast_waves import MonitorWave

the methods provided allows to choose plotting and treatment actions
for example ::

   mtrends, ttrends:
      # attributes =  'data', 'fig', 'filename', 'header', 'param', ...
      # methods = 'show_graphs', 'clean_trend', 'plot_trend', 'save_roi', ...

   mwaves:
      # attributes = 'data', 'fig', 'filename', 'header', 'param' ...
      # methods : 'animate_fig', 'filter_ekg', 'plot_sample_ekgbeat_overlap', 'plot_sample_systolic_variation', 'plot_wave', ...


MonitorTrend object
....................

   .. autoclass:: anesplot.slow_waves.MonitorTrend


TaphTrend object
....................

   .. autoclass:: anesplot.slow_waves.TaphTrend


MonitorWave object
....................

   .. autoclass:: anesplot.fast_waves.MonitorWave


TelevetWave object
....................

   .. autoclass:: anesplot.fast_waves.TelevetWave
