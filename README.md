

Triple-A: Analysis and Visual Exploration of Households' Energy Consumption
==========

[Triple-A](http://triple-a-interreg.eu) is a EU-INTERREG project aiming at reducing CO2 emissions in cities by generating awareness in homeowners about households carbon footprint. This repository contains an interactive dashboard developped in the context of Triple-A intented to show homeowners their **energy consumption patterns** through time.

Demo at [https://triple-a-demo.herokuapp.com](https://triple-a-demo.herokuapp.com/)


## Dataset

The dashboard uses data collected from a house in the north of France during 1-year. The dataset is composed of measurements from 4 sensors:

* electricity (kWh)
* gas
* indoor/outdoor temperature (°C) 
* indoor/outdoor relative humidity (%)

The raw dataset is available at the [Triple-A-household-energy-dataset](https://github.com/javieraespinosa/Triple-A-household-energy-dataset) repository. A copy is also available inside the [data-preparation/notebooks/data/original](./data-preparation/notebooks/data/original) folder.

## Data Preparation

The data powering the dashboard is the result of a cleansing process described in the notebooks of the [data-preparation](./data-preparation) folder. The folder also contains the docker files required for running the notebooks (e.g., jupyter server, python dependencies).

## Dashboard

The dashboard is a [Dash.plotly](http://dash.plotly.com/) application. The code is in the [visual-exploration-demo](./visual-exploration-demo) folder.


## Other Works Based on this Project

This work was the basis for the [GreenHome](./GreenHome.pdf) system, a CO2 and energy consumption prediction and metering platform, developped by [Maysaa Khalil](https://www.linkedin.com/in/mkhalil2208/) as part of her master final project.
