# Vanilla Steel Case Study

*Author*: Liam Tharp

## Installation & Usage

To install this project, please ensure you have the [latest version of Poetry](https://python-poetry.org/docs/ "Poetry's installation docs"). Install the necessary dependencies using:

```sh
poetry install
```

If Poetry is not installed, you can alternatively install dependencies using `pip`:

```sh
pip install -r requirements.txt
```

Once the dependencies are installed, you can reproduce the output files by running the [`vanilla_steel/parse.py`](vanilla_steel/parse.py) script:

```sh
python vanilla_steel/parse.py
```

## Project Structure

The project is organized to facilitate future development as a stand-alone module. The main components are within the `vanilla_steel` directory, containing three key files:

- **[parse.py](vanilla_steel/parse.py)**: This script serves as the core of the ETL pipeline. The extraction is handled by a custom function, `parse_xlsx_file`, defined in [utils.py](vanilla_steel/utils.py). Each source file is transformed through separate functions (`parse_source{n}` where `n` is 1, 2, or 3), producing two dictionaries: `order_info` and `metadata`. These are then exported as static CSV files, including a joined version (`joined.csv`) for convenience.

- **[eda.py](vanilla_steel/eda.py)**: This script was used for initial data exploration. While traditional methods like summary statistics or word clouds were not utilized, I found directly interacting with the `.xlsx` files in Excel more insightful. This script evolved alongside the [`utils.py:parse_xlsx_file`](vanilla_steel/utils.py#11) function.

- **[utils.py](vanilla_steel/utils.py)**: This utility file contains three primary functions:
    - `parse_xlsx_files`: Takes a file path and returns a list of tables ordered by their sheet within the Excel file. Tables are identified based on a threshold parameter, which determines when a new table starts based on missing values.
    - `extract_material_info`: Parses material strings against predefined regex patterns, returning the best match (or none).
    - `generate_metadata_id`: Creates a unique ID based on an entire metadata dictionary, ensuring consistency in data linking.

### Outputs:

Under the outputs folder there are 3 different files:

- **metadata.csv**: the extracted metdata from the orders
- **order_info.csv**: information about the quantity available to be ordered.
- **joined.csv**: both the metadata and the order information joined together using the `metadata_id` for ease of viewing together.

## Discussion

I completed most of the steps outlined in the project description, but I did not implement machine-learning methods as I felt that developing a full fine-tuning pipeline was beyond the scope of this case study. However, I have experience building pipelines with spaCy, including rules-based systems and entity linking for knowledge graphs, which I’d be happy to discuss in more detail during an interview.

### Design Decisions

I chose to separate the data into `order_info` and `metadata`, linking them via a `metadata_id`. This decision was made to distinguish between the intrinsic qualities of the data (metadata) and the extrinsic ones (order details). This separation allows for easier updates to metadata without affecting the order information, which could be advantageous in scenarios where metadata or order quantities change frequently. While integrating more metadata into the order information, such as 'quality' or 'class', might benefit sales teams, this would require deeper internal knowledge.

### Feature Engineering: Regex vs. SpaCy

The decision to use regex patterns instead of immediately employing a machine learning approach was based on the nature of the task. Given the structured format of the supplier data and the well-defined patterns within it, regex offered a quick and efficient way to extract features with minimal overhead. This approach allowed for rapid prototyping and immediate results without the need for extensive training data. However, recognizing the limitations of regex, I outlined a potential transition to a more scalable and robust solution using spaCy for future iterations.

If I were to use spaCy for feature engineering, I would follow these steps:

#### spaCy: NER Steps
- **Rules-Based Matching**: Start with [spaCy's rules-based matching](https://spacy.io/usage/rule-based-matching) to bootstrap the data collection process.
- **Matcher**: Define various patterns using the [spaCy matcher API](https://spacy.io/api/matcher). The regexes I created would be converted to dictionaries compatible with spaCy’s token-based system, offering more powerful pattern matching.
- **Scaling**: Use the matcher to generate "named" custom spans. Once a sufficient amount of data is collected, these spans could train a spaCy model (specifically en_core_web_trf) or another classification model. 
- **Active Learning**: Once the system has been created, you can have the model flag uncertain results for human evaluation, then a Matcher pattern can be created, and the model fine-tuned to improve performance.
- **Evaluation**: Standard evaluation metrics for the classification model would be used: precision, recall, F1. 

## Next Steps

This project represents a solid first draft of an ETL pipeline for data ingestion. There are several avenues for future improvement, including:

- **Clustering/Dimensionality Reduction**: Group different coatings and classes under a consistent internal hierarchy. This could be achieved through unsupervised clustering, using a training set of previous order fulfillments.
- **Pipeline Enhancement**: While the current code is manually tailored for each type of import, it could be improved by introducing a customizable input format, such as a YAML file, to map input fields directly to output fields.
- **Industry-Specific Term Translation**: As different suppliers might use varied terminologies for similar concepts (e.g., different names for the same material or component), developing a translation layer for industry-specific terms would be highly beneficial. This could involve creating a dictionary or lookup table that maps different supplier-specific terms to a standardized industry term. Additionally, a machine learning approach could be implemented to automatically learn these mappings over time, improving the accuracy and consistency of the data across various sources.
- **Automated Data Validation**: Implementing automated checks to validate the integrity and consistency of the data during the ETL process could help prevent errors and ensure higher quality outputs.
- **Advanced Analytics**: Once the data is consistently structured, it could be leveraged for more advanced analytics, such as predictive modeling for demand forecasting or supplier performance analysis.
