# codepress

Transforming code into clean, readable text with precision and style.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
    - [Basic Usage](#basic-usage)
    - [Options](#options)
    - [Examples](#examples)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Introduction

**codepress** is a powerful command-line tool designed to transform your codebase into clean, readable text. Whether you're preparing documentation, creating code snippets for tutorials, or simply organizing your projects, codepress ensures that your code is presented with precision and style. Additionally, it provides token usage analysis to help you understand the size and complexity of your codebase.

## Features

- **Recursive File Processing**: Walk through directories to process multiple files effortlessly.
- **Flexible Output Formats**: Generate output in plain text or JSON formats.
- **Customizable Output Styles**: Define how your code and file information are formatted.
- **Gitignore Support**: Automatically respect `.gitignore` patterns to exclude unwanted files.
- **Line Truncation**: Limit the number of lines read from each file to manage large files efficiently.
- **Token Usage Analysis**: Inspect and visualize token counts for files in your project.
- **Verbose Logging**: Get detailed logs to monitor the processing flow.
- **Extensible**: Easily integrate with other tools and workflows.

## Installation

Ensure you have Python **3.11** or higher installed.

1. **Clone the Repository**

   ```bash
   git clone https://github.com/allen2c/codepress.git
   cd codepress
   ```

2. **Install Dependencies**

   Using [Poetry](https://python-poetry.org/):

   ```bash
   poetry install
   ```

   Alternatively, using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

3. **Build and Install**

   ```bash
   poetry build
   poetry install
   ```

## Usage

Once installed, you can use `codepress` via the command line.

### Basic Usage

```bash
codepress [OPTIONS] [PATH]
```

- **PATH**: The directory or file to process. Defaults to the current directory (`.`).

### Options

- `--ignore TEXT`
  Patterns to ignore. Can be specified multiple times.

- `--ignore-hidden / --no-ignore-hidden`
  Ignore hidden files and directories. Default is `--ignore-hidden`.

- `--enable-gitignore / --no-enable-gitignore`
  Enable `.gitignore` patterns. Default is `--enable-gitignore`.

- `--truncate-lines INTEGER`
  Number of lines to read from each file. Default is `5000`.

- `--output-format [text|json]`
  Output format. Choices are `text` or `json`. Default is `text`.

- `--output-style TEXT`
  Output style. Default is `codepress:DEFAULT_CONTENT_STYLE`. Skip style if output format is `json`.

- `--output PATH`
  Output file. Defaults to `stdout` if not specified.

- `--inspect`
  Show files with total token count and usage summary.

- `--verbose / --no-verbose`
  Enable verbose output. Default is `--no-verbose`.

- `--help`
  Show the help message and exit.

### Examples

1. **Process the Current Directory**

   ```bash
   codepress
   ```

2. **Process a Specific Directory with Verbose Logging**

   ```bash
   codepress ./my_project --verbose
   ```

3. **Ignore Specific Patterns**

   ```bash
   codepress ./my_project --ignore "*.pyc" --ignore "__pycache__/"
   ```

4. **Output to a File in JSON Format**

   ```bash
   codepress ./my_project --output-format json --output output.json
   ```

5. **Limit the Number of Lines Read from Each File**

   ```bash
   codepress ./my_project --truncate-lines 1000
   ```

6. **Disable Gitignore Support**

   ```bash
   codepress ./my_project --no-enable-gitignore
   ```

7. **Inspect Token Usage**

   ```bash
   codepress ./my_project --inspect
   ```

## Configuration

You can customize the output style by modifying or creating your own styles. The default style is defined in `codepress/__init__.py` as `DEFAULT_CONTENT_STYLE`. To use a custom style, specify it using the `--output-style` option in the format `module:VARIABLE_NAME`.

Example:

```bash
codepress ./my_project --output-style mymodule:MY_CUSTOM_STYLE
```

Ensure that your custom style variable is defined and accessible within the specified module.

## Contributing

Contributions are welcome! Whether it's reporting bugs, suggesting features, or submitting pull requests, your support helps make codepress better.

1. **Fork the Repository**

2. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Make Your Changes**

4. **Commit Your Changes**

   ```bash
   git commit -m "Add your message"
   ```

5. **Push to the Branch**

   ```bash
   git push origin feature/YourFeature
   ```

6. **Open a Pull Request**

Please ensure your code follows the project's coding standards and that all tests pass.

## License

This project is licensed under the [MIT License](LICENSE).
