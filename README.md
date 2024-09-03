# Vanilla Steel Case Study

*Author*: Liam Tharp


## Installation & Usage

To install this project please ensure you have the [latest version of poetry](https://python-poetry.org/docs/ "Poetry's installation docs"). The necessary dependencies can be installed using:

``` sh 
poetry install
```

If you don't have poetry installed, [you can also install using `pip`](https://pypi.org/project/pip/). 

``` sh
pip install -r requirements.txt
```

After you have installed the files, you should be able to reproduce the files in the `output` folder, by executing the [`vanilla_steel/parse.py`](vanilla_steel/parse.py) script, as:

``` sh
python vanilla_steel/parse.py
```

## Description of Files

The overall project is structured in such a way that in future it could be installed as a stand-alone module / project. The files all fall under the `vanilla_steel` directory. There are 3 files contained, described here:

- **[parse.py](vanilla_steel/parse.py)**: this file is the meat & potatoes of the analysis. This is the 'quick and dirty' method of an ETL pipeline, where the Extraction is done primarily using a custom function I wrote: `parse_xlsx_file`, defined later in the [utils.py](vanilla_steel/utils.py) file. The transformation for each source file is done in a separate function: `parse_source{n}` where `n in [1,2,3]`, this returns two dictionaries, `order_info`, and `metadata`. Finally the loading is done where `order_info`, and `metadata` are exported as static CSV files, and a joined version of them is exported for convenience: `joined.csv`.

- **[eda.py](vanilla_steel/eda.py)**: this was the script used for initial ingestion of the data, I found that actually opening up the files as `.xlsx` files using Excel was more helpful than doing summary statistics, so the typical 'word-cloud' and counting the values / types within each column are not shown here. This script was mostly developed alongside the [`utils.py:parse_xlsx_file`](vanilla_steel/utils.py#11) function.

- **[utils.py](vanilla_steel/utils.py)**: this is the utility file section, there are 3 functions of note (and some helper functions). 

    - `parse_xlsx_files`: this function takes a file path, and exports a list of all of the tables ordered by the excel sheet they are contained within. It does this by assuming that any time more than 2 values are missing (the delta of non-missing values between consecutive rows > threshold) a table is defined. This `threshold` is a parameter and can be fine-tuned.
    - `extract_material_info`: takes a material string, and attempts to parse it against several pre-defined regex patterns, and returns the most successful match (or none). 
    - `generate_metadata_id`: this function is created for consistency, it generates a unique id based on an entire metadata dictionary, which will allow matching.


## Discussion

I successfully completed most of the steps in the original description, however I did not employ the machine-learning methods described. I believe developing an entire fine-tuning pipeline to be outside of the scope of a case-study. I have developed pipelines with spaCy using rules-based systems as well as doing entity-linking for the creation of a knowledge graph using [spacy-dbpedia-spotlight](https://pypi.org/project/spacy-dbpedia-spotlight/0.2.0/) which I am happy to discuss further in an interview!

### Design decision

I made the decision to biforcate the data into `order_info` and `metadata`, and have them be linked by `metadata_id`, which can easily join back in the data. This decision was made to separate out the intrinsic and extrinsic qualities of the data. The quantity information (and unit), are extrinsic properties: dependent on the amount in the order, but the metadata is intrinsic to the object itself.

This was an arbitrary distinction made, but it would allow you to change the metadata easily, possibly avoiding other headaches down the line when metadata or order quantities are revised. It is likely that keeping more metadata information with the order information such as 'quality' or 'class' would prove useful to a sales person, but this would require more internal knowledge.

### Feature Engineering: regex vs. spacy

Instead of feature engineering using spaCy NER with tagging + fine-tuning, multiple regular expression (regex) strings were created, which were able to satisfactorily extract the necessary features.

If the feature engineering / extraction were to be done with spacy, the exact steps I would take are as follows:

#### spaCy: NER steps
- Since the number of patterns to be matched will likely be small, I would begin by using [spacy rules-based matching](https://spacy.io/usage/rule-based-matching). As is suggested on this page, you can use this to _bootstrap_ your data collection process.
- **Matcher**: I would begin by definine various patterns according to the [spaCy matcher api](https://spacy.io/api/matcher), these have already been pre-created (at least a starting point) by the tagged regexes. These regexes have to be converted to dictionaries that work on tokens, but theoretically should be more powerful. 
- **Scaling**: This matcher can be used to generate "named" custom spans, and once a sufficiently large number of these has been collected, you can use these spans to train a spaCy NER model, or another classification model.

## Next Steps:

What I completed here was a good first draft at an ETL pipeline for ingestion of the data. There is significant value to be gained in further feature engineering, such as grouping the `Quality` together, to possibly a more useful metric to the sales team, such as a heuristic 'high-quality', 'medium-quality', 'low-quality'. 

- **Clustering / Dimensionality Reduction**: grouping various different coatings and classes, which will be named differently according to suppliers, and categorizing them according to an internal hierarchy would provide a lot of value. This can be done with unsupervised clustering, likely with a training set of previous order fulfillments.
- **Pipeline Improvement**: I wrote the code by hand for each type of import, likely some kind of pre-defined but easily customizable input could be generated, such as a YAML file which maps input fields directly to output fields.
