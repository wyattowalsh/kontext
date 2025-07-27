This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: docs/**/*.{md,markdown,rmd,mdx,rst,rest,txt,adoc,asciidoc}
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
docs/
  concepts/
    architecture.md
    chunking.md
    confidence_scores.md
    docling_document.md
    index.md
    plugins.md
    serialization.md
  examples/
    index.md
  faq/
    index.md
  installation/
    index.md
  integrations/
    .template.md
    apify.md
    bee.md
    cloudera.md
    crewai.md
    data_prep_kit.md
    docetl.md
    haystack.md
    index.md
    instructlab.md
    kotaemon.md
    langchain.md
    llamaindex.md
    nvidia.md
    opencontracts.md
    openwebui.md
    prodigy.md
    rhel_ai.md
    spacy.md
    txtai.md
    vectara.md
  reference/
    cli.md
    docling_document.md
    document_converter.md
    pipeline_options.md
  usage/
    enrichments.md
    index.md
    supported_formats.md
    vision_models.md
  index.md
  v2.md
```

# Files

## File: docs/concepts/architecture.md
````markdown
![docling_architecture](../assets/docling_arch.png)

In a nutshell, Docling's architecture is outlined in the diagram above.

For each document format, the *document converter* knows which format-specific *backend* to employ for parsing the document and which *pipeline* to use for orchestrating the execution, along with any relevant *options*.

!!! tip

    While the document converter holds a default mapping, this configuration is parametrizable, so e.g. for the PDF format, different backends and different pipeline options can be used — see [Usage](../usage/index.md#adjust-pipeline-features).

The *conversion result* contains the [*Docling document*](./docling_document.md), Docling's fundamental document representation.

Some typical scenarios for using a Docling document include directly calling its *export methods*, such as for markdown, dictionary etc., or having it serialized by a
[*serializer*](./serialization.md) or chunked by a [*chunker*](./chunking.md).

For more details on Docling's architecture, check out the [Docling Technical Report](https://arxiv.org/abs/2408.09869).

!!! note

    The components illustrated with dashed outline indicate base classes that can be subclassed for specialized implementations.
````

## File: docs/concepts/chunking.md
````markdown
## Introduction

!!! note "Chunking approaches"

    Starting from a `DoclingDocument`, there are in principle two possible chunking
    approaches:

    1. exporting the `DoclingDocument` to Markdown (or similar format) and then
      performing user-defined chunking as a post-processing step, or
    2. using native Docling chunkers, i.e. operating directly on the `DoclingDocument`

    This page is about the latter, i.e. using native Docling chunkers.
    For an example of using approach (1) check out e.g.
    [this recipe](../examples/rag_langchain.ipynb) looking at the Markdown export mode.

A *chunker* is a Docling abstraction that, given a
[`DoclingDocument`](./docling_document.md), returns a stream of chunks, each of which
captures some part of the document as a string accompanied by respective metadata.

To enable both flexibility for downstream applications and out-of-the-box utility,
Docling defines a chunker class hierarchy, providing a base type, `BaseChunker`, as well
as specific subclasses.

Docling integration with gen AI frameworks like LlamaIndex is done using the
`BaseChunker` interface, so users can easily plug in any built-in, self-defined, or
third-party `BaseChunker` implementation.

## Base Chunker

The `BaseChunker` base class API defines that any chunker should provide the following:

- `def chunk(self, dl_doc: DoclingDocument, **kwargs) -> Iterator[BaseChunk]`:
  Returning the chunks for the provided document.
- `def contextualize(self, chunk: BaseChunk) -> str`:
  Returning the potentially metadata-enriched serialization of the chunk, typically
  used to feed an embedding model (or generation model).

## Hybrid Chunker

!!! note "To access `HybridChunker`"

    - If you are using the `docling` package, you can import as follows:
        ```python
        from docling.chunking import HybridChunker
        ```
    - If you are only using the `docling-core` package, you must ensure to install
        the `chunking` extra if you want to use HuggingFace tokenizers, e.g.
        ```shell
        pip install 'docling-core[chunking]'
        ```
        or the `chunking-openai` extra if you prefer Open AI tokenizers (tiktoken), e.g.
        ```shell
        pip install 'docling-core[chunking-openai]'
        ```
        and then you
        can import as follows:
        ```python
        from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
        ```

The `HybridChunker` implementation uses a hybrid approach, applying tokenization-aware
refinements on top of document-based [hierarchical](#hierarchical-chunker) chunking.

More precisely:

- it starts from the result of the hierarchical chunker and, based on the user-provided
  tokenizer (typically to be aligned to the embedding model tokenizer), it:
- does one pass where it splits chunks only when needed (i.e. oversized w.r.t.
tokens), &
- another pass where it merges chunks only when possible (i.e. undersized successive
chunks with same headings & captions) — users can opt out of this step via param
`merge_peers` (by default `True`)

👉 Usage examples:

- [Hybrid chunking](../examples/hybrid_chunking.ipynb)
- [Advanced chunking & serialization](../examples/advanced_chunking_and_serialization.ipynb)

## Hierarchical Chunker

The `HierarchicalChunker` implementation uses the document structure information from
the [`DoclingDocument`](./docling_document.md) to create one chunk for each individual
detected document element, by default only merging together list items (can be opted out
via param `merge_list_items`). It also takes care of attaching all relevant document
metadata, including headers and captions.
````

## File: docs/concepts/confidence_scores.md
````markdown
## Introduction

**Confidence grades** were introduced in [v2.34.0](https://github.com/docling-project/docling/releases/tag/v2.34.0) to help users understand how well a conversion performed and guide decisions about post-processing workflows. They are available in the [`confidence`](../../reference/document_converter/#docling.document_converter.ConversionResult.confidence) field of the [`ConversionResult`](../../reference/document_converter/#docling.document_converter.ConversionResult) object returned by the document converter.

## Purpose

Complex layouts, poor scan quality, or challenging formatting can lead to suboptimal document conversion results that may require additional attention or alternative conversion pipelines.

Confidence scores provide a quantitative assessment of document conversion quality. Each confidence report includes a **numerical score** (0.0 to 1.0) measuring conversion accuracy, and a **quality grade** (poor, fair, good, excellent) for quick interpretation.

!!! note "Focus on quality grades!"

    Users can and should safely focus on the document-level grade fields — `mean_grade` and `low_grade` — to assess overall conversion quality. Numerical scores are used internally and are for informational purposes only; their computation and weighting may change in the future.

Use cases for confidence grades include:

- Identify documents requiring manual review after the conversion
- Adjust conversion pipelines to the most appropriate for each document type
- Set confidence thresholds for unattended batch conversions
- Catch potential conversion issues early in your workflow.

## Concepts

### Scores and grades

A confidence report contains *scores* and *grades*:

- **Scores**: Numerical values between 0.0 and 1.0, where higher values indicate better conversion quality, for internal use only
- **Grades**: Categorical quality assessments based on score thresholds, used to assess the overall conversion confidence:
  - `POOR`
  - `FAIR`
  - `GOOD`
  - `EXCELLENT`

### Types of confidence calculated

Each confidence report includes four component scores and grades:

- **`layout_score`**: Overall quality of document element recognition 
- **`ocr_score`**: Quality of OCR-extracted content
- **`parse_score`**: 10th percentile score of digital text cells (emphasizes problem areas)
- **`table_score`**: Table extraction quality *(not yet implemented)*

### Summary grades

Two aggregate grades provide overall document quality assessment:

- **`mean_grade`**: Average of the four component scores
- **`low_grade`**: 5th percentile score (highlights worst-performing areas)

### Page-level vs document-level

Confidence grades are calculated at two levels:

- **Page-level**: Individual scores and grades for each page, stored in the `pages` field
- **Document-level**: Overall scores and grades for the entire document, calculated as averages of the page-level grades and stored in fields equally named in the root [`ConfidenceReport`](h../../reference/document_converter/#docling.document_converter.ConversionResult.confidence)

### Example

![confidence_scores](../assets/confidence_scores.png)
````

## File: docs/concepts/docling_document.md
````markdown
With Docling v2, we introduce a unified document representation format called `DoclingDocument`. It is defined as a
pydantic datatype, which can express several features common to documents, such as:

* Text, Tables, Pictures, and more
* Document hierarchy with sections and groups
* Disambiguation between main body and headers, footers (furniture)
* Layout information (i.e. bounding boxes) for all items, if available
* Provenance information

The definition of the Pydantic types is implemented in the module `docling_core.types.doc`, more details in [source code definitions](https://github.com/docling-project/docling-core/tree/main/docling_core/types/doc).

It also brings a set of document construction APIs to build up a `DoclingDocument` from scratch.

## Example document structures

To illustrate the features of the `DoclingDocument` format, in the subsections below we consider the
`DoclingDocument` converted from `tests/data/word_sample.docx` and we present some side-by-side comparisons,
where the left side shows snippets from the converted document
serialized as YAML and the right one shows the corresponding parts of the original MS Word.

### Basic structure

A `DoclingDocument` exposes top-level fields for the document content, organized in two categories.
The first category is the _content items_, which are stored in these fields:

- `texts`: All items that have a text representation (paragraph, section heading, equation, ...). Base class is `TextItem`.
- `tables`: All tables, type `TableItem`. Can carry structure annotations.
- `pictures`: All pictures, type `PictureItem`. Can carry structure annotations.
- `key_value_items`: All key-value items.

All of the above fields are lists and store items inheriting from the `DocItem` type. They can express different
data structures depending on their type, and reference parents and children through JSON pointers.

The second category is _content structure_, which is encapsulated in:

- `body`: The root node of a tree-structure for the main document body
- `furniture`: The root node of a tree-structure for all items that don't belong into the body (headers, footers, ...)
- `groups`: A set of items that don't represent content, but act as containers for other content items (e.g. a list, a chapter)

All of the above fields are only storing `NodeItem` instances, which reference children and parents
through JSON pointers.

The reading order of the document is encapsulated through the `body` tree and the order of _children_ in each item
in the tree.

Below example shows how all items in the first page are nested below the `title` item (`#/texts/1`).

