# MeMAD cross-lingual content retrieval experiments

This repository is a **work in progress**, but will eventually contain the combined scripts and models related to MeMAD automatic cross-lingual content retrieval experiments.

## Dependencies

* [`zet >= 0.9.3`](http://www.seg.rmit.edu.au/zettair/)
* [ImageCLEF Wikipedia image retrieval 2010-2011 dataset](https://www.imageclef.org/wikidata)

## Usage

Before you run any of the scripts, make sure you edit the configuration file `paths.conf`, so that the variables point to the correct paths for your system.

The scripts responsible for building the experimental settings require modules from the [ImageCLEF Wikipedia image retrieval 2010-2011 dataset](https://www.imageclef.org/wikidata). First, register to the dataset management system linked from the dataset page, and log in to get the credentials provided to you for resource access. Using those credentials, download the distributed archive files for the [image collection](http://medgift.hevs.ch/wikipediaMM/2010-2011/images/) (`1.tar.gz` through `26.tar.gz`), the corresponding [visual features](http://medgift.hevs.ch/wikipediaMM/2010-2011/features.zip) (`features.zip`) and [text metadata](http://medgift.hevs.ch/wikipediaMM/2010-2011/all_text.zip) (`metadata.zip`), and the [2011 topic metadata](http://medgift.hevs.ch/wikipediaMM/2010-2011/wikipedia_topics_2011.zip) (`wikipedia_topics_2011.zip`) including [visual features for the example images](http://medgift.hevs.ch/wikipediaMM/2010-2011/wikipedia_topic_examples_features_2011.zip) (`wikipedia_topic_examples_features_2011.zip`). Afterwards, place the archives into a common directory and change the path variable `WIKIDATA-DIR` in the file `paths.conf` to point to that directory. Finally, extract each archive into a subfolder of its own (e.g. `features/`) named after the archive file (`features.zip`). Extract the image archives altogether into a subfolder named `images/`, rather than `1/ through 26/`.
