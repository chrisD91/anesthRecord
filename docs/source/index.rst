.. anesplot documentation master file, created by
   sphinx-quickstart on Wed Sep  8 17:19:08 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#####################################
Welcome to anesplot's documentation!
#####################################

anesthPlot is a python package developped to extract, manipulate and plots **anesthesia data
recorded during equine anesthesia**.
Is is using recording generated by the Monitor Software or the Taphonius equine anesthesia machine.

The main purpose is an usage in a **teaching environment** (briefing-debriefing approach),
but this package can also facilite recording manipulation for other purposes.

.. warning::

  This is a work in progres,

   * the processes are mainly focused on horses anesthesia (default values)
   * in our environment the data recorded came from either:

      * an as3 or as5 anesthesia monitor (ekg, invasive pressure, etCO2, halogenate, spirometry)
      * a Taphonius equine ventilator
      * (some ekg .csv data extracted using a Televet holter system)



basics
======

.. toctree::
   :caption: basics

   script_usage
   import_usage

usage
=====

.. toctree::
   :caption: usage

   anesplot.record_main
   record_objects

example
=======

.. toctree::
   :caption: cookbook

   cookbook

more
====

.. toctree::
   :maxdepth: 1
   :caption: global usage

   anesplot.scanplot_directory
   anesplot.extract_hypotension
   anesplot.build_debrief

sub_modules
===========

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   anesplot.guides
   anesplot.loadrec
   anesplot.plot
   anesplot.treatrec
   anesplot.config


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