![doc_hierarchy_1](../assets/docling_doc_hierarchy_1.png)

### Grouping

Below example shows how all items under the heading "Let's swim" (`#/texts/5`) are nested as children. The children of
"Let's swim" are both text items and groups, which contain the list elements. The group items are stored in the
top-level `groups` field.

![doc_hierarchy_2](../assets/docling_doc_hierarchy_2.png)

<!--
### Tables

TBD

### Pictures

TBD

### Provenance

TBD
 -->
````

## File: docs/concepts/index.md
````markdown
Use the navigation on the left to browse through some core Docling concepts.
````

## File: docs/concepts/plugins.md
````markdown
Docling allows to be extended with third-party plugins which extend the choice of options provided in several steps of the pipeline.

Plugins are loaded via the [pluggy](https://github.com/pytest-dev/pluggy/) system which allows third-party developers to register the new capabilities using the [setuptools entrypoint](https://setuptools.pypa.io/en/latest/userguide/entry_point.html#entry-points-for-plugins).

The actual entrypoint definition might vary, depending on the packaging system you are using. Here are a few examples:

=== "pyproject.toml"

    ```toml
    [project.entry-points."docling"]
    your_plugin_name = "your_package.module"
    ```

=== "poetry v1 pyproject.toml"

    ```toml
    [tool.poetry.plugins."docling"]
    your_plugin_name = "your_package.module"
    ```

=== "setup.cfg"

    ```ini
    [options.entry_points]
    docling =
        your_plugin_name = your_package.module
    ```

=== "setup.py"

    ```py
    from setuptools import setup

    setup(
        # ...,
        entry_points = {
            'docling': [
                'your_plugin_name = "your_package.module"'
            ]
        }
    )
    ```

- `your_plugin_name` is the name you choose for your plugin. This must be unique among the broader Docling ecosystem.
- `your_package.module` is the reference to the module in your package which is responsible for the plugin registration.

## Plugin factories

### OCR factory

The OCR factory allows to provide more OCR engines to the Docling users.

The content of `your_package.module` registers the OCR engines with a code similar to:

```py
# Factory registration
def ocr_engines():
    return {
        "ocr_engines": [
            YourOcrModel,
        ]
    }
```

where `YourOcrModel` must implement the [`BaseOcrModel`](https://github.com/docling-project/docling/blob/main/docling/models/base_ocr_model.py#L23) and provide an options class derived from [`OcrOptions`](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L105).

If you look for an example, the [default Docling plugins](https://github.com/docling-project/docling/blob/main/docling/models/plugins/defaults.py) is a good starting point.

## Third-party plugins

When the plugin is not provided by the main `docling` package but by a third-party package this have to be enabled explicitly via the `allow_external_plugins` option.

```py
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions()
pipeline_options.allow_external_plugins = True  # <-- enabled the external plugins
pipeline_options.ocr_options = YourOptions  # <-- your options here

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options
        )
    }
)
```

### Using the `docling` CLI

Similarly, when using the `docling` users have to enable external plugins before selecting the new one.

```sh
# Show the external plugins
docling --show-external-plugins

# Run docling with the new plugin
docling --allow-external-plugins --ocr-engine=NAME
```
````

## File: docs/concepts/serialization.md
````markdown
## Introduction

A *document serializer* (AKA simply *serializer*) is a Docling abstraction that is
initialized with a given [`DoclingDocument`](./docling_document.md) and returns a
textual representation for that document.

Besides the document serializer, Docling defines similar abstractions for several
document subcomponents, for example: *text serializer*, *table serializer*,
*picture serializer*, *list serializer*, *inline serializer*, and more.

Last but not least, a *serializer provider* is a wrapper that abstracts the
document serialization strategy from the document instance.

## Base classes

To enable both flexibility for downstream applications and out-of-the-box utility,
Docling defines a serialization class hierarchy, providing:

- base types for the above abstractions: `BaseDocSerializer`, as well as
  `BaseTextSerializer`, `BaseTableSerializer` etc, and `BaseSerializerProvider`, and
- specific subclasses for the above-mentioned base types, e.g. `MarkdownDocSerializer`.

You can review all methods required to define the above base classes [here](https://github.com/docling-project/docling-core/blob/main/docling_core/transforms/serializer/base.py).

From a client perspective, the most relevant is `BaseDocSerializer.serialize()`, which
returns the textual representation, as well as relevant metadata on which document
components contributed to that serialization.

## Use in `DoclingDocument` export methods

Docling provides predefined serializers for Markdown, HTML, and DocTags.

The respective `DoclingDocument` export methods (e.g. `export_to_markdown()`) are
provided as user shorthands — internally directly instantiating and delegating to
respective serializers.

## Examples

For an example showcasing how to use serializers, see
[here](../examples/serialization.ipynb).
````

## File: docs/examples/index.md
````markdown
Use the navigation on the left to browse through examples covering a range of possible workflows and use cases.
````

## File: docs/faq/index.md
````markdown
# FAQ

This is a collection of FAQ collected from the user questions on <https://github.com/docling-project/docling/discussions>.


??? question "Is Python 3.13 supported?"

    ### Is Python 3.13 supported?

    Python 3.13 is supported from Docling 2.18.0.


??? question "Install conflicts with numpy (python 3.13)"

    ### Install conflicts with numpy (python 3.13)

    When using `docling-ibm-models>=2.0.7` and `deepsearch-glm>=0.26.2` these issues should not show up anymore.
    Docling supports numpy versions `>=1.24.4,<3.0.0` which should match all usages.

    **For older versions**

    This has been observed installing docling and langchain via poetry.

    ```
    ...
    Thus, docling (>=2.7.0,<3.0.0) requires numpy (>=1.26.4,<2.0.0).
    So, because ... depends on both numpy (>=2.0.2,<3.0.0) and docling (^2.7.0), version solving failed.
    ```

    Numpy is only adding Python 3.13 support starting in some 2.x.y version. In order to prepare for 3.13, Docling depends on a 2.x.y for 3.13, otherwise depending an 1.x.y version. If you are allowing 3.13 in your pyproject.toml, Poetry will try to find some way to reconcile Docling's numpy version for 3.13 (some 2.x.y) with LangChain's version for that (some 1.x.y) — leading to the error above.

    Check if Python 3.13 is among the Python versions allowed by your pyproject.toml and if so, remove it and try again.
    E.g., if you have python = "^3.10", use python = ">=3.10,<3.13" instead.

    If you want to retain compatibility with python 3.9-3.13, you can also use a selector in pyproject.toml similar to the following

    ```toml
    numpy = [
        { version = "^2.1.0", markers = 'python_version >= "3.13"' },
        { version = "^1.24.4", markers = 'python_version < "3.13"' },
    ]
    ```

    Source: Issue [#283](https://github.com/docling-project/docling/issues/283#issuecomment-2465035868)


??? question "Is macOS x86_64 supported?"

    ### Is macOS x86_64 supported?

    Yes, Docling (still) supports running the standard pipeline on macOS x86_64.

    However, users might get into a combination of incompatible dependencies on a fresh install.
    Because Docling depends on PyTorch which dropped support for macOS x86_64 after the 2.2.2 release,
    and this old version of PyTorch works only with NumPy 1.x, users **must** ensure the correct NumPy version is running.

    ```shell
    pip install docling "numpy<2.0.0"
    ```

    Source: Issue [#1694](https://github.com/docling-project/docling/issues/1694).


??? question "Are text styles (bold, underline, etc) supported?"

    ### Are text styles (bold, underline, etc) supported?

    Currently text styles are not supported in the `DoclingDocument` format.
    If you are interest in contributing this feature, please open a discussion topic to brainstorm on the design.

    _Note: this is not a simple topic_


??? question "How do I run completely offline?"

    ### How do I run completely offline?

    Docling is not using any remote service, hence it can run in completely isolated air-gapped environments.

    The only requirement is pointing the Docling runtime to the location where the model artifacts have been stored.

    For example

    ```py

    pipeline_options = PdfPipelineOptions(artifacts_path="your location")
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    ```

    Source: Issue [#326](https://github.com/docling-project/docling/issues/326)


??? question " Which model weights are needed to run Docling?"
    ### Which model weights are needed to run Docling?

    Model weights are needed for the AI models used in the PDF pipeline. Other document types (docx, pptx, etc) do not have any such requirement.

    For processing PDF documents, Docling requires the model weights from <https://huggingface.co/ds4sd/docling-models>.

    When OCR is enabled, some engines also require model artifacts. For example EasyOCR, for which Docling has [special pipeline options](https://github.com/docling-project/docling/blob/main/docling/datamodel/pipeline_options.py#L68) to control the runtime behavior.


??? question "SSL error downloading model weights"

    ### SSL error downloading model weights

    ```
    URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)>
    ```

    Similar SSL download errors have been observed by some users. This happens when model weights are fetched from Hugging Face.
    The error could happen when the python environment doesn't have an up-to-date list of trusted certificates.

    Possible solutions were

    - Update to the latest version of [certifi](https://pypi.org/project/certifi/), i.e. `pip install --upgrade certifi`
    - Use [pip-system-certs](https://pypi.org/project/pip-system-certs/) to use the latest trusted certificates on your system.
    - Set environment variables `SSL_CERT_FILE` and `REQUESTS_CA_BUNDLE` to the value of `python -m certifi`:
        ```
        CERT_PATH=$(python -m certifi)
        export SSL_CERT_FILE=${CERT_PATH}
        export REQUESTS_CA_BUNDLE=${CERT_PATH}
        ```


??? question "Which OCR languages are supported?"

    ### Which OCR languages are supported?

    Docling supports multiple OCR engine, each one has its own list of supported languages.
    Here is a collection of links to the original OCR engine's documentation listing the OCR languages.

    - [EasyOCR](https://www.jaided.ai/easyocr/)
    - [Tesseract](https://tesseract-ocr.github.io/tessdoc/Data-Files-in-different-versions.html)
    - [RapidOCR](https://rapidai.github.io/RapidOCRDocs/blog/2022/09/28/%E6%94%AF%E6%8C%81%E8%AF%86%E5%88%AB%E8%AF%AD%E8%A8%80/)
    - [Mac OCR](https://github.com/straussmaximilian/ocrmac/tree/main?tab=readme-ov-file#example-select-language-preference)

    Setting the OCR language in Docling is done via the OCR pipeline options:

    ```py
    from docling.datamodel.pipeline_options import PdfPipelineOptions

    pipeline_options = PdfPipelineOptions()
    pipeline_options.ocr_options.lang = ["fr", "de", "es", "en"]  # example of languages for EasyOCR
    ```


??? question "Some images are missing from MS Word and Powerpoint"

    ### Some images are missing from MS Word and Powerpoint

    The image processing library used by Docling is able to handle embedded WMF images only on Windows platform.
    If you are on other operating systems, these images will be ignored.


??? question "`HybridChunker` triggers warning: 'Token indices sequence length is longer than the specified maximum sequence length for this model'"

    ### `HybridChunker` triggers warning: 'Token indices sequence length is longer than the specified maximum sequence length for this model'

    **TLDR**:
    In the context of the `HybridChunker`, this is a known & ancitipated "false alarm".

    **Details**:

    Using the [`HybridChunker`](../concepts/chunking.md#hybrid-chunker) often triggers a warning like this:
    > Token indices sequence length is longer than the specified maximum sequence length for this model (531 > 512). Running this sequence through the model will result in indexing errors

    This is a warning that is emitted by transformers, saying that actually *running this sequence through the model* will result in indexing errors, i.e. the problematic case is only if one indeed passes the particular sequence through the (embedding) model.

    In our case though, this occurs as a "false alarm", since what happens is the following:

    - the chunker invokes the tokenizer on a potentially long sequence (e.g. 530 tokens as mentioned in the warning) in order to count its tokens, i.e. to assess if it is short enough. At this point transformers already emits the warning above!
    - whenever the sequence at hand is oversized, the chunker proceeds to split it (but the transformers warning has already been shown nonetheless)

    What is important is the actual token length of the produced chunks.
    The snippet below can be used for getting the actual maximum chunk size (for users wanting to confirm that this does not exceed the model limit):

    ```python
    chunk_max_len = 0
    for i, chunk in enumerate(chunks):
        ser_txt = chunker.serialize(chunk=chunk)
        ser_tokens = len(tokenizer.tokenize(ser_txt))
        if ser_tokens > chunk_max_len:
            chunk_max_len = ser_tokens
        print(f"{i}\t{ser_tokens}\t{repr(ser_txt[:100])}...")
    print(f"Longest chunk yielded: {chunk_max_len} tokens")
    print(f"Model max length: {tokenizer.model_max_length}")
    ```

    Also see [docling#725](https://github.com/docling-project/docling/issues/725).

    Source: Issue [docling-core#119](https://github.com/docling-project/docling-core/issues/119)


??? question "How to use flash attention?"

    ### How to use flash attention?

    When running models in Docling on CUDA devices, you can enable the usage of the Flash Attention2 library.

    Using environment variables:

    ```
    DOCLING_CUDA_USE_FLASH_ATTENTION2=1
    ```

    Using code:

    ```python
    from docling.datamodel.accelerator_options import (
        AcceleratorOptions,
    )

    pipeline_options = VlmPipelineOptions(
        accelerator_options=AcceleratorOptions(cuda_use_flash_attention2=True)
    )
    ```

    This requires having the [flash-attn](https://pypi.org/project/flash-attn/) package installed. Below are two alternative ways for installing it:

    ```shell
    # Building from sources (required the CUDA dev environment)
    pip install flash-attn

    # Using pre-built wheels (not available in all possible setups)
    FLASH_ATTENTION_SKIP_CUDA_BUILD=TRUE pip install flash-attn
    ```
````

## File: docs/installation/index.md
````markdown
To use Docling, simply install `docling` from your Python package manager, e.g. pip:
```bash
pip install docling
```

Works on macOS, Linux, and Windows, with support for both x86_64 and arm64 architectures.

??? "Alternative PyTorch distributions"

    The Docling models depend on the [PyTorch](https://pytorch.org/) library.
    Depending on your architecture, you might want to use a different distribution of `torch`.
    For example, you might want support for different accelerator or for a cpu-only version.
    All the different ways for installing `torch` are listed on their website <https://pytorch.org/>.

    One common situation is the installation on Linux systems with cpu-only support.
    In this case, we suggest the installation of Docling with the following options

    ```bash
    # Example for installing on the Linux cpu-only version
    pip install docling --extra-index-url https://download.pytorch.org/whl/cpu
    ```

??? "Alternative OCR engines"

    Docling supports multiple OCR engines for processing scanned documents. The current version provides
    the following engines.

    | Engine | Installation | Usage |
    | ------ | ------------ | ----- |
    | [EasyOCR](https://github.com/JaidedAI/EasyOCR) | Default in Docling or via `pip install easyocr`. | `EasyOcrOptions` |
    | Tesseract | System dependency. See description for Tesseract and Tesserocr below.  | `TesseractOcrOptions` |
    | Tesseract CLI | System dependency. See description below. | `TesseractCliOcrOptions` |
    | OcrMac | System dependency. See description below. | `OcrMacOptions` |
    | [RapidOCR](https://github.com/RapidAI/RapidOCR) | Extra feature not included in Default Docling installation can be installed via `pip install rapidocr_onnxruntime` | `RapidOcrOptions` |
    | [OnnxTR](https://github.com/felixdittrich92/OnnxTR) | Can be installed via the plugin system `pip install "docling-ocr-onnxtr[cpu]"`. Please take a look at [docling-OCR-OnnxTR](https://github.com/felixdittrich92/docling-OCR-OnnxTR).| `OnnxtrOcrOptions` |

    The Docling `DocumentConverter` allows to choose the OCR engine with the `ocr_options` settings. For example

    ```python
    from docling.datamodel.base_models import ConversionStatus, PipelineOptions
    from docling.datamodel.pipeline_options import PipelineOptions, EasyOcrOptions, TesseractOcrOptions
    from docling.document_converter import DocumentConverter

    pipeline_options = PipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.ocr_options = TesseractOcrOptions()  # Use Tesseract

    doc_converter = DocumentConverter(
        pipeline_options=pipeline_options,
    )
    ```

    <h3>Tesseract installation</h3>

    [Tesseract](https://github.com/tesseract-ocr/tesseract) is a popular OCR engine which is available
    on most operating systems. For using this engine with Docling, Tesseract must be installed on your
    system, using the packaging tool of your choice. Below we provide example commands.
    After installing Tesseract you are expected to provide the path to its language files using the
    `TESSDATA_PREFIX` environment variable (note that it must terminate with a slash `/`).

    === "macOS (via [Homebrew](https://brew.sh/))"

        ```console
        brew install tesseract leptonica pkg-config
        TESSDATA_PREFIX=/opt/homebrew/share/tessdata/
        echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
        ```

    === "Debian-based"

        ```console
        apt-get install tesseract-ocr tesseract-ocr-eng libtesseract-dev libleptonica-dev pkg-config
        TESSDATA_PREFIX=$(dpkg -L tesseract-ocr-eng | grep tessdata$)
        echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
        ```

    === "RHEL"

        ```console
        dnf install tesseract tesseract-devel tesseract-langpack-eng tesseract-osd leptonica-devel
        TESSDATA_PREFIX=/usr/share/tesseract/tessdata/
        echo "Set TESSDATA_PREFIX=${TESSDATA_PREFIX}"
        ```

    <h3>Linking to Tesseract</h3>
    The most efficient usage of the Tesseract library is via linking. Docling is using
    the [Tesserocr](https://github.com/sirfz/tesserocr) package for this.

    If you get into installation issues of Tesserocr, we suggest using the following
    installation options:

    ```console
    pip uninstall tesserocr
    pip install --no-binary :all: tesserocr
    ```

    <h3>ocrmac installation</h3>

    [ocrmac](https://github.com/straussmaximilian/ocrmac) is using
    Apple's vision(or livetext) framework as OCR backend.
    For using this engine with Docling, ocrmac must be installed on your system.
    This only works on macOS systems with newer macOS versions (10.15+).

    ```console
    pip install ocrmac
    ```

??? "Installation on macOS Intel (x86_64)"

    When installing Docling on macOS with Intel processors, you might encounter errors with PyTorch compatibility.
    This happens because newer PyTorch versions (2.6.0+) no longer provide wheels for Intel-based Macs.

    If you're using an Intel Mac, install Docling with compatible PyTorch
    **Note:** PyTorch 2.2.2 requires Python 3.12 or lower. Make sure you're not using Python 3.13+.

    ```bash
    # For uv users
    uv add torch==2.2.2 torchvision==0.17.2 docling

    # For pip users
    pip install "docling[mac_intel]"

    # For Poetry users
    poetry add docling
    ```

## Development setup

To develop Docling features, bugfixes etc., install as follows from your local clone's root dir:

```bash
uv sync --all-extras
```
````

## File: docs/integrations/.template.md
````markdown
Docling is available as a plugin for [EXAMPLE](https://example.com).

- 💻 [GitHub][github]
- 📖 [Docs][docs]
- 📦 [PyPI][pypi]

[github]: https://github.com/...
[docs]: https://...
[pypi]: https://pypi.org/project/...
````

## File: docs/integrations/apify.md
````markdown
You can run Docling in the cloud without installation using the [Docling Actor][apify] on Apify platform. Simply provide a document URL and get the processed result:

<a href="https://apify.com/vancura/docling?fpr=docling"><img src="https://apify.com/ext/run-on-apify.png" alt="Run Docling Actor on Apify" width="176" height="39" /></a>

```bash
apify call vancura/docling -i '{
  "options": {
    "to_formats": ["md", "json", "html", "text", "doctags"]
  },
  "http_sources": [
    {"url": "https://vancura.dev/assets/actor-test/facial-hairstyles-and-filtering-facepiece-respirators.pdf"},
    {"url": "https://arxiv.org/pdf/2408.09869"}
  ]
}'
```

The Actor stores results in:

* Processed document in key-value store (`OUTPUT_RESULT`)
* Processing logs (`DOCLING_LOG`)
* Dataset record with result URL and status

Read more about the [Docling Actor](.actor/README.md), including how to use it via the Apify API and CLI.

- 💻 [GitHub][github]
- 📖 [Docs][docs]
- 📦 [Docling Actor][apify]

[github]: https://github.com/docling-project/docling/tree/main/.actor/
[docs]: https://github.com/docling-project/docling/tree/main/.actor/README.md
[apify]: https://apify.com/vancura/docling?fpr=docling
````

## File: docs/integrations/bee.md
````markdown
Docling is available as an extraction backend in the [Bee][github] framework.

- 💻 [Bee GitHub][github]
- 📖 [Bee docs][docs]
- 📦 [Bee NPM][package]

[github]: https://github.com/i-am-bee
[docs]: https://i-am-bee.github.io/bee-agent-framework/
[package]: https://www.npmjs.com/package/bee-agent-framework
````

## File: docs/integrations/cloudera.md
````markdown
Docling is available in [Cloudera](https://www.cloudera.com/) through the *RAG Studio*
Accelerator for Machine Learning Projects (AMP).

- 💻 [RAG Studio AMP GitHub][github]

[github]: https://github.com/cloudera/CML_AMP_RAG_Studio
````

## File: docs/integrations/crewai.md
````markdown
Docling is available in [CrewAI](https://www.crewai.com/) as the `CrewDoclingSource`
knowledge source.

- 💻 [Crew AI GitHub][github]
- 📖 [Crew AI knowledge docs][docs]
- 📦 [Crew AI PyPI][package]

[github]: https://github.com/crewAIInc/crewAI/
[docs]: https://docs.crewai.com/concepts/knowledge
[package]: https://pypi.org/project/crewai/
````

## File: docs/integrations/data_prep_kit.md
````markdown
Docling is used by the [Data Prep Kit](https://data-prep-kit.github.io/data-prep-kit/) open-source toolkit for preparing unstructured data for LLM application development ranging from laptop scale to datacenter scale.

## Components
### PDF ingestion to Parquet
- 💻 [Docling2Parquet source](https://github.com/data-prep-kit/data-prep-kit/tree/dev/transforms/language/docling2parquet)
- 📖 [Docling2Parquet docs](https://data-prep-kit.github.io/data-prep-kit/transforms/language/pdf2parquet/)

### Document chunking
- 💻 [Doc Chunking source](https://github.com/data-prep-kit/data-prep-kit/tree/dev/transforms/language/doc_chunk)
- 📖 [Doc Chunking docs](https://data-prep-kit.github.io/data-prep-kit/transforms/language/doc_chunk/)
````

## File: docs/integrations/docetl.md
````markdown
Docling is available as a file conversion method in [DocETL](https://github.com/ucbepic/docetl):

- 💻 [DocETL GitHub][github]
- 📖 [DocETL docs][docs]
- 📦 [DocETL PyPI][pypi]

[github]: https://github.com/ucbepic/docetl
[docs]: https://ucbepic.github.io/docetl/
[pypi]: https://pypi.org/project/docetl/
````

## File: docs/integrations/haystack.md
````markdown
Docling is available as a converter in [Haystack](https://haystack.deepset.ai/):

- 📖 [Docling Haystack integration docs][docs]
- 💻 [Docling Haystack integration GitHub][github]
- 🧑🏽‍🍳 [Docling Haystack integration example][example]
- 📦 [Docling Haystack integration PyPI][pypi]

[github]: https://github.com/docling-project/docling-haystack
[docs]: https://haystack.deepset.ai/integrations/docling
[pypi]: https://pypi.org/project/docling-haystack
[example]: ../examples/rag_haystack.ipynb
````

## File: docs/integrations/index.md
````markdown
Use the navigation on the left to browse through Docling integrations with popular frameworks and tools.


<p align="center">
  <img loading="lazy" alt="Docling" src="../assets/docling_ecosystem.png" width="100%" />
</p>
````

## File: docs/integrations/instructlab.md
````markdown
Docling is powering document processing in [InstructLab][home],
enabling users to unlock the knowledge hidden in documents and present it to
InstructLab's fine-tuning for aligning AI models to the user's specific data.

More details can be found in this [blog post][blog].

- 🏠 [InstructLab home][home]
- 💻 [InstructLab GitHub][github]
- 🧑🏻‍💻 [InstructLab UI][ui]
- 📖 [InstructLab docs][docs]

[home]: https://instructlab.ai
[github]: https://github.com/instructlab
[ui]: https://ui.instructlab.ai/
[docs]: https://docs.instructlab.ai/
[blog]: https://www.redhat.com/en/blog/docling-missing-document-processing-companion-generative-ai
````

## File: docs/integrations/kotaemon.md
````markdown
Docling is available in [Kotaemon](https://cinnamon.github.io/kotaemon/) as the `DoclingReader` loader:

- 💻 [Kotaemon GitHub][github]
- 📖 [DoclingReader docs][docs]
- ⚙️ [Docling setup in Kotaemon][setup]

[github]: https://github.com/Cinnamon/kotaemon
[docs]: https://cinnamon.github.io/kotaemon/reference/loaders/docling_loader/
[setup]: https://cinnamon.github.io/kotaemon/development/?h=docling#setup-multimodal-document-parsing-ocr-table-parsing-figure-extraction
````

## File: docs/integrations/langchain.md
````markdown
Docling is available as an official [LangChain](https://python.langchain.com/) extension.

To get started, check out the [step-by-step guide in LangChain][guide].

- 📖 [LangChain Docling integration docs][docs]
- 💻 [LangChain Docling integration GitHub][github]
- 🧑🏽‍🍳 [LangChain Docling integration example][example]
- 📦 [LangChain Docling integration PyPI][pypi]

[docs]: https://python.langchain.com/docs/integrations/providers/docling/
[github]: https://github.com/docling-project/docling-langchain
[guide]: https://python.langchain.com/docs/integrations/document_loaders/docling/
[example]: ../examples/rag_langchain.ipynb
[pypi]: https://pypi.org/project/langchain-docling/
````

## File: docs/integrations/llamaindex.md
````markdown
Docling is available as an official [LlamaIndex](https://docs.llamaindex.ai/) extension.

To get started, check out the [step-by-step guide in LlamaIndex](https://docs.llamaindex.ai/en/stable/examples/data_connectors/DoclingReaderDemo/).

## Components

### Docling Reader

Reads document files and uses Docling to populate LlamaIndex `Document` objects — either serializing Docling's data model (losslessly, e.g. as JSON) or exporting to a simplified format (lossily, e.g. as Markdown).

- 💻 [Docling Reader GitHub](https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/readers/llama-index-readers-docling)
- 📖 [Docling Reader docs](https://docs.llamaindex.ai/en/stable/api_reference/readers/docling/)
- 📦 [Docling Reader PyPI](https://pypi.org/project/llama-index-readers-docling/)

### Docling Node Parser

Reads LlamaIndex `Document` objects populated in Docling's format by Docling Reader and, using its knowledge of the Docling format, parses them to LlamaIndex `Node` objects for downstream usage in LlamaIndex applications, e.g. as chunks for embedding.

- 💻 [Docling Node Parser GitHub](https://github.com/run-llama/llama_index/tree/main/llama-index-integrations/node_parser/llama-index-node-parser-docling)
- 📖 [Docling Node Parser docs](https://docs.llamaindex.ai/en/stable/api_reference/node_parser/docling/)
- 📦 [Docling Node Parser PyPI](https://pypi.org/project/llama-index-node-parser-docling/)
````

## File: docs/integrations/nvidia.md
````markdown
Docling is powering the NVIDIA *PDF to Podcast* agentic AI blueprint:

- [🏠 PDF to Podcast home](https://build.nvidia.com/nvidia/pdf-to-podcast)
- [💻 PDF to Podcast GitHub](https://github.com/NVIDIA-AI-Blueprints/pdf-to-podcast)
- [📣 PDF to Podcast announcement](https://nvidianews.nvidia.com/news/nvidia-launches-ai-foundation-models-for-rtx-ai-pcs)
- [✍️ PDF to Podcast blog post](https://blogs.nvidia.com/blog/agentic-ai-blueprints/)
````

## File: docs/integrations/opencontracts.md
````markdown
Docling is available an ingestion engine for [OpenContracts](https://github.com/JSv4/OpenContracts), allowing you to use Docling's OCR engine(s), chunker(s), labels, etc. and load them into a platform supporting bulk data extraction, text annotating, and question-answering:

- 💻 [OpenContracts GitHub](https://github.com/JSv4/OpenContracts)
- 📖 [OpenContracts Docs](https://jsv4.github.io/OpenContracts/)
- ▶️ [OpenContracts x Docling PDF annotation screen capture](https://github.com/JSv4/OpenContracts/blob/main/docs/assets/images/gifs/PDF%20Annotation%20Flow.gif)
````

## File: docs/integrations/openwebui.md
````markdown
Docling is available as a plugin for [Open WebUI](https://github.com/open-webui/open-webui).

- 📖 [Docs][docs]
- 💻 [GitHub][github]

[github]: https://github.com/open-webui/open-webui
[docs]: https://docs.openwebui.com/features/document-extraction/docling
````

## File: docs/integrations/prodigy.md
````markdown
Docling is available in [Prodigy][home] as a [Prodigy-PDF plugin][plugin] recipe.

More details can be found in this [blog post][blog].

- 🌐 [Prodigy home][home]
- 🔌 [Prodigy-PDF plugin][plugin]
- 🧑🏽‍🍳 [pdf-spans.manual recipe][recipe]

[home]: https://prodi.gy/
[plugin]: https://prodi.gy/docs/plugins#pdf
[recipe]: https://prodi.gy/docs/plugins#pdf-spans.manual
[blog]: https://explosion.ai/blog/pdfs-nlp-structured-data
````

## File: docs/integrations/rhel_ai.md
````markdown
Docling is powering document processing in [Red Hat Enterprise Linux AI (RHEL AI)](https://rhel.ai),
enabling users to unlock the knowledge hidden in documents and present it to
InstructLab's fine-tuning for aligning AI models to the user's specific data.

- 📣 [RHEL AI 1.3 announcement](https://www.redhat.com/en/about/press-releases/red-hat-delivers-next-wave-gen-ai-innovation-new-red-hat-enterprise-linux-ai-capabilities)
- ✍️ RHEL blog posts:
    - [RHEL AI 1.3 Docling context aware chunking: What you need to know](https://www.redhat.com/en/blog/rhel-13-docling-context-aware-chunking-what-you-need-know)
    - [Docling: The missing document processing companion for generative AI](https://www.redhat.com/en/blog/docling-missing-document-processing-companion-generative-ai)
````

## File: docs/integrations/spacy.md
````markdown
Docling is available in [spaCy](https://spacy.io/) as the *spaCy Layout* plugin.

More details can be found in this [blog post][blog].

- 💻 [SpacyLayout GitHub][github]
- 📖 [SpacyLayout docs][docs]
- 📦 [SpacyLayout PyPI][pypi]

[github]: https://github.com/explosion/spacy-layout
[docs]: https://github.com/explosion/spacy-layout?tab=readme-ov-file#readme
[pypi]: https://pypi.org/project/spacy-layout/
[blog]: https://explosion.ai/blog/pdfs-nlp-structured-data
````

## File: docs/integrations/txtai.md
````markdown
Docling is available as a text extraction backend for [txtai](https://neuml.github.io/txtai/).

- 💻 [txtai GitHub][github]
- 📖 [txtai docs][docs]
- 📖 [txtai Docling backend][integration_docs]

[github]: https://github.com/neuml/txtai
[docs]: https://neuml.github.io/txtai
[integration_docs]: https://neuml.github.io/txtai/pipeline/data/filetohtml/#docling
````

## File: docs/integrations/vectara.md
````markdown
Docling is available as a document parser in [Vectara](https://www.vectara.com/).

- 💻 [Vectara GitHub org](https://github.com/vectara)
    - [vectara-ingest GitHub repo](https://github.com/vectara/vectara-ingest)
- 📖 [Vectara docs](https://docs.vectara.com/)
````

## File: docs/reference/cli.md
````markdown
# CLI reference

This page provides documentation for our command line tools.

::: mkdocs-click
    :module: docling.cli.main
    :command: click_app
    :prog_name: docling
    :style: table
````

## File: docs/reference/docling_document.md
````markdown
# Docling Document

This is an automatic generated API reference of the DoclingDocument type.

::: docling_core.types.doc
    handler: python
    options:
        members:
            - DoclingDocument
            - DocumentOrigin
            - DocItem
            - DocItemLabel
            - ProvenanceItem
            - GroupItem
            - GroupLabel
            - NodeItem
            - PageItem
            - FloatingItem
            - TextItem
            - TableItem
            - TableCell
            - TableData
            - TableCellLabel
            - KeyValueItem
            - SectionHeaderItem
            - PictureItem
            - ImageRef
            - PictureClassificationClass
            - PictureClassificationData
            - RefItem
            - BoundingBox
            - CoordOrigin
            - ImageRefMode
            - Size
        docstring_style: sphinx
        show_if_no_docstring: true
        show_submodules: true
        docstring_section_style: list
        filters: ["!^_"]
        heading_level: 2
        show_root_toc_entry: true
        inherited_members: true
        merge_init_into_class: true
        separate_signature: true
        show_root_heading: true
        show_root_full_path: false
        show_signature_annotations: true
        show_source: false
        show_symbol_type_heading: true
        show_symbol_type_toc: true
        show_labels: false
        signature_crossrefs: true
        summary: true
````

## File: docs/reference/document_converter.md
````markdown
# Document converter

This is an automatic generated API reference of the main components of Docling.

::: docling.document_converter
    handler: python
    options:
        members:
            - DocumentConverter
            - ConversionResult
            - ConversionStatus
            - FormatOption
            - InputFormat
            - PdfFormatOption
            - ImageFormatOption
            - StandardPdfPipeline
            - WordFormatOption
            - PowerpointFormatOption
            - MarkdownFormatOption
            - AsciiDocFormatOption
            - HTMLFormatOption
            - SimplePipeline
        show_if_no_docstring: true
        show_submodules: true
        docstring_section_style: list
        filters: ["!^_"]
        heading_level: 2
        inherited_members: true
        merge_init_into_class: true
        separate_signature: true
        show_root_heading: true
        show_root_full_path: false
        show_signature_annotations: true
        show_source: false
        show_symbol_type_heading: true
        show_symbol_type_toc: true
        signature_crossrefs: true
        summary: true
````

## File: docs/reference/pipeline_options.md
````markdown
# Pipeline options

Pipeline options allow to customize the execution of the models during the conversion pipeline.
This includes options for the OCR engines, the table model as well as enrichment options which
can be enabled with `do_xyz = True`.


This is an automatic generated API reference of the all the pipeline options available in Docling.


::: docling.datamodel.pipeline_options
    handler: python
    options:
        show_if_no_docstring: true
        show_submodules: true
        docstring_section_style: list
        filters: ["!^_"]
        heading_level: 2
        inherited_members: true
        merge_init_into_class: true
        separate_signature: true
        show_root_heading: true
        show_root_full_path: false
        show_signature_annotations: true
        show_source: false
        show_symbol_type_heading: true
        show_symbol_type_toc: true
        signature_crossrefs: true
        summary: true

<!-- ::: docling.document_converter.DocumentConverter
    handler: python
    options:
        show_if_no_docstring: true
        show_submodules: true -->
````

## File: docs/usage/enrichments.md
````markdown
Docling allows to enrich the conversion pipeline with additional steps which process specific document components,
e.g. code blocks, pictures, etc. The extra steps usually require extra models executions which may increase
the processing time consistently. For this reason most enrichment models are disabled by default.

The following table provides an overview of the default enrichment models available in Docling.

| Feature | Parameter | Processed item | Description |
| ------- | --------- | ---------------| ----------- |
| Code understanding | `do_code_enrichment` | `CodeItem` | See [docs below](#code-understanding). |
| Formula understanding | `do_formula_enrichment` | `TextItem` with label `FORMULA` | See [docs below](#formula-understanding). |
| Picture classification | `do_picture_classification` | `PictureItem` | See [docs below](#picture-classification). |
| Picture description | `do_picture_description` | `PictureItem` | See [docs below](#picture-description). |


## Enrichments details

### Code understanding

The code understanding step allows to use advance parsing for code blocks found in the document.
This enrichment model also set the `code_language` property of the `CodeItem`.

Model specs: see the [`CodeFormula` model card](https://huggingface.co/ds4sd/CodeFormula).

Example command line:

```sh
docling --enrich-code FILE
```

Example code:

```py
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_code_enrichment = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document
```

### Formula understanding

The formula understanding step will analize the equation formulas in documents and extract their LaTeX representation.
The HTML export functions in the DoclingDocument will leverage the formula and visualize the result using the mathml html syntax.

Model specs: see the [`CodeFormula` model card](https://huggingface.co/ds4sd/CodeFormula).

Example command line:

```sh
docling --enrich-formula FILE
```

Example code:

```py
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_formula_enrichment = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document
```

### Picture classification

The picture classification step classifies the `PictureItem` elements in the document with the `DocumentFigureClassifier` model.
This model is specialized to understand the classes of pictures found in documents, e.g. different chart types, flow diagrams,
logos, signatures, etc.

Model specs: see the [`DocumentFigureClassifier` model card](https://huggingface.co/ds4sd/DocumentFigureClassifier).

Example command line:

```sh
docling --enrich-picture-classes FILE
```

Example code:

```py
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2
pipeline_options.do_picture_classification = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document
```


### Picture description

The picture description step allows to annotate a picture with a vision model. This is also known as a "captioning" task.
The Docling pipeline allows to load and run models completely locally as well as connecting to remote API which support the chat template.
Below follow a few examples on how to use some common vision model and remote services.


```py
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

pipeline_options = PdfPipelineOptions()
pipeline_options.do_picture_description = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("https://arxiv.org/pdf/2501.17887")
doc = result.document

```

#### Granite Vision model

Model specs: see the [`ibm-granite/granite-vision-3.1-2b-preview` model card](https://huggingface.co/ibm-granite/granite-vision-3.1-2b-preview).

Usage in Docling:

```py
from docling.datamodel.pipeline_options import granite_picture_description

pipeline_options.picture_description_options = granite_picture_description
```

#### SmolVLM model

Model specs: see the [`HuggingFaceTB/SmolVLM-256M-Instruct` model card](https://huggingface.co/HuggingFaceTB/SmolVLM-256M-Instruct).

Usage in Docling:

```py
from docling.datamodel.pipeline_options import smolvlm_picture_description

pipeline_options.picture_description_options = smolvlm_picture_description
```

#### Other vision models

The option class `PictureDescriptionVlmOptions` allows to use any another model from the Hugging Face Hub.

```py
from docling.datamodel.pipeline_options import PictureDescriptionVlmOptions

pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="",  # <-- add here the Hugging Face repo_id of your favorite VLM
    prompt="Describe the image in three sentences. Be consise and accurate.",
)
```

#### Remote vision model

The option class `PictureDescriptionApiOptions` allows to use models hosted on remote platforms, e.g.
on local endpoints served by [VLLM](https://docs.vllm.ai), [Ollama](https://ollama.com/) and others,
or cloud providers like [IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai), etc.

_Note: in most cases this option will send your data to the remote service provider._

Usage in Docling:

```py
from docling.datamodel.pipeline_options import PictureDescriptionApiOptions

# Enable connections to remote services
pipeline_options.enable_remote_services=True  # <-- this is required!

# Example using a model running locally, e.g. via VLLM
# $ vllm serve MODEL_NAME
pipeline_options.picture_description_options = PictureDescriptionApiOptions(
    url="http://localhost:8000/v1/chat/completions",
    params=dict(
        model="MODEL NAME",
        seed=42,
        max_completion_tokens=200,
    ),
    prompt="Describe the image in three sentences. Be consise and accurate.",
    timeout=90,
)
```

End-to-end code snippets for cloud providers are available in the examples section:

- [IBM watsonx.ai](../examples/pictures_description_api.py)


## Develop new enrichment models

Beside looking at the implementation of all the models listed above, the Docling documentation has a few examples
dedicated to the implementation of enrichment models.

- [Develop picture enrichment](../examples/develop_picture_enrichment.py)
- [Develop formula enrichment](../examples/develop_formula_understanding.py)
````

## File: docs/usage/index.md
````markdown
## Conversion

### Convert a single document

To convert individual PDF documents, use `convert()`, for example:

```python
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"  # PDF path or URL
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  # output: "### Docling Technical Report[...]"
```

### CLI

You can also use Docling directly from your command line to convert individual files —be it local or by URL— or whole directories.

```console
docling https://arxiv.org/pdf/2206.01062
```
You can also use 🥚[SmolDocling](https://huggingface.co/ds4sd/SmolDocling-256M-preview) and other VLMs via Docling CLI:
```bash
docling --pipeline vlm --vlm-model smoldocling https://arxiv.org/pdf/2206.01062
```
This will use MLX acceleration on supported Apple Silicon hardware.


To see all available options (export formats etc.) run `docling --help`. More details in the [CLI reference page](../reference/cli.md).

### Advanced options

#### Model prefetching and offline usage

By default, models are downloaded automatically upon first usage. If you would prefer
to explicitly prefetch them for offline use (e.g. in air-gapped environments) you can do
that as follows:

**Step 1: Prefetch the models**

Use the `docling-tools models download` utility:

```sh
$ docling-tools models download
Downloading layout model...
Downloading tableformer model...
Downloading picture classifier model...
Downloading code formula model...
Downloading easyocr models...
Models downloaded into $HOME/.cache/docling/models.
```

Alternatively, models can be programmatically downloaded using `docling.utils.model_downloader.download_models()`.

**Step 2: Use the prefetched models**

```python
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import EasyOcrOptions, PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

artifacts_path = "/local/path/to/models"

pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

Or using the CLI:

```sh
docling --artifacts-path="/local/path/to/models" FILE
```

Or using the `DOCLING_ARTIFACTS_PATH` environment variable:

```sh
export DOCLING_ARTIFACTS_PATH="/local/path/to/models"
python my_docling_script.py
```

#### Using remote services

The main purpose of Docling is to run local models which are not sharing any user data with remote services.
Anyhow, there are valid use cases for processing part of the pipeline using remote services, for example invoking OCR engines from cloud vendors or the usage of hosted LLMs.

In Docling we decided to allow such models, but we require the user to explicitly opt-in in communicating with external services.

```py
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

pipeline_options = PdfPipelineOptions(enable_remote_services=True)
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

When the value `enable_remote_services=True` is not set, the system will raise an exception `OperationNotAllowed()`.

_Note: This option is only related to the system sending user data to remote services. Control of pulling data (e.g. model weights) follows the logic described in [Model prefetching and offline usage](#model-prefetching-and-offline-usage)._

##### List of remote model services

The options in this list require the explicit `enable_remote_services=True` when processing the documents.

- `PictureDescriptionApiOptions`: Using vision models via API calls.


#### Adjust pipeline features

The example file [custom_convert.py](../examples/custom_convert.py) contains multiple ways
one can adjust the conversion pipeline and features.

##### Control PDF table extraction options

You can control if table structure recognition should map the recognized structure back to PDF cells (default) or use text cells from the structure prediction itself.
This can improve output quality if you find that multiple columns in extracted tables are erroneously merged into one.


```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.do_cell_matching = False  # uses text cells predicted from table structure model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

Since docling 1.16.0: You can control which TableFormer mode you want to use. Choose between `TableFormerMode.FAST` (faster but less accurate) and `TableFormerMode.ACCURATE` (default) to receive better quality with difficult table structures.

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

pipeline_options = PdfPipelineOptions(do_table_structure=True)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # use more accurate TableFormer model

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```


#### Impose limits on the document size

You can limit the file size and number of pages which should be allowed to process per document:

```python
from pathlib import Path
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869"
converter = DocumentConverter()
result = converter.convert(source, max_num_pages=100, max_file_size=20971520)
```

#### Convert from binary PDF streams

You can convert PDFs from a binary stream instead of from the filesystem as follows:

```python
from io import BytesIO
from docling.datamodel.base_models import DocumentStream
from docling.document_converter import DocumentConverter

buf = BytesIO(your_binary_stream)
source = DocumentStream(name="my_doc.pdf", stream=buf)
converter = DocumentConverter()
result = converter.convert(source)
```

#### Limit resource usage

You can limit the CPU threads used by Docling by setting the environment variable `OMP_NUM_THREADS` accordingly. The default setting is using 4 CPU threads.


#### Use specific backend converters

!!! note

    This section discusses directly invoking a [backend](../concepts/architecture.md),
    i.e. using a low-level API. This should only be done when necessary. For most cases,
    using a `DocumentConverter` (high-level API) as discussed in the sections above
    should suffice — and is the recommended way.

By default, Docling will try to identify the document format to apply the appropriate conversion backend (see the list of [supported formats](supported_formats.md)).
You can restrict the `DocumentConverter` to a set of allowed document formats, as shown in the [Multi-format conversion](../examples/run_with_formats.py) example.
Alternatively, you can also use the specific backend that matches your document content. For instance, you can use `HTMLDocumentBackend` for HTML pages:

```python
import urllib.request
from io import BytesIO
from docling.backend.html_backend import HTMLDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import InputDocument

url = "https://en.wikipedia.org/wiki/Duck"
text = urllib.request.urlopen(url).read()
in_doc = InputDocument(
    path_or_stream=BytesIO(text),
    format=InputFormat.HTML,
    backend=HTMLDocumentBackend,
    filename="duck.html",
)
backend = HTMLDocumentBackend(in_doc=in_doc, path_or_stream=BytesIO(text))
dl_doc = backend.convert()
print(dl_doc.export_to_markdown())
```

## Chunking

You can chunk a Docling document using a [chunker](../concepts/chunking.md), such as a
`HybridChunker`, as shown below (for more details check out
[this example](../examples/hybrid_chunking.ipynb)):

```python
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker

conv_res = DocumentConverter().convert("https://arxiv.org/pdf/2206.01062")
doc = conv_res.document

chunker = HybridChunker(tokenizer="BAAI/bge-small-en-v1.5")  # set tokenizer as needed
chunk_iter = chunker.chunk(doc)
```

An example chunk would look like this:

```python
print(list(chunk_iter)[11])
# {
#   "text": "In this paper, we present the DocLayNet dataset. [...]",
#   "meta": {
#     "doc_items": [{
#       "self_ref": "#/texts/28",
#       "label": "text",
#       "prov": [{
#         "page_no": 2,
#         "bbox": {"l": 53.29, "t": 287.14, "r": 295.56, "b": 212.37, ...},
#       }], ...,
#     }, ...],
#     "headings": ["1 INTRODUCTION"],
#   }
# }
```
````

## File: docs/usage/supported_formats.md
````markdown
Docling can parse various documents formats into a unified representation (Docling
Document), which it can export to different formats too — check out
[Architecture](../concepts/architecture.md) for more details.

Below you can find a listing of all supported input and output formats.

## Supported input formats

| Format | Description |
|--------|-------------|
| PDF | |
| DOCX, XLSX, PPTX | Default formats in MS Office 2007+, based on Office Open XML |
| Markdown | |
| AsciiDoc | |
| HTML, XHTML | |
| CSV | |
| PNG, JPEG, TIFF, BMP, WEBP | Image formats |

Schema-specific support:

| Format | Description |
|--------|-------------|
| USPTO XML | XML format followed by [USPTO](https://www.uspto.gov/patents) patents |
| JATS XML | XML format followed by [JATS](https://jats.nlm.nih.gov/) articles |
| Docling JSON | JSON-serialized [Docling Document](../concepts/docling_document.md) |

## Supported output formats

| Format | Description |
|--------|-------------|
| HTML | Both image embedding and referencing are supported |
| Markdown | |
| JSON | Lossless serialization of Docling Document |
| Text | Plain text, i.e. without Markdown markers |
| Doctags | |
````

## File: docs/usage/vision_models.md
````markdown
The `VlmPipeline` in Docling allows you to convert documents end-to-end using a vision-language model.

Docling supports vision-language models which output:

- DocTags (e.g. [SmolDocling](https://huggingface.co/ds4sd/SmolDocling-256M-preview)), the preferred choice
- Markdown
- HTML


For running Docling using local models with the `VlmPipeline`:

=== "CLI"

    ```bash
    docling --pipeline vlm FILE
    ```

=== "Python"

    See also the example [minimal_vlm_pipeline.py](./../examples/minimal_vlm_pipeline.py).

    ```python
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.pipeline.vlm_pipeline import VlmPipeline

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_cls=VlmPipeline,
            ),
        }
    )

    doc = converter.convert(source="FILE").document
    ```

## Available local models

By default, the vision-language models are running locally.
Docling allows to choose between the Hugging Face [Transformers](https://github.com/huggingface/transformers) framework and the [MLX](https://github.com/Blaizzy/mlx-vlm) (for Apple devices with MPS acceleration) one.

The following table reports the models currently available out-of-the-box.

| Model instance | Model | Framework | Device | Num pages | Inference time (sec) |
| ---------------|------ | --------- | ------ | --------- | ---------------------|
| `vlm_model_specs.SMOLDOCLING_TRANSFORMERS` | [ds4sd/SmolDocling-256M-preview](https://huggingface.co/ds4sd/SmolDocling-256M-preview) | `Transformers/AutoModelForVision2Seq` | MPS | 1 |  102.212 |
| `vlm_model_specs.SMOLDOCLING_MLX` | [ds4sd/SmolDocling-256M-preview-mlx-bf16](https://huggingface.co/ds4sd/SmolDocling-256M-preview-mlx-bf16) | `MLX`| MPS | 1 |    6.15453 |
| `vlm_model_specs.QWEN25_VL_3B_MLX` | [mlx-community/Qwen2.5-VL-3B-Instruct-bf16](https://huggingface.co/mlx-community/Qwen2.5-VL-3B-Instruct-bf16)  |  `MLX`| MPS | 1 |   23.4951 |
| `vlm_model_specs.PIXTRAL_12B_MLX` | [mlx-community/pixtral-12b-bf16](https://huggingface.co/mlx-community/pixtral-12b-bf16) |  `MLX` | MPS | 1 |  308.856 |
| `vlm_model_specs.GEMMA3_12B_MLX` | [mlx-community/gemma-3-12b-it-bf16](https://huggingface.co/mlx-community/gemma-3-12b-it-bf16) |  `MLX` | MPS | 1 |  378.486 |
| `vlm_model_specs.GRANITE_VISION_TRANSFORMERS` | [ibm-granite/granite-vision-3.2-2b](https://huggingface.co/ibm-granite/granite-vision-3.2-2b) | `Transformers/AutoModelForVision2Seq` | MPS | 1 |  104.75 |
| `vlm_model_specs.PHI4_TRANSFORMERS` | [microsoft/Phi-4-multimodal-instruct](https://huggingface.co/microsoft/Phi-4-multimodal-instruct) | `Transformers/AutoModelForCasualLM` | CPU | 1 | 1175.67 |
| `vlm_model_specs.PIXTRAL_12B_TRANSFORMERS` | [mistral-community/pixtral-12b](https://huggingface.co/mistral-community/pixtral-12b) | `Transformers/AutoModelForVision2Seq` | CPU | 1 | 1828.21 |

_Inference time is computed on a Macbook M3 Max using the example page `tests/data/pdf/2305.03393v1-pg9.pdf`. The comparison is done with the example [compare_vlm_models.py](./../examples/compare_vlm_models.py)._

For choosing the model, the code snippet above can be extended as follow

```python
from docling.datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.datamodel.pipeline_options import (
    VlmPipelineOptions,
)
from docling.datamodel import vlm_model_specs

pipeline_options = VlmPipelineOptions(
    vlm_options=vlm_model_specs.SMOLDOCLING_MLX,  # <-- change the model here
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_cls=VlmPipeline,
            pipeline_options=pipeline_options,
        ),
    }
)

doc = converter.convert(source="FILE").document
```

### Other models

Other models can be configured by directly providing the Hugging Face `repo_id`, the prompt and a few more options.

For example:

```python
from docling.datamodel.pipeline_options_vlm_model import InlineVlmOptions, InferenceFramework, TransformersModelType

pipeline_options = VlmPipelineOptions(
    vlm_options=InlineVlmOptions(
        repo_id="ibm-granite/granite-vision-3.2-2b",
        prompt="Convert this page to markdown. Do not miss any text and only output the bare markdown!",
        response_format=ResponseFormat.MARKDOWN,
        inference_framework=InferenceFramework.TRANSFORMERS,
        transformers_model_type=TransformersModelType.AUTOMODEL_VISION2SEQ,
        supported_devices=[
            AcceleratorDevice.CPU,
            AcceleratorDevice.CUDA,
            AcceleratorDevice.MPS,
        ],
        scale=2.0,
        temperature=0.0,
    )
)
```


## Remote models

Additionally to local models, the `VlmPipeline` allows to offload the inference to a remote service hosting the models.
Many remote inference services are provided, the key requirement is to offer an OpenAI-compatible API. This includes vLLM, Ollama, etc.

More examples on how to connect with the remote inference services can be found in the following examples:

- [vlm_pipeline_api_model.py](./../examples/vlm_pipeline_api_model.py)
````

## File: docs/index.md
````markdown
<p align="center">
  <img loading="lazy" alt="Docling" src="assets/docling_processing.png" width="100%" />
  <a href="https://trendshift.io/repositories/12132" target="_blank"><img src="https://trendshift.io/api/badge/repositories/12132" alt="DS4SD%2Fdocling | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
</p>

[![arXiv](https://img.shields.io/badge/arXiv-2408.09869-b31b1b.svg)](https://arxiv.org/abs/2408.09869)
[![PyPI version](https://img.shields.io/pypi/v/docling)](https://pypi.org/project/docling/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/docling)](https://pypi.org/project/docling/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/pydantic/pydantic/main/docs/badge/v2.json)](https://pydantic.dev)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![License MIT](https://img.shields.io/github/license/docling-project/docling)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/badge/docling/month)](https://pepy.tech/projects/docling)
[![Docling Actor](https://apify.com/actor-badge?actor=vancura/docling?fpr=docling)](https://apify.com/vancura/docling)
[![Chat with Dosu](https://dosu.dev/dosu-chat-badge.svg)](https://app.dosu.dev/097760a8-135e-4789-8234-90c8837d7f1c/ask?utm_source=github)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/10101/badge)](https://www.bestpractices.dev/projects/10101)
[![LF AI & Data](https://img.shields.io/badge/LF%20AI%20%26%20Data-003778?logo=linuxfoundation&logoColor=fff&color=0094ff&labelColor=003778)](https://lfaidata.foundation/projects/)

Docling simplifies document processing, parsing diverse formats — including advanced PDF understanding — and providing seamless integrations with the gen AI ecosystem.

## Features

* 🗂️  Parsing of [multiple document formats][supported_formats] incl. PDF, DOCX, PPTX, XLSX, HTML, WAV, MP3, images (PNG, TIFF, JPEG, ...), and more
* 📑 Advanced PDF understanding incl. page layout, reading order, table structure, code, formulas, image classification, and more
* 🧬 Unified, expressive [DoclingDocument][docling_document] representation format
* ↪️  Various [export formats][supported_formats] and options, including Markdown, HTML, [DocTags](https://arxiv.org/abs/2503.11576) and lossless JSON
* 🔒 Local execution capabilities for sensitive data and air-gapped environments
* 🤖 Plug-and-play [integrations][integrations] incl. LangChain, LlamaIndex, Crew AI & Haystack for agentic AI
* 🔍 Extensive OCR support for scanned PDFs and images
* 👓 Support of several Visual Language Models ([SmolDocling](https://huggingface.co/ds4sd/SmolDocling-256M-preview))
* 🎙️  Support for Audio with Automatic Speech Recognition (ASR) models
* 💻 Simple and convenient CLI

### Coming soon

* 📝 Metadata extraction, including title, authors, references & language
* 📝 Chart understanding (Barchart, Piechart, LinePlot, etc)
* 📝 Complex chemistry understanding (Molecular structures)

## Get started

<div class="grid">
  <a href="concepts/" class="card"><b>Concepts</b><br />Learn Docling fundamentals</a>
  <a href="examples/" class="card"><b>Examples</b><br />Try out recipes for various use cases, including conversion, RAG, and more</a>
  <a href="integrations/" class="card"><b>Integrations</b><br />Check out integrations with popular frameworks and tools</a>
  <a href="reference/document_converter/" class="card"><b>Reference</b><br />See more API details</a>
</div>

## Live assistant

Do you want to leverage the power of AI and get a live support on Docling?
Try out the [Chat with Dosu](https://app.dosu.dev/097760a8-135e-4789-8234-90c8837d7f1c/ask?utm_source=github) functionalities provided by our friends at [Dosu](https://dosu.dev/).

[![Chat with Dosu](https://dosu.dev/dosu-chat-badge.svg)](https://app.dosu.dev/097760a8-135e-4789-8234-90c8837d7f1c/ask?utm_source=github)

## LF AI & Data

Docling is hosted as a project in the [LF AI & Data Foundation](https://lfaidata.foundation/projects/).

### IBM ❤️ Open Source AI

The project was started by the AI for knowledge team at IBM Research Zurich.

[supported_formats]: ./usage/supported_formats.md
[docling_document]: ./concepts/docling_document.md
[integrations]: ./integrations/index.md
````

## File: docs/v2.md
````markdown
## What's new

Docling v2 introduces several new features:

- Understands and converts PDF, MS Word, MS Powerpoint, HTML and several image formats
- Produces a new, universal document representation which can encapsulate document hierarchy
- Comes with a fresh new API and CLI

## Changes in Docling v2

### CLI

We updated the command line syntax of Docling v2 to support many formats. Examples are seen below.
```shell
# Convert a single file to Markdown (default)
docling myfile.pdf

# Convert a single file to Markdown and JSON, without OCR
docling myfile.pdf --to json --to md --no-ocr

# Convert PDF files in input directory to Markdown (default)
docling ./input/dir --from pdf

# Convert PDF and Word files in input directory to Markdown and JSON
docling ./input/dir --from pdf --from docx --to md --to json --output ./scratch

# Convert all supported files in input directory to Markdown, but abort on first error
docling ./input/dir --output ./scratch --abort-on-error

```

**Notable changes from Docling v1:**

- The standalone switches for different export formats are removed, and replaced with `--from` and `--to` arguments, to define input and output formats respectively.
- The new `--abort-on-error` will abort any batch conversion as soon an error is encountered
- The `--backend` option for PDFs was removed

### Setting up a `DocumentConverter`

To accommodate many input formats, we changed the way you need to set up your `DocumentConverter` object.
You can now define a list of allowed formats on the `DocumentConverter` initialization, and specify custom options
per-format if desired. By default, all supported formats are allowed. If you don't provide `format_options`, defaults
will be used for all `allowed_formats`.

Format options can include the pipeline class to use, the options to provide to the pipeline, and the document backend.
They are provided as format-specific types, such as `PdfFormatOption` or `WordFormatOption`, as seen below.

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
    WordFormatOption,
)
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

## Default initialization still works as before:
# doc_converter = DocumentConverter()


# previous `PipelineOptions` is now `PdfPipelineOptions`
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = True
#...

## Custom options are now defined per format.
doc_converter = (
    DocumentConverter(  # all of the below is optional, has internal defaults.
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.IMAGE,
            InputFormat.DOCX,
            InputFormat.HTML,
            InputFormat.PPTX,
        ],  # whitelist formats, non-matching files are ignored.
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options, # pipeline options go here.
                backend=PyPdfiumDocumentBackend # optional: pick an alternative backend
            ),
            InputFormat.DOCX: WordFormatOption(
                pipeline_cls=SimplePipeline # default for office formats and HTML
            ),
        },
    )
)
```

**Note**: If you work only with defaults, all remains the same as in Docling v1.

More options are shown in the following example units:

- [run_with_formats.py](examples/run_with_formats.py)
- [custom_convert.py](examples/custom_convert.py)

### Converting documents

We have simplified the way you can feed input to the `DocumentConverter` and renamed the conversion methods for
better semantics. You can now call the conversion directly with a single file, or a list of input files,
or `DocumentStream` objects, without constructing a `DocumentConversionInput` object first.

* `DocumentConverter.convert` now converts a single file input (previously `DocumentConverter.convert_single`).
* `DocumentConverter.convert_all` now converts many files at once (previously `DocumentConverter.convert`).


```python
...
from docling.datamodel.document import ConversionResult
## Convert a single file (from URL or local path)
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Convert several files at once:

input_files = [
    "tests/data/html/wiki_duck.html",
    "tests/data/docx/word_sample.docx",
    "tests/data/docx/lorem_ipsum.docx",
    "tests/data/pptx/powerpoint_sample.pptx",
    "tests/data/2305.03393v1-pg9-img.png",
    "tests/data/pdf/2206.01062.pdf",
]

# Directly pass list of files or streams to `convert_all`
conv_results_iter = doc_converter.convert_all(input_files) # previously `convert`

```
Through the `raises_on_error` argument, you can also control if the conversion should raise exceptions when first
encountering a problem, or resiliently convert all files first and reflect errors in each file's conversion status.
By default, any error is immediately raised and the conversion aborts (previously, exceptions were swallowed).

```python
...
conv_results_iter = doc_converter.convert_all(input_files, raises_on_error=False) # previously `convert`

```

### Access document structures

We have simplified how you can access and export the converted document data, too. Our universal document representation
is now available in conversion results as a `DoclingDocument` object.
`DoclingDocument` provides a neat set of APIs to construct, iterate and export content in the document, as shown below.

```python
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Inspect the converted document:
conv_result.document.print_element_tree()

## Iterate the elements in reading order, including hierarchy level:
for item, level in conv_result.document.iterate_items():
    if isinstance(item, TextItem):
        print(item.text)
    elif isinstance(item, TableItem):
        table_df: pd.DataFrame = item.export_to_dataframe()
        print(table_df.to_markdown())
    elif ...:
        #...
```

**Note**: While it is deprecated, you can _still_ work with the Docling v1 document representation, it is available as:
```shell
conv_result.legacy_document # provides the representation in previous ExportedCCSDocument type
```

### Export into JSON, Markdown, Doctags
**Note**: All `render_...` methods in `ConversionResult` have been removed in Docling v2,
and are now available on `DoclingDocument` as:

- `DoclingDocument.export_to_dict`
- `DoclingDocument.export_to_markdown`
- `DoclingDocument.export_to_document_tokens`

```python
conv_result: ConversionResult = doc_converter.convert("https://arxiv.org/pdf/2408.09869") # previously `convert_single`

## Export to desired format:
print(json.dumps(conv_res.document.export_to_dict()))
print(conv_res.document.export_to_markdown())
print(conv_res.document.export_to_document_tokens())
```

**Note**: While it is deprecated, you can _still_ export Docling v1 JSON format. This is available through the same
methods as on the `DoclingDocument` type:
```shell
## Export legacy document representation to desired format, for v1 compatibility:
print(json.dumps(conv_res.legacy_document.export_to_dict()))
print(conv_res.legacy_document.export_to_markdown())
print(conv_res.legacy_document.export_to_document_tokens())
```

### Reload a `DoclingDocument` stored as JSON

You can save and reload a `DoclingDocument` to disk in JSON format using the following codes:

```python
# Save to disk:
doc: DoclingDocument = conv_res.document # produced from conversion result...

with Path("./doc.json").open("w") as fp:
    fp.write(json.dumps(doc.export_to_dict())) # use `export_to_dict` to ensure consistency

# Load from disk:
with Path("./doc.json").open("r") as fp:
    doc_dict = json.loads(fp.read())
    doc = DoclingDocument.model_validate(doc_dict) # use standard pydantic API to populate doc

```

### Chunking

Docling v2 defines new base classes for chunking:

- `BaseMeta` for chunk metadata
- `BaseChunk` containing the chunk text and metadata, and
- `BaseChunker` for chunkers, producing chunks out of a `DoclingDocument`.

Additionally, it provides an updated `HierarchicalChunker` implementation, which
leverages the new `DoclingDocument` and provides a new, richer chunk output format, including:

- the respective doc items for grounding
- any applicable headings for context
- any applicable captions for context

For an example, check out [Chunking usage](usage.md#chunking).
````
