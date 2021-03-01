# MeMAD cross-lingual content retrieval experiments

This repository is a **work in progress**, but will eventually contain the combined scripts and models related to MeMAD automatic cross-lingual content retrieval experiments.

## Dependencies

* [`zet >= 0.9.3`](http://www.seg.rmit.edu.au/zettair/)
* [ImageCLEF Wikipedia image retrieval 2010-2011 dataset](https://www.imageclef.org/wikidata)

## Usage

Before you run any of the scripts, make sure you edit the configuration file `paths.conf`, so that the variables point to the correct paths for your system.

### Downloading and staging the Wikipedia data

The scripts responsible for building the experimental settings require modules from the [ImageCLEF Wikipedia image retrieval 2010-2011 dataset](https://www.imageclef.org/wikidata). First, register to the dataset management system linked from the dataset page, and log in to get the credentials provided to you for resource access. Using those credentials, download the distributed archive files for the [image collection](http://medgift.hevs.ch/wikipediaMM/2010-2011/images/) (`1.tar.gz` through `26.tar.gz`), the corresponding [visual features](http://medgift.hevs.ch/wikipediaMM/2010-2011/features.zip) (`features.zip`) and [text metadata](http://medgift.hevs.ch/wikipediaMM/2010-2011/all_text.zip) (`metadata.zip`), and the [2011 topic metadata](http://medgift.hevs.ch/wikipediaMM/2010-2011/wikipedia_topics_2011.zip) (`wikipedia_topics_2011.zip`) including [visual features for the example images](http://medgift.hevs.ch/wikipediaMM/2010-2011/wikipedia_topic_examples_features_2011.zip) (`wikipedia_topic_examples_features_2011.zip`). Afterwards, place the archives into a common directory and change the path variable `WIKIDATA-DIR` in the file `paths.conf` to point to that directory. Finally, extract each archive into a subfolder of its own (e.g. `features/`) named after the archive file (`features.zip`). Extract the image archives altogether into a subfolder named `images/`, rather than `1/` through `26/`.

### Reproducing data indexed for search

All sets of metadata that have been indexed and used in the MeMAD search performance experiments have been released via the [MeMAD data for automatic cross-lingual retrieval experiments](https://zenodo.org/record/4570072) collection on Zenodo, under the same CC-BY-SA 3.0 license as the original dataset. These deposits can be freely downloaded and extracted in the `data` folder in order to replicate the search indices distributed through this repository (`zettair-index-all.py`).

Alternatively, the whole data may be reproduced using only the original dataset, by downloading and staging the data as instructed, and running the `collate-metadata.py` and `generate-setting-variants.py` scripts in order. The first script should compile `setting-original.json`, and the other one should generate all the other settings.

## Metadata setting URI format

Various views and enrichments of the original metadata have been used to generate the different search indices distributed with this repository. The name of each variant is a URI indicating the composition of the corresponding data.

* `setting-original`: The metadata from the original dataset, without any changes.
* `setting-masked`: Images with multilingual metadata were only allowed to keep one language.
* `*-only-qrels`: Excludes images for which the original data did not have any relevance annotations.
* `*.autocaps`: Adds automatically-generated captions for each image, for each language for which it had metadata.
* `*.translations`: Adds translations in the two other languages for each metadata stratum of each image.
* `*.fully-enriched`: Adds both automatically-generated captions and metadata translations.
