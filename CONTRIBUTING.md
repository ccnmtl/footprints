# Contributing to Footprints

:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

The following is a set of guidelines for contributing to Footprints. These are
mostly guidelines, not rules. Use your best judgement, and feel free to
propose changes to this document in a pull request.

#### Table Of Contents

 - [Code of Conduct](#code-of-conduct)
 - [Question or Problem?](#question)
 - [Issues and Bugs](#issue)
 - [Getting Started](#start)
 - [Coding Rules](#rules)
 - [Making Changes](#changes)
 - [Submitting Changes](#submit)
 - [Further Info](#info)

## <a name="code-of-conduct"></a> Code of Conduct
This project and everyone participating in it is governed by the [Footprints Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior via our [Contact Page](https://footprints.ctl.columbia.edu/contact/).

## <a name="question"></a> Got a Question or Problem?

If you have questions about how to use Footprints, please contact us via 
our [Contact Page](https://footprints.ctl.columbia.edu/contact/).

## <a name="issue"></a> Found an Issue?
If you find a bug in the source code or a mistake in the documentation, you can help us by
submitting an issue to our [GitHub issue tracker](https://github.com/ccnmtl/footprints/issues). 
Even better you can submit a Pull Request with a fix :heart_eyes:.

If you're not sure how to write a bug report, here's a quick guide: 
[Write an Effective Simple Bug Report](https://medium.com/prismapp/write-an-effective-simple-bug-report-c3f8ebe1b72f) 
(4 minutes!).

**Note:** Please don't file an issue to ask a question, please contact us via 
our [Contact Page](https://footprints.ctl.columbia.edu/contact/) instead.

## <a name="start"></a> Getting Started

* Make sure you have a [GitHub account](https://github.com/signup/free)
* Submit a ticket for your issue, assuming one does not already exist.
  * Clearly describe the issue including steps to reproduce when it is a bug.
  * Make sure you fill in the earliest version that you know has the issue.
* Fork the repository into your account on GitHub

## <a name="rules"></a> Coding Rules
To ensure consistency throughout the source code, please keep these rules in mind as you are working:

* All features or bug fixes **must be tested** by one or more unit tests.
* We follow the conventions contained in:
     * Python's [PEP8 Style Guide](https://www.python.org/dev/peps/pep-0008/) (enforced by [flake8](https://pypi.python.org/pypi/flake8))
     * Javscript's [ESLint](http://eslint.org/) errors and warnings.
* The master branch is continuously integrated by [Travis-CI](https://travis-ci.org/ccnmtl/footprints), and all tests must pass before merging.

## <a name="changes"></a>Making Changes

* Create a topic branch from where you want to base your work.
  * To quickly create a topic branch based on master; `git checkout -b
    fix/master/my_contribution master`. Please do not work directly on the
    `master` branch.
* Create your patch, **including appropriate test cases**.
* Make commits of logical units.
* Run `make` to make sure the code passes all validation, flake8, jshint and unit tests
* Make sure your commit messages are in the proper format.

## <a name="submit"></a>Submitting Changes

* Push your changes to a topic branch in your fork of the repository.
* Submit a pull request to the repository in the ccnmtl organization.
* The core team reviews Pull Requests on a regular basis, and will provide feedback

## <a name="info"></a> Further Information
For more information, see:
* [Footprint's Web Site](https://footprints.ctl.columbia.edu)
* [Footprints Wiki](https://github.com/ccnmtl/footprints/wiki)
